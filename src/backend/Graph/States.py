from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class ActionInstruction(BaseModel):
    """单个动作的指令模型"""

    action: str = Field(description="动作类型：search/schedule/document/todo")
    instruction: str = Field(description="该动作的具体执行指令")


class PlanDecision(BaseModel):
    """计划决策模型，定义用户请求的处理顺序"""

    actions: List[ActionInstruction] = Field(
        description="处理用户请求的动作序列，包含每个动作的具体指令",
        min_length=1,
        max_length=4,
    )


class State(TypedDict):
    data: str
    data_type: str
    user_message: str
    decision: str
    output: str
    supplementary_info: str
    messages: Annotated[list[BaseMessage], add_messages]
    plan_decision: Optional[PlanDecision]
    current_action: Optional[str]
    current_instruction: Optional[str]
    action_sequence: Optional[List[Dict[str, Any]]]
