"""检索相关节点。

- SQL 工具节点：基于 SQLDatabase + langgraph ToolNode（最新位置在 langgraph.prebuilt）
- RAG 工具节点：基于 FAISS 向量库 + create_retriever_tool（最新路径在 langchain.tools.retriever）
- FAISS 索引采用懒加载，避免索引文件不存在时启动直接报错。
"""

import os
import re
from typing import Literal

from langchain.tools.retriever import create_retriever_tool
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from llms import fastllm, llm
from prompts import Retriever_prompt
from States import State


def get_db_path(destination: str) -> str:
    """获取用户文档下 FlowCalendar 目录中的数据/索引文件路径。"""
    docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
    app_dir = os.path.join(docs_dir, "FlowCalendar")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, destination)


# ---------------------------------------------------------------------------
# SQL 工具
# ---------------------------------------------------------------------------

db = SQLDatabase.from_uri(
    database_uri=f"sqlite:///{get_db_path('flowcalendar.db')}",
    max_string_length=10000,
)

DENY_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|ALTER|DROP|CREATE|REPLACE|TRUNCATE)\b", re.I
)
HAS_LIMIT_TAIL_RE = re.compile(r"(?is)\blimit\b\s+\d+(\s*,\s*\d+)?\s*;?\s*$")


def _safe_sql(query: str) -> str:
    """对 SQL 进行只读安全校验并附加 LIMIT。"""
    q = query.strip()
    if q.count(";") > 1 or (q.endswith(";") and ";" in q[:-1]):
        return "Error: multiple statements are not allowed."
    q = q.rstrip(";").strip()

    if not q.lower().startswith("select"):
        return "Error: only SELECT statements are allowed."
    if DENY_RE.search(q):
        return "Error: DML/DDL detected. Only read-only queries are permitted."

    if not HAS_LIMIT_TAIL_RE.search(q):
        q += " LIMIT 25"
    return q


@tool
def execute_sql(query: str) -> str:
    """Execute a READ-ONLY SQLite SELECT query and return results."""
    safe = _safe_sql(query)
    if safe.startswith("Error:"):
        return safe
    try:
        return db.run(safe)
    except Exception as exc:  # noqa: BLE001 - 直接回传给 LLM 让其修复
        return f"Error: {exc}"


_sql_tools = [execute_sql]
_sql_model_with_tools = fastllm.bind_tools(_sql_tools)
execute_sql_node = ToolNode(_sql_tools)


def sql_retriever(state: State) -> dict:
    """触发 LLM ReAct，让模型决定继续调用 execute_sql 还是给出答案。

    第一次进入时注入 SystemMessage + HumanMessage；后续循环（工具调用-观察-再思考）
    复用累积消息即可，避免重复注入污染上下文。
    """
    history = list(state.get("messages", []))
    has_system = any(isinstance(m, SystemMessage) for m in history)
    if not has_system:
        messages = [
            SystemMessage(content=Retriever_prompt),
            HumanMessage(content=state["user_message"]),
        ] + history
    else:
        messages = history
    ai_msg: AIMessage = _sql_model_with_tools.invoke(messages)
    return {"messages": [ai_msg]}


def retrieve_again_or_forward(state: State) -> Literal["tools", "refine_output_from_retriever"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return "refine_output_from_retriever"


# ---------------------------------------------------------------------------
# RAG 工具（懒加载，避免索引不存在时启动失败）
# ---------------------------------------------------------------------------

_DASHSCOPE_API_KEY = os.getenv(
    "DASHSCOPE_API_KEY", "sk-17ac2b2ecf484caba72a55292d658feb"
)

_embed = DashScopeEmbeddings(
    model="text-embedding-v1", dashscope_api_key=_DASHSCOPE_API_KEY
)

_retriever_tool = None
_rag_tool_node: ToolNode | None = None


def _ensure_retriever_tool():
    """首次使用时再加载 FAISS 索引。"""
    global _retriever_tool, _rag_tool_node
    if _retriever_tool is not None:
        return _retriever_tool
    index_path = get_db_path("faiss_index")
    vector_store = FAISS.load_local(
        folder_path=index_path,
        embeddings=_embed,
        allow_dangerous_deserialization=True,
    )
    _retriever_tool = create_retriever_tool(
        vector_store.as_retriever(search_kwargs={"k": 3}),
        name="retrieve_user_private_database",
        description="Search and return information about the user's private database.",
    )
    _rag_tool_node = ToolNode([_retriever_tool])
    return _retriever_tool


class _LazyToolNode:
    """对外暴露 ToolNode 接口，在首次调用时再实例化真正的 ToolNode。"""

    def __call__(self, state):  # langgraph 会以可调用方式触发节点
        _ensure_retriever_tool()
        return _rag_tool_node.invoke(state)

    def invoke(self, state, config=None):
        _ensure_retriever_tool()
        return _rag_tool_node.invoke(state, config=config)


rag_retriever_tool_node = _LazyToolNode()


def rag_retriever(state: State) -> dict:
    """让模型决定是否调用 RAG 工具，否则直接回答。"""
    retriever_tool = _ensure_retriever_tool()
    messages = state.get("messages") or [HumanMessage(content=state["user_message"])]
    response = fastllm.bind_tools([retriever_tool]).invoke(messages)
    return {"messages": [response]}


# ---------------------------------------------------------------------------
# 文档相关性评估 / 重写问题 / 终答
# ---------------------------------------------------------------------------

GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question.\n"
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant.\n"
    "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
)


class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


grader_model = fastllm


def grade_documents(state: State) -> Literal["generate_answer", "rewrite_question"]:
    """判断检索到的文档是否与用户问题相关。失败时默认走生成答案，避免死循环。"""
    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)
    try:
        response = grader_model.with_structured_output(GradeDocuments).invoke(
            [HumanMessage(content=prompt)]
        )
        score = (response.binary_score if response else "yes").strip().lower()
    except Exception as exc:  # noqa: BLE001
        print(f"[grade_documents] 评分失败，默认 yes: {exc}")
        score = "yes"
    return "generate_answer" if score == "yes" else "rewrite_question"


REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Here is the initial question:\n ------- \n{question}\n ------- \n"
    "Formulate an improved question:"
)


def rewrite_question(state: State) -> dict:
    """改写用户原始问题以提高检索质量。"""
    question = state["messages"][0].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = fastllm.invoke([HumanMessage(content=prompt)])
    return {"messages": [HumanMessage(content=response.content)]}


GENERATE_PROMPT = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer, just say that you don't know. "
    "If the input contains time, add 8 hours to the time before outputting. Do not output the original time. "
    "If the Context is already an answer, just output the answer.\n"
    "Answer in Chinese.\n"
    "Question: {question} \n"
    "Context: {context}"
)


def generate_answer(state: State) -> dict:
    """根据 retriever / sql 工具返回的上下文生成最终回复。"""
    question = state["user_message"]
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"output": response.content, "messages": [response]}

