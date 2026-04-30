from flask import request, jsonify, stream_with_context, Response
from Graph import calendar_agent_flow
from langgraph.types import Command  # 导入Command类
import json
import tempfile
import os
import base64
import atexit

# 全局变量用于跟踪当前活动的流式响应
current_stream_thread = None
stop_stream_flag = False
# 全局变量用于存储临时文件路径
TEMP_FILES = []

# 注册程序退出时的清理函数
def cleanup_temp_files():
    for file_path in TEMP_FILES:
        if os.path.exists(file_path):
            os.unlink(file_path)

# 注册清理函数
atexit.register(cleanup_temp_files)

def handle_message(message):
    """处理消息并返回流式响应"""
    global current_stream_thread, stop_stream_flag
    
    def generate():
        global stop_stream_flag
        stop_stream_flag = False
        has_interrupt = False
        try:
            # 根据是否是resume操作选择不同的输入
            if message.get("is_resume"):  # 修改默认值为False
                # 使用Command对象恢复中断
                input_data = Command(resume=message.get("message", ""))
            else:
                # 普通消息处理
                input_data = {"user_message": message.get("message", ""), "data": message.get("data", ""),"data_type":message.get("data_type", "text")}
            
            # 使用 calendar_agent_flow 处理消息
            for mode, chunk in calendar_agent_flow.stream(
                input_data,
                stream_mode=["messages", "custom"],
                config={"configurable": {"thread_id": message.get("thread_id", "default")}}
                ):
                if stop_stream_flag:
                    break
                if mode == "messages":
                    response,matedata = chunk
                    if response.content and matedata["langgraph_node"] == "general":
                        yield json.dumps({
                                "type": "text",
                                "message": response.content,
                                "thread_id": message.get("thread_id", "default"),
                                "is_resume": False,
                            }) + "\n"
                    if response.content and matedata["langgraph_node"] == "generate_answer":
                        yield json.dumps({
                                "type": "text",
                                "message": response.content,
                                "thread_id": message.get("thread_id", "default"),
                                "is_resume": False,
                            }) + "\n"
                    if "tags" in matedata and matedata["tags"] == ["router"]:
                        yield json.dumps({
                                "type": "progress",
                                "message": "思考需求中...",
                                "thread_id": message.get("thread_id", "default")
                            }) + "\n"
                    if response.content and matedata["langgraph_node"] == "check_data_complete":
                        if "Continue" in response.content:
                            continue
                        else:
                            yield json.dumps({
                                "type": "text",
                                "is_resume": True,
                                "message": response.content,
                                "thread_id": message.get("thread_id", "default")
                            }) + "\n"
                else:
                    if "new_event" in chunk:
                        yield json.dumps({"type": "new_event",
                                          "is_resume": False,
                                          "data": chunk["new_event"], 
                                          "thread_id": message.get("thread_id", "default")})
    
            # 如果没有中断，发送完成信号
            if not has_interrupt:
                yield json.dumps({
                    "message": None,
                    "thread_id": message.get("thread_id", "default")
                }) + "\n"
                
        except Exception as e:
            if not stop_stream_flag:
                # 发送错误信息
                yield json.dumps({
                    "type": "error",
                    "data": str(e),
                    "thread_id": message.get("thread_id", "default")
                }) + "\n"
    
    return generate()

def create_app(app):
    """注册路由到Flask应用"""
    @app.route('/api/chat', methods=['POST'])
    def chat():
        global current_stream_thread, TEMP_FILES
        data = request.json
        print(data)
        # 确保data是一个字典
        if not isinstance(data, dict):
            return jsonify({'error': '请求数据格式不正确'}), 400
        
        if not data.get("thread_id"):
            return jsonify({'error': 'thread_id 不能为空'}), 401
        
        message_type = data.get('data_type', 'text')
        tmp_file_path = None  # 初始化临时文件路径变量
        if message_type == 'text':
            pass
        elif message_type == 'image':
            file_data = data.get('data')
            if file_data:
                # 将文件数据转换为 base64 编码
                # 注意：这里假设前端已经正确发送了文件数据
                # 在实际应用中，可能需要更复杂的处理来提取文件内容
                if isinstance(file_data, list):
                    # 如果是int列表，先转换为byte数组
                    byte_data = bytes(file_data)
                    base64_image = base64.b64encode(byte_data).decode('utf-8')
                elif isinstance(file_data, str):
                    # 如果是base64字符串，直接使用
                    base64_image = file_data
                else:
                    # 其他情况，尝试转换为base64
                    byte_data = bytes(file_data)
                    base64_image = base64.b64encode(byte_data).decode('utf-8')
                
                # 创建临时文件以供视觉模型处理
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(base64.b64decode(base64_image))
                    tmp_file_path = tmp_file.name
                
                # 将临时文件路径添加到全局数组中
                TEMP_FILES.append(tmp_file_path)
                
                try:
                    data['data'] = tmp_file_path
                except Exception as e:
                    # 如果发生异常，确保删除临时文件
                    if tmp_file_path and os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
                        TEMP_FILES.remove(tmp_file_path)
                    raise e
        elif message_type == 'table':
            file_data = data.get('data')
            file_name = data.get('file_name')
            if file_data and file_name:
                # 处理接收到的文件数据
                if isinstance(file_data, str):
                    # 如果是字符串，需要解码
                    file_bytes = file_data.encode('latin1')  # 使用latin1编码解码字符串
                elif isinstance(file_data, (list, bytes)):
                    # 如果是字节数组或列表，直接转换为bytes
                    file_bytes = bytes(file_data)
                else:
                    # 其他情况，尝试直接写入
                    file_bytes = file_data

                # 创建临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.' + file_name.split('.')[-1]) as tmp_file:
                    tmp_file.write(file_bytes)
                    tmp_file_path = tmp_file.name
                
                data['data'] = tmp_file_path
                
                # 将临时文件路径添加到全局数组中
                TEMP_FILES.append(tmp_file_path)
        # 调用大模型处理消息
        response = Response(
            stream_with_context(handle_message(data)), 
            mimetype='application/json'
        )

        return response

if __name__ == '__main__':
    input_data = {"user_message": "明天下午五点开会,六点结束", "data": "", "data_type": "text"}
    #input_data = {"user_message": "你好啊", "data": "", "data_type": "text"}
    for mode, chunk in calendar_agent_flow.stream(
        input_data,
        stream_mode=["messages", "custom"],
        config={"configurable": {"thread_id": "s"}}
        ):
        output = ""
        if mode == "messages":
            response,matedata = chunk
            if response.content and matedata["langgraph_node"] == "general":
                print(response.content)
            if "tags" in matedata and matedata["tags"] == ["router"]:
                print("router:"+response.content)
            if response.content and matedata["langgraph_node"] == "check_data_complete":
                print(response.content)
        else:
            if "new_event" in chunk:
                print(chunk["new_event"])