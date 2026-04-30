import { defineStore } from "pinia";
import { ref } from "vue";
import { sendMessage, stopStreamResponse } from '../service/chatAPI';
import { ChatParams } from './ChatParams';
export const ChatStore = defineStore("chat", () => {
  // 状态定义
  const useChatParams = ChatParams();
  const progressInfo = ref<string | null>(null);
  const messages = ref<Array<{
    id: string;
    content: string;
    sender: 'user' | 'ai';
    timestamp: Date;
    type: 'text';
    completed: boolean;
  }>>([]);
  
  const inputMessage = ref("");
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const abortController = ref<AbortController | null>(null);
  const thread_id = ref(crypto.randomUUID());
  // 添加消息到聊天记录
  const addMessage = (content: string, sender: 'user' | 'ai') => {
    messages.value.push({
      id: Date.now().toString(),
      content,
      sender,
      timestamp: new Date(),
      type: 'text',
      completed: sender === 'user' // 用户消息默认完成，AI消息默认未完成
    });
  };
  
  // 发送消息
  const send = async () => {
    if (!inputMessage.value.trim() || isLoading.value) return;
    useChatParams.disableInput = true;
    const userMessage = inputMessage.value.trim();
    
    // 添加用户消息
    addMessage(userMessage, 'user');
    inputMessage.value = "";
    
    try {
      isLoading.value = true;
      error.value = null;
      
      // 添加AI回复占位符
      const aiMessageIndex = messages.value.length;
      addMessage('', 'ai');
      // 创建新的AbortController
      abortController.value = new AbortController();

      // 使用流式响应
      let accumulatedResponse = '';
      try {
        for await (const chunk of sendMessage({
          message: userMessage,
          data: null,
          file_name: '',
          data_type: 'text',
          thread_id: thread_id.value,
          is_resume: false,
          onProgress: (progress) => {
            progressInfo.value = progress;
          }
        })) {
          // 检查是否被中断
          if (abortController.value?.signal.aborted) {
            break;
          }
          accumulatedResponse += chunk;
          // 更新AI消息内容
          messages.value[aiMessageIndex].content = accumulatedResponse;
        }
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          console.log('流式响应被用户中断');
        } else {
          throw err;
        }
      }
      
      // 流式响应完成后，标记AI消息为已完成
      messages.value[aiMessageIndex].completed = true;
      useChatParams.disableInput = false;
      abortController.value = null;
      // 清空进度信息
      progressInfo.value = null;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '发送消息时发生未知错误';
      // 更新最后一条AI消息为错误信息
      if (messages.value.length > 0 && messages.value[messages.value.length - 1].sender === 'ai') {
        messages.value[messages.value.length - 1].content = '抱歉，我无法回答您的问题。';
        // 即使出错也标记消息为已完成
        messages.value[messages.value.length - 1].completed = true;
        useChatParams.disableInput = false;
      }
      // 清空进度信息
      progressInfo.value = null;
    } finally {
      isLoading.value = false;
    }
  };
  
  // 添加图片消息
  const addImageMessage = async (file: File, message: string) => {
    if (isLoading.value) return;
    useChatParams.disableInput = true;
    
    // 添加用户消息
    addMessage(message || '发送了图片消息', 'user');
    
    try {
      isLoading.value = true;
      error.value = null;
      
      // 添加AI回复占位符
      const aiMessageIndex = messages.value.length;
      addMessage('', 'ai');
      
      // 创建新的AbortController
      abortController.value = new AbortController();
      
      // 将文件转换为 ArrayBuffer
      const arrayBuffer = await file.arrayBuffer();
      console.log('图片文件 ArrayBuffer:', arrayBuffer);
      // 使用流式响应
      let accumulatedResponse = '';
      try {
        for await (const chunk of sendMessage({
          message: message || "提取日程",
          data:  Array.from(new Uint8Array(arrayBuffer)), 
          data_type: 'image',
          file_name: file.name,
          thread_id: thread_id.value,
          is_resume: false,
          onProgress: (progress) => {
            progressInfo.value = progress;
          }
        })) {
          // 检查是否被中断
          if (abortController.value?.signal.aborted) {
            break;
          }
          accumulatedResponse += chunk;
          // 更新AI消息内容
          messages.value[aiMessageIndex].content = accumulatedResponse;
        }
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          console.log('流式响应被用户中断');
        } else {
          throw err;
        }
      }
      
      // 流式响应完成后，标记AI消息为已完成
      messages.value[aiMessageIndex].completed = true;
      useChatParams.disableInput = false;
      abortController.value = null;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '发送图片消息时发生未知错误';
      // 更新最后一条AI消息为错误信息
      if (messages.value.length > 0 && messages.value[messages.value.length - 1].sender === 'ai') {
        messages.value[messages.value.length - 1].content = '抱歉，我无法处理您的图片。';
        // 即使出错也标记消息为已完成
        messages.value[messages.value.length - 1].completed = true;
        useChatParams.disableInput = false;
      }
      // 清空进度信息
      progressInfo.value = null;
    } finally {
      isLoading.value = false;
    }
  };
  
  // 添加表格消息
  const addTableMessage = async (file: File, message: string) => {
    if (isLoading.value) return;
    useChatParams.disableInput = true;
    
    // 添加用户消息
    addMessage(message || '发送了表格文件', 'user');
    
    try {
      isLoading.value = true;
      error.value = null;
      
      // 添加AI回复占位符
      const aiMessageIndex = messages.value.length;
      addMessage('', 'ai');
      
      // 创建新的AbortController
      abortController.value = new AbortController();
      
      // 将文件转换为 ArrayBuffer
      const arrayBuffer = await file.arrayBuffer();
      
      // 使用流式响应
      let accumulatedResponse = '';
      try {
        for await (const chunk of sendMessage({
          message: message || "提取日程",
          data: Array.from(new Uint8Array(arrayBuffer)), // 将 ArrayBuffer 转换为数组
          data_type: 'table',
          file_name: file.name,
          thread_id: thread_id.value,
          is_resume: false,
          onProgress: (progress) => {
            progressInfo.value = progress;
          }
        })) {
          // 检查是否被中断
          if (abortController.value?.signal.aborted) {
            break;
          }
          accumulatedResponse += chunk;
          // 更新AI消息内容
          messages.value[aiMessageIndex].content = accumulatedResponse;
        }
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          console.log('流式响应被用户中断');
        } else {
          throw err;
        }
      }
      
      // 流式响应完成后，标记AI消息为已完成
      messages.value[aiMessageIndex].completed = true;
      useChatParams.disableInput = false;
      abortController.value = null;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '发送表格消息时发生未知错误';
      // 更新最后一条AI消息为错误信息
      if (messages.value.length > 0 && messages.value[messages.value.length - 1].sender === 'ai') {
        messages.value[messages.value.length - 1].content = '抱歉，我无法处理您的表格文件。';
        // 即使出错也标记消息为已完成
        messages.value[messages.value.length - 1].completed = true;
        useChatParams.disableInput = false;
      }
      // 清空进度信息
      progressInfo.value = null;
    } finally {
      isLoading.value = false;
    }
  };
  // 清除聊天记录
  const clearMessages = () => {
    messages.value = [];
    messages.value.push({
                    id: Date.now().toString(),
                    content: '您好！我是您的日程助手，有什么可以帮您？',
                    sender: 'ai',
                    timestamp: new Date(),
                    type: 'text',
                    completed: true
                });
    thread_id.value = crypto.randomUUID();
  };
  
  // 中断当前输出
  const stopOutput = async () => {
    if (isLoading.value && abortController.value) {
      // 中断前端的流式响应
      abortController.value.abort();
      
      // 通知后端停止生成
      try {
        await stopStreamResponse();
      } catch (error) {
        console.error('通知后端停止失败:', error);
      }
      
      // 重置状态
      isLoading.value = false;
      useChatParams.disableInput = false;
      
      // 标记当前AI消息为已完成
      if (messages.value.length > 0 && messages.value[messages.value.length - 1].sender === 'ai') {
        messages.value[messages.value.length - 1].completed = true;
      }
    }
  };
  
  return {
    // 状态
    messages,
    inputMessage,
    isLoading,
    error,
    progressInfo,
    addImageMessage,
    addTableMessage,
    send,
    clearMessages,
    addMessage,
    stopOutput
  };
});