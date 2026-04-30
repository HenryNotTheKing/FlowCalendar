import axios from 'axios';
import { ScheduleStore } from "../stores/Calendar/ScheduleStore";
// 设置axios基础配置


const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api', // Flask后端地址
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

let resume = false;

interface ChatMessage {
  message: string;
  data: number[] | null;
  data_type: string;
  file_name: string;
  thread_id: string;
  is_resume: boolean;
}

interface SendMessageOptions extends ChatMessage {
  onProgress?: (progress: string) => void;
}
/**
 * 发送消息到后端AI助手
 * @param message 用户输入的消息
 * @returns 一个异步迭代器，用于接收流式响应
 */
export async function* sendMessage(message: SendMessageOptions): AsyncGenerator<string, void, unknown> {
  try {
    console.log('发送消息:', resume);
    const useScheduleStore = ScheduleStore();
    // 使用Fetch API处理流式响应
    const response = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({...message, is_resume: resume}),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('ReadableStream not supported in this browser.');
    }

    // 处理流式响应
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      // 解码数据块
      const chunk = decoder.decode(value, { stream: true });
      
      // 按行分割数据块，因为后端发送的是带换行符的JSON字符串
      const lines = chunk.split('\n').filter(line => line.trim() !== '');
      
      for (const line of lines) {
        try {
          // 解析JSON数据
          const data = JSON.parse(line);
          console.log('Received data:', data);
          // 根据数据类型处理
          if (data.type === 'error') {
            yield "抱歉，出错了，请重启软件后重新尝试。" + String(data.data)
            throw new Error(data.data);
          }
          if (data.type === 'progress') {
            // 调用进度回调函数
            if (message.onProgress && data.message !== undefined && data.message !== null) {
              message.onProgress(data.message);
            }
            continue;
          }
          if (data.type === 'text') {
            if (data.message !== undefined && data.message !== null) {
              yield data.message;
            }
          }
          if (data.type === 'new_event') {
            useScheduleStore.addEventFromAi(data.data);
            yield `<p> 已添加新事件:${data.data.title} </p>`;
          }
          if(data.is_resume){
            resume = data.is_resume;
          }else if(data.is_resume === false){
            resume = false;
          }
          console.log(data);
          // yield 消息内容
          
        } catch (parseError) {
          // 如果解析失败，可能是不完整的数据，跳过
          console.warn('Failed to parse JSON:', line);
        }
      }
    }
  } catch (error) {
    console.error('发送消息时出错:', error);
    throw new Error('网络错误或服务器无响应');
  }
}

/**
 * 中断当前正在进行的流式响应
 * @returns 中断结果
 */
export async function stopStreamResponse(): Promise<boolean> {
  try {
    const response = await apiClient.post('/stop', {});
    resume = false;
    return response.data.success;
  } catch (error) {
    console.error('中断流式响应时出错:', error);
    return false;
  }
}