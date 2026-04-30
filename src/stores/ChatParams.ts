import { defineStore } from "pinia";
import { ref } from "vue";
import { ScheduleStore } from "./Calendar/ScheduleStore";
import { ChatStore } from "./chat";
import { io, Socket } from "socket.io-client";
export const ChatParams = defineStore("ChatParams", () => {
    // 共享状态
    const pendingImageCount = ref(0);
    const currentSessionId = ref<string>();
    const useScheduleStore = ScheduleStore();
    const isChatBoxVisible = ref(false);
    const messages = ref<Message[]>([]);
    const processMessage = ref<string>();
    const seenEvents = ref<string[]>([]);
    const inputMessage = ref("");

    const isLoading = ref(false);
    const disableInput = ref(false);
    const error = ref<string | null>(null);

    const socket = ref<Socket | null>(null);
    const isConnected = ref(false);

    // 初始化 WebSocket
    const initSocket = async () => {
        socket.value = io("ws://localhost:5000", {
            reconnection: true,
            reconnectionAttempts: 3
        });

        // 事件监听
        socket.value.on("connect", () => {
            isConnected.value = true;
            currentSessionId.value = socket.value?.id; 
        });

        socket.value.on("disconnect", () => {
            isConnected.value = false;
        });

        socket.value.on("message", (data: { content: string }) => {
            messages.value.push({
                content: data.content,
                sender: 'ai',
                timestamp: new Date(),
                type: 'text'
            });
        });

        socket.value.on("middle_state", (data: { content: string }) => {
            console.log(data.content);
            processMessage.value = data.content;
        });
        socket.value.on("finish_signal", (data: { content: string }) => {
            console.log(data.content);
            processMessage.value = "";
            seenEvents.value = [];
            messages.value.push({
                content: data.content,
                sender: 'ai',
                timestamp: new Date(),
                type: 'text'
            });
            disableInput.value = false;
        });

        socket.value.on("event_created", (data: { event: any }) => {
            useScheduleStore.addEventFromAi(data.event);
            seenEvents.value.push(data.event.title);
            
            // 替换messages的最后一条消息为seenEvents中的所有事件
            if (messages.value.length > 0) {
                messages.value[messages.value.length - 1] = {
                    content: `已创建事件: ${seenEvents.value.join(',')}`,
                    sender: 'ai',
                    timestamp: new Date(),
                    type: 'text'
                };
            }
        });

        socket.value.on("error", (err: { message: string }) => {
            error.value = `连接错误: ${err.message}`;
        });
    };



    const toggleChatBox = () => {
        isChatBoxVisible.value = !isChatBoxVisible.value;
        useScheduleStore.isShowEventForm = false;
        const useChatStore = ChatStore();
        if (isChatBoxVisible.value) {
            if(useChatStore.messages.length === 0) {
                useChatStore.messages.push({
                    id: Date.now().toString(),
                    content: '您好！我是您的日程助手，有什么可以帮您？',
                    sender: 'ai',
                    timestamp: new Date(),
                    type: 'text',
                    completed: true
                });
            }
        } else {
            socket.value?.disconnect();
            messages.value = [];
        }
    };

    const sendMessage = async () => {
        if (!inputMessage.value.trim()) return;
        disableInput.value = true;
        // 添加用户消息
        messages.value.push({
            content: inputMessage.value,
            sender: 'user',
            timestamp: new Date(),
            type: 'text'
        });

        try {
            isLoading.value = true;

            if (pendingImageCount.value > 0) {
                // 构造带上下文的特殊消息
                const contextMessage = {
                    type: 'img_context',
                    message: inputMessage.value,
                    count: pendingImageCount.value, // 携带当前计数
                    session_id: currentSessionId.value
                };

                // 发送组合消息
                socket.value?.emit('message', contextMessage);
                messages.value.push({
                    content: "收到！",
                    sender: 'ai',
                    timestamp: new Date(),
                    type: 'text'
                });
                if (pendingImageCount.value > 0) {
                    pendingImageCount.value--;
                }
                console.log('发送组合消息:', contextMessage);
            } else {
                initSocket();
                while (currentSessionId.value === undefined) { // 等待 currentSessionId 被赋值
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
                socket.value?.emit('message', {
                    type: 'text',
                    message: inputMessage.value,
                    session_id: currentSessionId.value
                })
                messages.value.push({
                    content: '解析中...',
                    sender: 'ai',
                    timestamp: new Date(),
                    type: 'text'
                });
                console.log('发送文本消息:', inputMessage.value,currentSessionId.value);
            };
        } catch (err) {
            error.value = '消息发送失败';
        } finally {
            isLoading.value = false;
            inputMessage.value = "";
        }
    };


    const addImageMessage = async (file: File, pendingMessage: string) => {
        disableInput.value = true;
        messages.value.push({
            content: inputMessage.value || '发送了图片消息',
            sender: 'user',
            timestamp: new Date(),
            type: 'text'
        });
        // 添加加载提示
        await initSocket();
        while (currentSessionId.value === undefined) { // 等待 currentSessionId 被赋值
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        messages.value.push({
            content: '解析中...',
            sender: 'ai',
            timestamp: new Date(),
            type: 'text'
        });

        try {
            console.log('发送图片消息:', currentSessionId.value);
            
            // 将文件转换为 ArrayBuffer
            const arrayBuffer = await file.arrayBuffer();
            // 通过 WebSocket 发送文件数据
            socket.value?.emit('message', {
                type: 'img',
                file: arrayBuffer,  // 发送文件的二进制数据
                session_id: currentSessionId.value,
                pendingMessage: pendingMessage
            });

            pendingImageCount.value++; // 增加计数
        } catch (err) {
            error.value = '图片发送失败';
            console.error('Image Send Error:', err);
        }
    };

    const addSpreadsheetMessage = async (file: File, pendingMessage: string) => {
        // 添加加载提示
        disableInput.value = true;
        messages.value.push({
            content: inputMessage.value || '发送了表格文件',
            sender: 'user',
            timestamp: new Date(),
            type: 'text'
        });
        await initSocket();
        while (currentSessionId.value === undefined) { // 等待 currentSessionId 被赋值
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        messages.value.push({
            content: '解析中...',
            sender: 'ai',
            timestamp: new Date(),
            type: 'text'
        });

        try {
            console.log('发送表格文件消息:', currentSessionId.value);
            
            // 将文件转换为 ArrayBuffer
            const arrayBuffer = await file.arrayBuffer();
            console.log(arrayBuffer);

            // 通过 WebSocket 发送文件数据
            socket.value?.emit('message', {
                type: 'spreadsheet',
                file: arrayBuffer,  // 发送文件的二进制数据
                fileName: file.name, // 发送文件名
                session_id: currentSessionId.value,
                pendingMessage: pendingMessage
            });

            pendingImageCount.value++; // 增加计数
        } catch (err) {
            error.value = '表格文件发送失败';
            console.error('Spreadsheet Send Error:', err);
        }
    };



    return {
        pendingImageCount,
        isChatBoxVisible,
        messages,
        inputMessage,
        isLoading,
        error,
        processMessage,
        disableInput,
        addImageMessage,
        addSpreadsheetMessage, // 添加表格文件处理函数
        toggleChatBox,
        sendMessage,
        isConnected
    };
});

interface Message {
    content: string;
    sender: 'user' | 'ai';
    timestamp: Date;
    type: 'text' | 'image' | 'spreadsheet';
}