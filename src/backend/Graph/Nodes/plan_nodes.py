from typing import Literal
from pydantic import BaseModel, Field
from States import State
from llms import fastllm

# 定义计划决策提示词 - 深度思考模式
PLAN_PROMPT = """
你是一个智能日程计划助手。你的任务是深度分析用户的请求，确定处理这个请求的最佳执行顺序，并为每个动作生成具体的执行指令。

可用的动作类型：
1. "search" - 搜索相关信息
   - 需要生成搜索指令：明确搜索内容、搜索范围（网络、数据库、本地文件等）
   - 示例："在网络上查询明天的天气情况"、"在SQL数据库中查找用户订单信息"

2. "schedule" - 安排日程
   - 需要生成日程安排指令：明确标题、时间、重复规则、参与人等
   - 示例："安排明天上午10点的团队会议，标题为'项目进度讨论'，不重复"

3. "document" - 文档处理
   - 需要生成文档处理指令：明确文档类型、内容要点、格式要求等
   - 示例："创建项目需求文档，包含功能列表和技术架构"

4. "todo" - 待办事项
   - 需要生成待办事项指令：明确任务内容、优先级、截止时间等
   - 示例："添加明天需要完成的任务：代码review，优先级高"

用户请求：{user_request}

请深度分析这个请求，按执行顺序输出最合适的动作序列，并为每个动作生成具体的执行指令。
"""

class ActionInstruction(BaseModel):
    """单个动作的指令模型"""
    action: str = Field(description="动作类型：search/schedule/document/todo")
    instruction: str = Field(description="该动作的具体执行指令")

class PlanDecision(BaseModel):
    """计划决策模型 - 深度思考模式"""
    actions: list[ActionInstruction] = Field(
        description="处理用户请求的动作序列，包含每个动作的具体指令",
        min_length=1,
        max_length=4
    )

def plan_decision_node(state: State) -> dict:
    """
    第一个节点：接收用户请求，深度分析并输出处理顺序及具体指令
    
    参数:
        state: 包含用户请求的状态
        
    返回:
        dict: 包含plan_decision的状态更新
    """
    user_request = state["user_message"]
    
    # 使用LLM深度分析用户请求并生成计划决策
    prompt = PLAN_PROMPT.format(user_request=user_request)
    
    try:
        # 使用结构化输出确保返回正确的格式
        response = fastllm.with_structured_output(PlanDecision).invoke([
            {"role": "system", "content": "你是一个专业的日程计划分析助手。请深度思考用户需求，为每个动作生成具体明确的执行指令。"},
            {"role": "user", "content": prompt}
        ])
        
        # 验证动作类型并提取动作序列
        valid_actions = {"search", "schedule", "document", "todo"}
        validated_actions = []
        action_sequence = []
        
        for action_instruction in response.actions:
            action_type = action_instruction.action
            instruction = action_instruction.instruction
            
            # 验证动作类型
            if action_type in valid_actions:
                validated_actions.append(action_type)
                action_sequence.append({
                    "action": action_type,
                    "instruction": instruction
                })
            else:
                # 如果遇到无效动作，使用默认的search动作
                validated_actions.append("search")
                action_sequence.append({
                    "action": "search",
                    "instruction": f"搜索与'{user_request}'相关的信息"
                })
        
        # 确保至少有一个动作
        if not validated_actions:
            validated_actions = ["search"]
            action_sequence = [{
                "action": "search",
                "instruction": f"搜索与'{user_request}'相关的信息"
            }]
        
        # 创建计划决策
        plan_decision = PlanDecision(actions=response.actions)
        
        # 设置当前动作和指令
        current_action = validated_actions[0] if validated_actions else "search"
        current_instruction = action_sequence[0]["instruction"] if action_sequence else ""
        
        return {
            "plan_decision": plan_decision,
            "current_action": current_action,
            "current_instruction": current_instruction,
            "action_sequence": action_sequence
        }
        
    except Exception as e:
        print(f"LLM调用失败: {e}")
        # 如果LLM调用失败，使用基于关键词的简单逻辑
        user_request_lower = user_request.lower()
        action_sequence = []
        
        # 基于关键词判断需要哪些动作
        if any(word in user_request_lower for word in ["查找", "搜索", "查询", "找", "search"]):
            action_sequence.append({
                "action": "search",
                "instruction": f"搜索与'{user_request}'相关的信息"
            })
        if any(word in user_request_lower for word in ["安排", "日程", "会议", "时间", "schedule"]):
            action_sequence.append({
                "action": "schedule",
                "instruction": f"安排与'{user_request}'相关的日程"
            })
        if any(word in user_request_lower for word in ["文档", "文件", "创建", "编辑", "document"]):
            action_sequence.append({
                "action": "document",
                "instruction": f"处理与'{user_request}'相关的文档"
            })
        if any(word in user_request_lower for word in ["任务", "待办", "提醒", "todo"]):
            action_sequence.append({
                "action": "todo",
                "instruction": f"管理与'{user_request}'相关的待办事项"
            })
        
        # 如果没有任何匹配，使用默认动作
        if not action_sequence:
            action_sequence = [{
                "action": "search",
                "instruction": f"搜索与'{user_request}'相关的信息"
            }]
        
        # 创建计划决策
        plan_decision = PlanDecision(actions=[
            ActionInstruction(action=item["action"], instruction=item["instruction"])
            for item in action_sequence
        ])
        
        current_action = action_sequence[0]["action"] if action_sequence else "search"
        current_instruction = action_sequence[0]["instruction"] if action_sequence else ""
        
        return {
            "plan_decision": plan_decision,
            "current_action": current_action,
            "current_instruction": current_instruction,
            "action_sequence": action_sequence
        }

def update_current_action_and_instruction(state: State) -> dict:
    """
    更新当前动作和指令：删除已完成的动作，设置下一个动作和指令
    
    参数:
        state: 当前状态
        
    返回:
        dict: 更新后的状态
    """
    if not state.get("action_sequence") or not state.get("current_action"):
        return {"current_action": None, "current_instruction": None}
    
    current_action = state["current_action"]
    action_sequence = state["action_sequence"].copy()  # 创建副本避免修改原始数据
    
    # 找到当前动作在序列中的位置
    try:
        # 从action_sequence中提取动作类型列表
        action_types = [item["action"] for item in action_sequence]
        current_index = action_types.index(current_action)
        
        # 删除已完成的动作
        del action_sequence[current_index]
        
        # 如果还有剩余动作，设置下一个动作和指令
        if action_sequence:
            next_action = action_sequence[0]["action"]
            next_instruction = action_sequence[0]["instruction"]
            
            # 更新plan_decision中的actions
            updated_actions = [
                ActionInstruction(action=item["action"], instruction=item["instruction"])
                for item in action_sequence
            ]
            
            return {
                "action_sequence": action_sequence,
                "current_action": next_action,
                "current_instruction": next_instruction,
                "plan_decision": PlanDecision(actions=updated_actions)
            }
        else:
            # 所有动作都已完成
            return {
                "action_sequence": [],
                "current_action": None,
                "current_instruction": None,
                "plan_decision": PlanDecision(actions=[])
            }
            
    except (ValueError, IndexError):
        return {"current_action": None, "current_instruction": None}

def route_based_on_plan(state: State) -> Literal["search", "schedule", "document", "todo", "end"]:
    """
    路由函数：根据当前动作决定下一个节点
    
    参数:
        state: 当前状态
        
    返回:
        str: 下一个节点的名称
    """
    if not state.get("plan_decision") or not state.get("current_action"):
        return "end"
    
    current_action = state["current_action"]
    action_sequence = state.get("action_sequence", [])
    
    # 找到当前动作在序列中的位置
    try:
        # 从action_sequence中提取动作类型列表
        action_types = [item["action"] for item in action_sequence]
        current_index = action_types.index(current_action)
        
        # 如果是最后一个动作，结束流程
        if current_index == len(action_sequence) - 1:
            return "end"
        
        # 返回下一个动作
        next_action = action_sequence[current_index + 1]["action"]
        return next_action
        
    except (ValueError, IndexError):
        return "end"
    
def route_based_on_plan(state: State) -> Literal["search", "schedule", "document", "todo", "end"]:
    """
    路由函数：根据当前动作决定下一个节点
    
    参数:
        state: 当前状态
        
    返回:
        str: 下一个节点的名称
    """
    if not state.get("plan_decision") or not state.get("current_action"):
        return "end"
    
    current_action = state["current_action"]
    plan_actions = state["plan_decision"].actions
    
    # 找到当前动作在序列中的位置
    try:
        current_index = plan_actions.index(current_action)
        
        # 如果是最后一个动作，结束流程
        if current_index == len(plan_actions) - 1:
            return "end"
        
        # 返回下一个动作
        next_action = plan_actions[current_index + 1]
        return next_action
        
    except (ValueError, IndexError):
        return "end"
    


# 定义具体的动作节点函数
def search_node(state: State) -> dict:
    """搜索节点 - 使用具体的搜索指令"""
    current_instruction = state.get("current_instruction", "")
    print(f"执行搜索动作 - 指令: {current_instruction}")
    
    # 模拟搜索功能执行
    result = {
        "output": f"搜索功能已执行: {current_instruction}",
        "data": f"搜索结果: 根据指令'{current_instruction}'找到的相关信息"
    }
    
    # 更新当前动作和指令
    result.update(update_current_action_and_instruction(state))
    return result

def schedule_node(state: State) -> dict:
    """日程安排节点 - 使用具体的日程指令"""
    current_instruction = state.get("current_instruction", "")
    print(f"执行日程安排动作 - 指令: {current_instruction}")
    
    # 模拟日程安排功能执行
    result = {
        "output": f"日程安排功能已执行: {current_instruction}",
        "data": f"日程安排结果: 根据指令'{current_instruction}'创建的日程"
    }
    
    # 更新当前动作和指令
    result.update(update_current_action_and_instruction(state))
    return result

def document_node(state: State) -> dict:
    """文档处理节点 - 使用具体的文档指令"""
    current_instruction = state.get("current_instruction", "")
    print(f"执行文档处理动作 - 指令: {current_instruction}")
    
    # 模拟文档处理功能执行
    result = {
        "output": f"文档处理功能已执行: {current_instruction}",
        "data": f"文档处理结果: 根据指令'{current_instruction}'创建的文档"
    }
    
    # 更新当前动作和指令
    result.update(update_current_action_and_instruction(state))
    return result

def todo_node(state: State) -> dict:
    """待办事项节点 - 使用具体的待办指令"""
    current_instruction = state.get("current_instruction", "")
    print(f"执行待办事项动作 - 指令: {current_instruction}")
    
    # 模拟待办事项功能执行
    result = {
        "output": f"待办事项功能已执行: {current_instruction}",
        "data": f"待办事项结果: 根据指令'{current_instruction}'添加的任务"
    }
    
    # 更新当前动作和指令
    result.update(update_current_action_and_instruction(state))
    return result

from langgraph.graph import StateGraph, END
from States import State
from Nodes.plan_nodes import plan_decision_node, route_based_on_plan
from Nodes.retreiver_nodes import sql_retriever, rag_retriever
from llms import fastllm

def create_plan_agent():
    """
    创建计划代理工作流
    """
    # 创建工作流图
    workflow = StateGraph(State)
    
    # 添加第一个节点：计划决策
    workflow.add_node("plan_decision", plan_decision_node)
    
    # 添加其他动作节点（使用具体的指令）
    workflow.add_node("search", search_node)
    workflow.add_node("schedule", schedule_node)
    workflow.add_node("document", document_node)
    workflow.add_node("todo", todo_node)
    
    # 设置入口点
    workflow.set_entry_point("plan_decision")
    
    # 从计划决策节点到第一个动作节点的条件边
    workflow.add_conditional_edges(
        "plan_decision",
        route_based_on_plan,
        {
            "search": "search",
            "schedule": "schedule", 
            "document": "document",
            "todo": "todo",
            "end": END
        }
    )
    
    # 为每个动作节点添加条件边，实现顺序执行
    for action in ["search", "schedule", "document", "todo"]:
        workflow.add_conditional_edges(
            action,
            route_based_on_plan,
            {
                "search": "search",
                "schedule": "schedule",
                "document": "document", 
                "todo": "todo",
                "end": END
            }
        )
    
    return workflow.compile()

# 创建代理实例
plan_agent = create_plan_agent()

def test_plan_agent():
    """测试计划代理功能 - 深度思考模式"""
    
    # 测试用例
    test_cases = [
        "帮我查找明天的会议安排",  # 应该输出 ["search", "schedule"]
        "我需要创建一个项目文档并安排相关会议",  # 应该输出 ["document", "schedule"]
        "提醒我明天要完成的任务",  # 应该输出 ["todo"]
        "搜索相关资料并创建学习计划"  # 应该输出 ["search", "document", "schedule"]
    ]
    
    for i, user_request in enumerate(test_cases, 1):
        print(f"\n=== 测试用例 {i} ===")
        print(f"用户请求: {user_request}")
        
        # 初始化状态
        initial_state = State(
            user_message=user_request,
            messages=[],
            data="",
            data_type="",
            decision="", 
            output="",
            supplementary_info="",
            plan_decision=None,
            current_action=None,
            current_instruction=None,
            action_sequence=None
        )
        
        # 执行代理
        try:
            result = plan_agent.invoke(initial_state)
            plan_decision = result.get("plan_decision")
            
            if plan_decision:
                print(f"✓ 计划决策:")
                for i, action_instruction in enumerate(plan_decision.actions, 1):
                    print(f"  {i}. {action_instruction.action}: {action_instruction.instruction}")
                
                print(f"✓ 当前动作: {result.get('current_action')}")
                print(f"✓ 当前指令: {result.get('current_instruction', '无')}")
                print(f"✓ 输出: {result.get('output', '无输出')}")
                print(f"✓ 数据: {result.get('data', '无数据')}")
            else:
                print("✗ 未生成计划决策")
                
        except Exception as e:
            print(f"✗ 执行错误: {e}")

if __name__ == "__main__":
    test_plan_agent()