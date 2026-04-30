"""LangGraph 主流程定义。

升级要点：
- 使用 langchain-core 0.3 + langgraph 0.6 的最新 API。
- ``ToolNode`` / ``tools_condition`` 来自 ``langgraph.prebuilt``。
- 路由 / 检索决策统一使用 ``with_structured_output`` 输出 Pydantic 模型，避免 JsonOutputParser 二次拼接。
- 修复历史 bug：``plan_schedules`` 不再把 prompt 字符串当 schema；结构化输出不会再访问 ``.content``。
"""

from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition
from pydantic import BaseModel, Field

import Nodes.extract_nodes as extract_nodes
import Nodes.retreiver_nodes as retreiver_nodes
import prompts
from llms import fastllm, llm, router as router_llm
from States import State


# ---------------------------------------------------------------------------
# 路由 / 检索决策
# ---------------------------------------------------------------------------


class Route(BaseModel):
    step: Literal["extract_schedules", "plan_schedules", "retriever", "general"] = Field(
        description=(
            "必须选择以下四个路径之一：\n"
            "- extract_schedules: 提取图片、表格或文本中的日程信息\n"
            "- plan_schedules: 规划、安排或管理用户日程\n"
            "- retriever: 查询已有日程、待办事项、文档或历史记录\n"
            "- general: 与日程规划、检索无关的一般性问题"
        )
    )


class RetrieveDecision(BaseModel):
    decision: Literal["sql", "rag"] = Field(
        description=(
            "必须选择以下两个路径之一：\n"
            "- sql: 从数据库中检索信息\n"
            "- rag: 从文档中检索信息"
        )
    )


class PlanResult(BaseModel):
    """plan_schedules 节点的结构化输出。"""

    title: str = Field(description="计划标题")
    plan: str = Field(description="详细的计划内容（自然语言）")
    repeat: bool = Field(description="是否为重复事件")
    recurrence: str = Field(default="", description="若 repeat 为 true，描述重复规则")


# ---------------------------------------------------------------------------
# 节点实现
# ---------------------------------------------------------------------------


def plan_schedules(state: State) -> dict:
    """根据用户的规划需求生成结构化计划描述。"""
    structured_llm = fastllm.with_structured_output(PlanResult)
    try:
        response: PlanResult = structured_llm.invoke(
            [
                SystemMessage(content=prompts.plan_prompt),
                HumanMessage(content=state["user_message"]),
            ]
        )
    except Exception as exc:  # noqa: BLE001
        response = None
        print(f"[plan_schedules] 结构化输出失败：{exc}")

    if response is None:
        text = "抱歉，我暂时无法生成计划，请换一种说法再试。"
    elif response.repeat:
        text = (
            f"【{response.title}】\n{response.plan}\n"
            f"重复规则: {response.recurrence or '未指定'}"
        )
    else:
        text = f"【{response.title}】\n{response.plan}\n（不是重复事件）"

    return {"output": text, "messages": [AIMessage(content=text)]}


def retriever(state: State) -> dict:
    """决定走 SQL 检索还是 RAG 检索。"""
    decision_llm = fastllm.with_structured_output(RetrieveDecision)
    history = [
        msg.content
        for msg in state.get("messages", [])
        if isinstance(msg, (HumanMessage, AIMessage))
    ]
    try:
        response: RetrieveDecision = decision_llm.invoke(
            [
                SystemMessage(content=prompts.Retrieve_route_prompt),
                HumanMessage(
                    content=f"{state['user_message']}\n历史对话：{history}"
                ),
            ]
        )
        decision = response.decision if response else "sql"
    except Exception as exc:  # noqa: BLE001
        print(f"[retriever] 决策失败，回退到 sql：{exc}")
        decision = "sql"
    return {"decision": decision}


def sql_or_rag(state: State) -> Literal["sql", "rag"]:
    return "sql" if state["decision"] == "sql" else "rag"


def general(state: State) -> dict:
    """与日程无关的通用对话。"""
    history = [
        msg.content
        for msg in state.get("messages", [])
        if isinstance(msg, (HumanMessage, AIMessage))
    ]
    response = fastllm.invoke(
        [
            SystemMessage(content=f"对话历史：\n{history}\n请结合对话历史回答用户问题。"),
            HumanMessage(content=state["user_message"]),
        ]
    )
    return {"output": response.content, "messages": [response]}


def llm_call_router(state: State) -> dict:
    """根据用户输入将请求路由到合适的子流程。

    使用 JsonOutputParser 而非 ``with_structured_output``——后者在
    ChatTongyi(qwen3-coder-flash) 上经常返回 None。这里同时保留
    ``tags=["router"]``，前端依赖该标签显示"思考需求中..."。
    """
    history = [
        msg.content
        for msg in state.get("messages", [])
        if isinstance(msg, (HumanMessage, AIMessage))
    ]

    parser = JsonOutputParser(pydantic_object=Route)
    system_message = (
        "你是一个智能路由助手，负责将用户输入路由到最合适的处理节点。\n"
        "## 路径选择指南\n"
        "- extract_schedules: 用户提供图片、表格或文本需要从中提取日程\n"
        "- plan_schedules: 用户请求帮忙规划日程，含\"计划/安排/管理\"等关键词\n"
        "- retriever: 用户查询自身已有信息（日程、待办、文档内容等）\n"
        "- general: 与日程规划、检索均无关，或用户问历史对话相关内容\n"
        "## 示例\n"
        "- '明天六点到七点写一份卷子' → extract_schedules\n"
        "- '帮我安排下周的会议' → plan_schedules\n"
        "- '我明天有什么安排' → retriever\n"
        "- '今天天气怎么样' → general\n"
        "## 历史对话（仅供参考）\n{history_messages}\n"
        "严格按照以下 JSON Schema 返回，且只输出 JSON，不要其他文字：\n"
        "{format_instructions}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_message), ("human", "{text}")]
    ).partial(
        format_instructions=parser.get_format_instructions(),
        history_messages=str(history),
    )

    chain = prompt | router_llm | parser

    decision = "general"
    try:
        response = chain.invoke({"text": state["user_message"]})
        if isinstance(response, dict) and response.get("step") in (
            "extract_schedules",
            "plan_schedules",
            "retriever",
            "general",
        ):
            decision = response["step"]
    except Exception as exc:  # noqa: BLE001
        print(f"[llm_call_router] 解析失败，回退到 general：{exc}")

    return {
        "decision": decision,
        "messages": [HumanMessage(content=state["user_message"])],
    }


def route_decision(state: State) -> str:
    return state["decision"]


def check_router(state: State) -> Literal["check_data_complete", "parse_text"]:
    if state["decision"] == "check_again":
        return "check_data_complete"
    return "parse_text"


# ---------------------------------------------------------------------------
# 构建 StateGraph
# ---------------------------------------------------------------------------

flow_builder = StateGraph(State)

flow_builder.add_node("llm_call_router", llm_call_router)

flow_builder.add_node("extract_schedules", extract_nodes.extract_schedules)
flow_builder.add_node("check_data_complete", extract_nodes.check_data_complete)
flow_builder.add_node("ask_or_forward", extract_nodes.ask_or_forward)
flow_builder.add_node("parse_text", extract_nodes.parse_text)

flow_builder.add_node("plan_schedules", plan_schedules)

flow_builder.add_node("retriever", retriever)
flow_builder.add_node("sql_retriever", retreiver_nodes.sql_retriever)
flow_builder.add_node("execute_sql_node", retreiver_nodes.execute_sql_node)

flow_builder.add_node("generate_answer", retreiver_nodes.generate_answer)
flow_builder.add_node("rewrite_question", retreiver_nodes.rewrite_question)
flow_builder.add_node("rag_retriever", retreiver_nodes.rag_retriever)
flow_builder.add_node("rag_retriever_tool_node", retreiver_nodes.rag_retriever_tool_node)

flow_builder.add_node("general", general)


# 路由
flow_builder.add_edge(START, "llm_call_router")
flow_builder.add_conditional_edges(
    "llm_call_router",
    route_decision,
    {
        "extract_schedules": "extract_schedules",
        "plan_schedules": "plan_schedules",
        "retriever": "retriever",
        "general": "general",
    },
)

# 提取日程
flow_builder.add_edge("extract_schedules", "check_data_complete")
flow_builder.add_edge("check_data_complete", "ask_or_forward")
flow_builder.add_conditional_edges(
    "ask_or_forward",
    check_router,
    {
        "check_data_complete": "check_data_complete",
        "parse_text": "parse_text",
    },
)
flow_builder.add_edge("parse_text", END)
flow_builder.add_edge("plan_schedules", END)

# 检索：SQL or RAG
flow_builder.add_conditional_edges(
    "retriever",
    sql_or_rag,
    {
        "sql": "sql_retriever",
        "rag": "rag_retriever",
    },
)

flow_builder.add_conditional_edges(
    "rag_retriever",
    tools_condition,
    {
        "tools": "rag_retriever_tool_node",
        END: END,
    },
)
flow_builder.add_conditional_edges(
    "rag_retriever_tool_node",
    retreiver_nodes.grade_documents,
)
flow_builder.add_edge("generate_answer", END)
flow_builder.add_edge("rewrite_question", "rag_retriever")

flow_builder.add_conditional_edges(
    "sql_retriever",
    retreiver_nodes.retrieve_again_or_forward,
    {
        "tools": "execute_sql_node",
        "refine_output_from_retriever": "generate_answer",
    },
)
flow_builder.add_edge("execute_sql_node", "sql_retriever")
flow_builder.add_edge("general", END)

# Checkpointer：保留 InMemorySaver；如需持久化可改为 SqliteSaver。
checkpoint = InMemorySaver()
calendar_agent_flow = flow_builder.compile(checkpointer=checkpoint)

