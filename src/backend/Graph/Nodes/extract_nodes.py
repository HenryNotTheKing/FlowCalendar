"""日程信息抽取相关节点。

继续沿用 LCEL（``prompt | llm | JsonOutputParser``）+ ``.stream()`` 的方式，
这是 langchain-core 0.3 / langgraph 0.6 下对结构化输出做增量流式渲染的标准做法。
``with_structured_output`` 一次性返回 Pydantic 实例，无法满足前端按字段/事件粒度推送。
"""

from datetime import datetime
from typing import Any, Dict

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.config import get_stream_writer
from langgraph.types import interrupt
from markitdown import MarkItDown

import prompts
from llms import fastllm, fast_structured_llm, llm, visionllm
from States import State
from structure import ScheduleList

md = MarkItDown()

def read_csv(file_path: str):
    """读取表格文件，支持csv、xls、xlsx等多种格式，将表格文件转化成json文本"""
    file_extension = file_path.lower().split('.')[-1]
        
    if file_extension == 'csv':
        # 尝试不同的编码方式读取CSV文件
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise ValueError("无法使用任何支持的编码读取CSV文件")
    elif file_extension in ['xls', 'xlsx']:
        df = pd.read_excel(file_path)
    elif file_extension == 'json':
        df = pd.read_json(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {file_extension}")
    
    time_column = df.iloc[:, 0].astype(str)  # 确保转为字符串
    time_with_label = "time{" + time_column + "}"  # 添加标签
    result = {}
    # 鲁棒性处理1: 自动识别并设置第一列为索引
    for col in df.columns[1:]:  # 从第二列开始
    # 将时间标签与列数据拼接为字符串
        combined = time_with_label + " " + df[col].astype(str)
        result[col] = combined.to_dict()

    return result
# Nodes
def extract_schedules(state: State):
    """负责从图片或表格或用户信息中提取日程信息"""
    if state["data_type"] == "image":
        vision_prompt = prompts.vision_prompt
        image_message = {"image": state["data"]}
        text_message = {"text": vision_prompt}
        message = HumanMessage(content=[text_message, image_message])
        vision_response = visionllm.invoke([message])
        text = vision_response.content
        # ChatTongyi 视觉模型返回可能是 str，也可能是 [{"text": "..."}] 列表
        if isinstance(text, list):
            text = "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in text
            )
        return {"data": text or "", "supplementary_info": state["user_message"]}
    
    elif state["data_type"] == "table":
        records = read_csv(state["data"])
        return {"data" : str(records), "supplementary_info": state["user_message"]}
    
    else:
        return {"data": state["user_message"], "supplementary_info": state["user_message"]}

def check_data_complete(state: State) -> str:
    '''check if the data is enougth to parse as ScheduleList'''
    sys_prompt = prompts.check_data_complete_prompt
    response = llm.invoke([
            SystemMessage(
                content=sys_prompt
            ),
            HumanMessage(content="原始数据：\n" + state["supplementary_info"] + "用户补充信息：\n" + state["data"]),
        ])
    return {"decision" : response.content}

def ask_or_forward(state: State):
    '''ask for missing info in the data'''
    if state['decision'] == "Continue":
        return {"data": state["data"] , "supplementary_info" : f"\n{state['supplementary_info']}\n用户补充信息:{state['user_message']}\n", "decision": "parse_text"}
    else:
        supplement_prompt = interrupt(state['decision'])
        refine_prompt = f"""
        总结用户输入和上一轮的问题，生成一句连贯的补充的信息，用明确的命令告诉下一个模型要忽略这个事件还是补充这个事件的信息。注意识别用户意图，看是要忽略这个事件还是补充这个事件的信息。

        注意：
        - 如果用户没有提及月份，请仔细查看输入是否含有月份信息，如果没有默认使用本月。本月是{datetime.now().month}月, 将月份补充到用户信息上进行输出。
        - 如果用户没有提及年份，请仔细查看输入是否含有年份信息，如果没有默认使用本年。本年是{datetime.now().year}年，将年份补充到用户信息上进行输出。
            -**示例** ： 输入是九月八日，则已经包含了月份缺失年份，则补充为{datetime.now().year}年九月八日
        - 用户可能会回答补充信息，也可能会直接说明忽略这个事件，请根据上下文判断，给出合理的回复，以协助其他智能体判断信息是否完整。
        示例句式：
        -   某事件从X时间开始
        -   某事件到X时间结束
        -   某事件在X时间开始到Y时间结束\n
        
        上一轮提出的问题: {state['decision']}
        上一轮用户补充: {supplement_prompt}"""
        refine_info = fastllm.invoke(refine_prompt)
        return {"data":state["data"], "supplementary_info":f"\n上一轮问答结果: \n{refine_info.content}\n原始信息:{state['supplementary_info']}\n", "decision": "check_again"}

def parse_text(state: State):
    def is_event_complete(event_data: Dict[str, Any]) -> bool:
        """检查事件数据是否完整。

        ``exceptions`` / ``recurrence`` 仅在重复事件下才必须出现；
        非重复事件如果模型省略这两个字段，应视为完整。
        """
        always_required = [
            'title', 'category', 'start', 'end',
            'location', 'description', 'repeat', 'allDay',
        ]
        for field in always_required:
            if field not in event_data:
                return f"缺少必填字段: {field}"
        if event_data.get('repeat') is True:
            for field in ('recurrence', 'exceptions'):
                if field not in event_data:
                    return f"缺少必填字段: {field}"
        return True

    # 获取数据库中的类别数据
    def get_categories():
        """获取数据库中的所有类别数据"""
        return ""
    
    # 为每条记录创建系统消息和提示模板
    system_message = f"""你是一个日程信息提取助手。请分析提供的文本内容，根据用户的补充信息，识别出其中的所有日程信息。
                        请务必提取出你能找到的每一个日程条目，并严格按照以下JSON格式返回：
                        {{format_instructions}}
                        
                        注意事项：
                        - 对于标题相同并且时间相差小于或者等于15分钟的事件，合并为同一个事件。
                        - 当 repeat 为 false 时，recurrence 字段应为 null
                        - 当 repeat 为 true 时，recurrence 字段应包含有效的重复规则
                        - 对于1-16周代表从开始日期循环16次，对于8-10周代表从第八周开始一共三次，注意计算开始时间
                        - category字段请优先从以下已有类别中选择，如果没有合适的再自行生成：{get_categories()}
                        - 你已经知道今天的日期是{datetime.now().strftime('%Y-%m-%d')}，仅当用户的信息提到“明天”，“下周三”等需要知道当前日期的关键词时才使用。
                        - 如果用户没有提及月份，请仔细查看输入是否含有月份信息，如果没有默认使用本月。本月是{datetime.now().month}月, 将月份补充到用户信息上进行输出。
                        - 如果用户没有提及年份，请仔细查看输入是否含有年份信息，如果没有默认使用本年。本年是{datetime.now().year}年，将年份补充到用户信息上进行输出。
                        特别注意：
                        - 对于标题相同并且一个事件的结束时间和另一个事件的结束时间相差小于或者等于15分钟的事件，合并为同一个事件。
                            - **示例** ： 某事件从星期一8:00开始到8:45结束，另一事件从星期一8:50开始到9:35结束，这两个事件标题都是操作系统，时间相差5分钟，应该合并为一个事件。
                        """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "相关数据：{text}\n补充的信息：{supplementary_info} ")
    ])
    parser = JsonOutputParser(pydantic_object=ScheduleList)
    format_instructions = parser.get_format_instructions()
    prompt = prompt.partial(format_instructions=format_instructions)
    
    chain = prompt | fast_structured_llm | parser

    writer = get_stream_writer()
    emitted_indices: set[int] = set()
    seen_fields_by_idx: dict[int, set[str]] = {}

    try:
        response = chain.stream(
            {"text": state["data"], "supplementary_info": state["supplementary_info"]}
        )
        for chunk in response:
            schedules = chunk.get("schedules") if isinstance(chunk, dict) else None
            if not schedules:
                continue
            for idx, event in enumerate(schedules):
                if not isinstance(event, dict):
                    continue
                if idx in emitted_indices:
                    # 该事件已发射；后续追加的字段（如 recurrence/exceptions）忽略
                    continue

                # 仅对"当前正在构建"的最后一条事件推送字段进度
                if idx == len(schedules) - 1:
                    current = set(event.keys())
                    seen = seen_fields_by_idx.setdefault(idx, set())
                    new_fields = current - seen
                    if new_fields:
                        writer({"new_field": ", ".join(sorted(new_fields))})
                        seen_fields_by_idx[idx] = current

                if is_event_complete(event) is True:
                    payload = dict(event)  # 浅拷贝，避免污染流式状态
                    payload["id"] = None
                    payload["lastState"] = None
                    payload["originalEventId"] = None
                    if payload.get("repeat") is False:
                        payload["recurrence"] = None
                        payload["exceptions"] = None
                    else:
                        payload.setdefault("exceptions", None)
                    writer({"new_event": payload})
                    emitted_indices.add(idx)
    except Exception as exc:  # noqa: BLE001
        # 解析失败不应让整个对话崩溃；记录后向上抛出 friendly 文本
        print(f"[parse_text] 提取日程失败: {exc}")
        return {"output": f"解析日程时出错：{exc}"}

    return {"output": f"已提取 {len(emitted_indices)} 条日程。"}
