<template>
  <transition name="chat-box-float" appear>
    <div class="chat-box" v-if="useChatParams.isChatBoxVisible" @mousedown="startInteraction"
      @mousemove="handleMouseMove" @mouseleave="handleMouseLeave" :class="{
          'dragging': isDragging || isResizing,
          'resize-top-left': isResizing && resizeDirection === 'top-left',
          'resize-top-right': isResizing && resizeDirection === 'top-right',
          'resize-bottom-left': isResizing && resizeDirection === 'bottom-left',
          'resize-bottom-right': isResizing && resizeDirection === 'bottom-right',
          'resize-top': isResizing && resizeDirection === 'top',
          'resize-bottom': isResizing && resizeDirection === 'bottom',
          'resize-left': isResizing && resizeDirection === 'left',
          'resize-right': isResizing && resizeDirection === 'right'
        }" :style="{ bottom: position.y + 'px', right: position.x + 'px' }">
      <div class="chat-panel" :style="{ width: size.width + 'px', height: size.height + 'px' }">
        <!-- 图标容器 -->
        <div class="icon-container">
          <button class="icon-button">
            <div class="stopOutput" v-if="useChatParams.disableInput" @click="stopOutput"></div>
            <Trash2 v-else color="#999999" :size="18" @click="useChatStore.clearMessages()" />
          </button>
          <button class="icon-button" @click="useChatParams.isChatBoxVisible = false">
            <XIcon color="#999999" :size="20" />
          </button>
        </div>

        <div class="dialog-box" ref="scrollContainer" @dragover.prevent="onDragOver" @dragleave="onDragLeave" @drop.prevent="onDrop"
          :class="{ 'drag-over': dragOver }">
          <transition-group name="message-fade" appear>
            <div v-for="(msg, index) in useChatStore.messages" :key="index + msg.timestamp.getTime()"
              :class="['message', msg.sender]">
              <div class="bubble">
                <div class="profolio" v-if="msg.sender === 'ai'">
                  <Bot color="#999999" :size="20" />
                </div>
                <div class="message-content">
                  <div 
                    v-if="msg.completed || msg.sender === 'user'" 
                    class="markdown-content"
                    v-html="renderedMarkdown(msg.content)"
                  >
                  </div>
                  <div 
                    v-else 
                    class="markdown-content"
                  >
                    <span v-html="renderedMarkdown(msg.content)"></span>
                    <span class="cursor-blink">|</span>
                  </div>
                </div>
                <div class="profolio" v-if="msg.sender === 'user'">
                  <User color="#999999" :size="20" />
                </div>
              </div>
              <div class="sub-info">
                <div class="timestamp">{{ formatTime(msg.timestamp) }}</div>
                <div class="copy-button" v-if="msg.sender === 'ai'" @click="copyMessage(msg.content)">
                  <Copy color="#999999" :size="14" />
                </div>
                <div class="progress-info" v-if="msg.sender === 'ai' && !msg.completed">{{ useChatStore.progressInfo }}</div>
                <div
                  v-if="useChatParams.processMessage && index === useChatParams.messages.length - 1"
                  class="process-message">
                  {{ useChatParams.processMessage }}
                </div>
              </div>
            </div>
          </transition-group>
          <!-- 文件图标容器 -->

        </div>
        <div class="input-container">
          <div class="file-icons" v-if="pendingFiles.length > 0">
            <div v-for="( _ , index) in pendingFiles" :key="index" class="file-icon" @click="removePendingFile(index)">
              <PaperclipIcon color="#999999" :size="18" />
            </div>
          </div>
          <input v-if="useChatParams.isChatBoxVisible" ref="inputRef" v-model="useChatStore.inputMessage" @keyup.enter="handleEnter"
            @keydown.delete="handleDelete" @paste="handlePaste" :placeholder="useChatParams.disableInput ? '请等待输出完成' : '请输入...'" class="text-input" :disabled="useChatParams.disableInput" />
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ChatParams } from '../stores/ChatParams';
import { ChatStore } from '../stores/chat';
import { ref, onMounted, computed, nextTick } from 'vue';
import { Trash2 , XIcon, PaperclipIcon, Bot, User, Copy } from 'lucide-vue-next';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';
import 'highlight.js/styles/github-dark.css';

const useChatParams = ChatParams();
const useChatStore = ChatStore();
const inputRef = ref<HTMLInputElement | null>(null);

// 存储待发送的文件
const pendingFiles = ref<{file: File, message: string}[]>([]);

// 拖拽相关变量
const position = ref({ x: 100, y: 60 });
const isDragging = ref(false);
let initialMousePosition = { x: 0, y: 0 }; // 记录初始鼠标位置

// Resize相关变量
const size = ref({ width: 350, height: 500 });
const isResizing = ref(false);
const resizeDirection = ref('');
const resizeStart = ref({ x: 0, y: 0 });
const originalSize = ref({ width: 0, height: 0 });
const originalPosition = ref({ x: 0, y: 0 });

// 最小尺寸限制
const MIN_WIDTH = 200;
const MIN_HEIGHT = 300;

// 处理鼠标移动事件，用于在悬停时改变光标样式
const handleMouseMove = (e: MouseEvent) => {
  const rect = (e.target as HTMLElement).closest('.chat-box')?.getBoundingClientRect();
  if (!rect) return;
  
  const offsetX = e.clientX - rect.left;
  const offsetY = e.clientY - rect.top;
  
  // 检查是否在调整大小的边缘区域
  const edgeSize = 15;
  
  // 左上角
  if (offsetX <= edgeSize && offsetY <= edgeSize) {
    setCursor('nw-resize');
    return;
  }
  
  // 右上角
  if (offsetX >= rect.width - edgeSize && offsetY <= edgeSize) {
    setCursor('ne-resize');
    return;
  }
  
  // 左下角
  if (offsetX <= edgeSize && offsetY >= rect.height - edgeSize) {
    setCursor('sw-resize');
    return;
  }
  
  // 右下角
  if (offsetX >= rect.width - edgeSize && offsetY >= rect.height - edgeSize) {
    setCursor('se-resize');
    return;
  }
  
  
  // 下边
  if (offsetY >= rect.height - edgeSize && offsetX > edgeSize && offsetX < rect.width - edgeSize) {
    setCursor('n-resize');
    return;
  }
  
  // 左边
  if (offsetX <= edgeSize && offsetY > edgeSize && offsetY < rect.height - edgeSize) {
    setCursor('e-resize');
    return;
  }
  
  // 右边
  if (offsetX >= rect.width - edgeSize && offsetY > edgeSize && offsetY < rect.height - edgeSize) {
    setCursor('w-resize');
    return;
  }
  
  // 检查是否在顶部拖拽区域（排除边缘）
  if (offsetY <= 20 && offsetX > 15 && offsetX < rect.width - 15) {
    setCursor('move');
    return;
  }
  
  // 恢复默认光标
  setCursor('default');
};

// 处理鼠标离开事件，恢复默认光标
const handleMouseLeave = () => {
  setCursor('default');
};

// 开始交互（拖拽或调整大小）
const startInteraction = (e: MouseEvent) => {
  const rect = (e.target as HTMLElement).closest('.chat-box')?.getBoundingClientRect();
  if (!rect) return;
  
  const offsetX = e.clientX - rect.left;
  const offsetY = e.clientY - rect.top;
  
  // 检查是否在顶部拖拽区域（排除角落）
  if (offsetY <= 15 && offsetX > 15 && offsetX < rect.width - 15) {
    startDrag(e);
    return;
  }
  
  // 检查是否在调整大小的边缘区域
  const edgeSize = 15;
  
  // 左上角
  if (offsetX <= edgeSize && offsetY <= edgeSize) {
    startResize('bottom-right', e);
    return;
  }
  
  // 右上角
  if (offsetX >= rect.width - edgeSize && offsetY <= edgeSize) {
    startResize('bottom-left', e);
    return;
  }
  
  // 左下角
  if (offsetX <= edgeSize && offsetY >= rect.height - edgeSize) {
    startResize('top-right', e);
    return;
  }
  
  // 右下角
  if (offsetX >= rect.width - edgeSize && offsetY >= rect.height - edgeSize) {
    startResize('top-left', e);
    return;
  }
  
  // 上边
  if (offsetY <= edgeSize && offsetX > edgeSize && offsetX < rect.width - edgeSize) {
    startResize('bottom', e);
    return;
  }
  
  // 下边
  if (offsetY >= rect.height - edgeSize && offsetX > edgeSize && offsetX < rect.width - edgeSize) {
    startResize('top', e);
    return;
  }
  
  // 左边
  if (offsetX <= edgeSize && offsetY > edgeSize && offsetY < rect.height - edgeSize) {
    startResize('right', e);
    return;
  }
  
  // 右边
  if (offsetX >= rect.width - edgeSize && offsetY > edgeSize && offsetY < rect.height - edgeSize) {
    startResize('left', e);
    return;
  }

};

// 新增光标控制逻辑
const setCursor = (cursorType: string) => {
  const container = document.querySelector('.chat-box') as HTMLElement;
  container.style.cursor = cursorType;
};

// 修改后的开始拖拽
const startDrag = (e: MouseEvent) => {
  setCursor('move');
  isDragging.value = true;
  
  // 记录初始位置
  initialMousePosition = { x: e.clientX, y: e.clientY };
  
  // 禁用文本选择
  document.body.style.userSelect = 'none';
  
  document.addEventListener('mousemove', onDrag);
  document.addEventListener('mouseup', stopDrag);
};

// 拖拽中（修正方向逻辑）
const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return;
  
  // 计算鼠标移动差值（直接使用差值确保方向正确）
  const deltaX = e.clientX - initialMousePosition.x;
  const deltaY = e.clientY - initialMousePosition.y;
  
  position.value = {
    x: position.value.x - deltaX,
    y: position.value.y - deltaY
  };
  
  // 更新初始位置为当前位置
  initialMousePosition = { x: e.clientX, y: e.clientY };
};

// 停止拖拽
const stopDrag = () => {
  isDragging.value = false;
  
  // 恢复文本选择
  document.body.style.userSelect = '';
  
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);

  // 不再在这里设置光标样式，由 handleMouseMove 处理
};

// 开始调整大小
const startResize = (direction: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top' | 'bottom' | 'left' | 'right', e: MouseEvent) => {
  const cursorMap = {
    'top-left': 'nw-resize',
    'top-right': 'ne-resize',
    'bottom-left': 'sw-resize',
    'bottom-right': 'se-resize',
    'top': 'n-resize',
    'bottom': 's-resize',
    'left': 'w-resize',
    'right': 'e-resize'
  };
  setCursor(cursorMap[direction] || 'default');
  
  e.stopPropagation();
  isResizing.value = true;
  resizeDirection.value = direction;
  document.body.classList.add('resizing');

  resizeStart.value = { x: e.clientX, y: e.clientY };
  originalSize.value = { ...size.value };
  originalPosition.value = { ...position.value };

  document.body.style.userSelect = 'none';
  document.addEventListener('mousemove', onResize);
  document.addEventListener('mouseup', stopResize);
};

// 停止调整大小
const stopResize = () => {
  const container = document.querySelector('.chat-box') as HTMLElement;
  container.style.cursor = '';
  isResizing.value = false;
  resizeDirection.value = '';
  document.body.classList.remove('resizing');

  document.body.style.userSelect = '';
  document.removeEventListener('mousemove', onResize);
  document.removeEventListener('mouseup', stopResize);
};

// 调整大小中（修正各角落逻辑）
const onResize = (e: MouseEvent) => {
  if (!isResizing.value) return;

  const deltaX = e.clientX - resizeStart.value.x;
  const deltaY = e.clientY - resizeStart.value.y;

  let newWidth = originalSize.value.width;
  let newHeight = originalSize.value.height;
  let newX = originalPosition.value.x;
  let newY = originalPosition.value.y;

  switch (resizeDirection.value) {
    case 'top-left':
      // 向左拖动：宽度增加，向右拖动：宽度减少
      newWidth = Math.max(MIN_WIDTH, originalSize.value.width + deltaX);
      newHeight = Math.max(MIN_HEIGHT, originalSize.value.height + deltaY);
      newX = originalPosition.value.x - deltaX; // 向右移动
      newY = originalPosition.value.y - deltaY; // 向下移动
      break;
    case 'top-right':
      newWidth = Math.max(MIN_WIDTH, originalSize.value.width - deltaX);
      newHeight = Math.max(MIN_HEIGHT, originalSize.value.height + deltaY);
      newY = originalPosition.value.y - deltaY; // 向下移动
      break;
    case 'bottom-left':
      // 向左拖动：面板向左扩大，向右拖动：面板缩小
      newWidth = Math.max(MIN_WIDTH, originalSize.value.width + deltaX);
      newHeight = Math.max(MIN_HEIGHT, originalSize.value.height - deltaY);
      newX = originalPosition.value.x - deltaX; // 向右移动
      break;
    case 'bottom-right':
      newWidth = Math.max(MIN_WIDTH, originalSize.value.width - deltaX);
      newHeight = Math.max(MIN_HEIGHT, originalSize.value.height - deltaY);
      break;
    case 'top':
      newHeight = Math.max(MIN_HEIGHT, originalSize.value.height + deltaY);
      newY = originalPosition.value.y - deltaY; // 向下移动
      break;
    case 'bottom':
      newHeight = Math.max(MIN_HEIGHT, originalSize.value.height - deltaY);
      break;
    case 'left':
      newWidth = Math.max(MIN_WIDTH, originalSize.value.width + deltaX);
      newX = originalPosition.value.x - deltaX; // 向右移动
      break;
    case 'right':
      newWidth = Math.max(MIN_WIDTH, originalSize.value.width - deltaX);
      break;
  }

  // 边界限制（保持不变）
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;
  
  if (newX < 0) {
    newWidth += newX;
    newX = 0;
  }
  if (newY < 0) {
    newHeight += newY;
    newY = 0;
  }
  if (newX + newWidth > windowWidth) {
    newWidth = windowWidth - newX;
  }
  if (newY + newHeight > windowHeight) {
    newHeight = windowHeight - newY;
  }

  // 确保最小尺寸
  newWidth = Math.max(MIN_WIDTH, newWidth);
  newHeight = Math.max(MIN_HEIGHT, newHeight);

  size.value = { width: newWidth, height: newHeight };
  position.value = { x: newX, y: newY };
};

const handlePaste = async (event: ClipboardEvent) => {
  const clipboardItems = event.clipboardData?.items;
  if (useChatParams.disableInput) return;
  if (!clipboardItems) return;

  for (const item of clipboardItems) {
    if (item.kind === 'file') {
      const file = item.getAsFile();
      if (file) {
        // 检查文件类型是否为图片或表格
        const isImage = item.type.indexOf('image') !== -1;
        const isSpreadsheet = file.name.match(/\.(csv|xls|xlsx|json)$/i);
        
        if (isImage || isSpreadsheet) {
          event.preventDefault();
          // 添加文件到待发送列表
          pendingFiles.value.push({ file, message: '' });
          return;
        }
      }
    }
  }
};

const dragOver = ref(false);

const onDragOver = () => {
  dragOver.value = true;
};

const onDragLeave = () => {
  dragOver.value = false;
};

const onDrop = async (e: DragEvent) => {
  if (useChatParams.disableInput) return;
  if (inputRef.value) {
    inputRef.value.focus();
  }
  dragOver.value = false;
  const dt = e.dataTransfer;
  if (dt?.items) {
    for (const item of dt.items) {
      if (item.kind === 'file') {
        const file = item.getAsFile();
        if (file) {
          // 检查文件类型是否为图片或表格
          const isImage = item.type.indexOf('image') !== -1;
          const isSpreadsheet = file.name.match(/\.(csv|xls|xlsx|json)$/i);
          
          if (isImage || isSpreadsheet) {
            // 添加文件到待发送列表
            pendingFiles.value.push({ file, message: '' });
          }
        }
      }
    }
  }
};

const scrollContainer = ref<HTMLElement | null>(null);

// 滚动到底部
const scrollToBottom = async () => {
  // 等待DOM更新后滚动到底部
  await nextTick();
  if (scrollContainer.value) {
    // 方法一：使用 scrollTo (推荐，支持动画)
    scrollContainer.value.scrollTo({
      top: scrollContainer.value.scrollHeight, // 滚动到容器的总高度
      behavior: 'smooth' // 平滑滚动，可选 'auto' 或 'smooth'
    });
  }
};

// 处理回车键
const handleEnter = async () => {
  if (pendingFiles.value.length > 0) {
    // 发送所有待处理的文件
    pendingFiles.value.forEach(({ file }) => {
      // 检查文件类型
      const isImage = file.type.indexOf('image') !== -1;
      const isSpreadsheet = file.name.match(/\.(csv|xls|xlsx|json)$/i);
      
      if (isImage) {
        useChatStore.addImageMessage(file, useChatStore.inputMessage);
      } else if (isSpreadsheet) {
        useChatStore.addTableMessage(file, useChatStore.inputMessage);
      }
    });
    // 清空待发送列表
    pendingFiles.value = [];
    useChatStore.inputMessage = '';
  } else {
    // 发送普通文本消息
    useChatStore.send();
  }

  // 滚动到底部
  scrollToBottom();
};

// 处理删除键
const handleDelete = () => {
  // 仅当输入框内容为空时，按下删除键才执行移除最后一个待发送文件
  if (useChatStore.inputMessage === '' && pendingFiles.value.length > 0) {
    removePendingFile(pendingFiles.value.length - 1);
  }
};

// 移除待发送的文件
const removePendingFile = (index: number) => {
  pendingFiles.value.splice(index, 1);
};

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};
import DOMPurify from 'dompurify';
// 复制的是原始的Markdown文本（msg.content），而不是渲染后的HTML
const copyMessage = async (content: string) => {
  try {
    // 将 Markdown 转换为 HTML
    const htmlContent = renderMarkdown(content);
    
    // 使用 DOMPurify 进行安全过滤（防止 XSS）
    const cleanHtml = DOMPurify.sanitize(htmlContent, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'b', 'i', 'u', 'code', 'pre', 'span', 
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote',
                    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'a'],
      ALLOWED_ATTR: ['href', 'target', 'rel', 'class']
    });

    // 创建包含 HTML 和纯文本的 ClipboardItem
    const clipboardItem = new ClipboardItem({
      'text/html': new Blob([cleanHtml], { type: 'text/html' }),
      'text/plain': new Blob([content], { type: 'text/plain' }) // 备用纯文本版本
    });

    // 写入剪贴板
    await navigator.clipboard.write([clipboardItem]);
    
    console.log('已复制带格式的HTML内容');
  } catch (err) {
    console.error('复制失败:', err);
    // 降级方案：如果 Clipboard API 不支持，回退到纯文本复制
    try {
      await navigator.clipboard.writeText(content);
      // 显示纯文本复制成功的提示
    } catch (fallbackErr) {
      console.error('纯文本复制也失败:', fallbackErr);
      // 显示错误提示
    }
  }
};

const stopOutput = async () => {
  if (useChatParams.disableInput) {
    // 尝试中断ChatStore的流式响应
    try {
      await useChatStore.stopOutput();
      useChatStore.messages[useChatStore.messages.length - 1].content += '用户中断输出';
    } catch (error) {
      console.error('中断ChatStore响应失败:', error);
    }
    
    // 重置ChatParams的状态
    useChatParams.disableInput = false;
    useChatParams.processMessage = '';
  }
};
// 调整大小中
onMounted(() => {
  if (inputRef.value) {
    inputRef.value.focus();
  }
});

// Markdown 渲染相关
const renderMarkdown = (content: string): string => {
  if (!content) return '';
  
  marked.setOptions({
    highlight: function(code: string, lang: string) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext';
      return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-',
    async: false // 关键：设置为同步模式
  } as any);

  // 现在 marked.parse 会同步返回 string
  return marked.parse(content) as string;
};

// 计算属性：渲染后的 Markdown 内容
const renderedMarkdown = computed(() => (content: string) => renderMarkdown(content));

</script>

<style scoped>

.progress-info{
  color: #787878;
  padding-left: 8px;
  transform: translateY(1px);
  font-size: 12px;
  font-weight: 400;
}
.input-slide-enter-active {
  transition: all 0.5s 
}


.input-slide-enter-from,
.input-slide-leave-to {
  transform: translateX(120px);
  opacity: 0;
}

/* chat-box 上浮渐变动画 */
.chat-box-float-enter-active {
  transition: all 0.4s ease;
}

.chat-box-float-enter-from {
  transform: translateY(16px);
}

.chat-box {
  position: fixed;
  z-index: 9999999;
}

.chat-panel {
  display: flex;
  flex-direction: column;
  border-radius: 15px;
  overflow: hidden;
  background: rgba(212, 212, 212, 0.066);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(10px); 
  transform: translateZ(0);
  will-change: transform, backdrop-filter;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: inset 1px 1px 6px rgba(255, 255, 255, 0.3),
              0px 0px 5px rgba(113, 113, 113, 0.5);
  position: relative;
}

.stopOutput{
  width: 13px;
  height: 13px;
  border-radius: 4px;
  border: 2px solid #dd1c1c;
}
/* 拖拽时禁用文本选择 */
.chat-box.dragging {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* 拖拽区域的鼠标样式 */
.chat-box:not(.dragging):not(.resize-top-left):not(.resize-top-right):not(.resize-bottom-left):not(.resize-bottom-right) .chat-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 15px;
  pointer-events: none;
}

/* 调整大小时的鼠标样式 */
.chat-box {
  cursor: default;
}

/* 八个方向的调整大小鼠标样式 */
.chat-box.resize-top-left,
.chat-box.resize-top-left .chat-panel {
  cursor: nw-resize; /* 左上-右下双向箭头 */
}

.chat-box.resize-top-right,
.chat-box.resize-top-right .chat-panel {
  cursor: ne-resize; /* 右上-左下双向箭头 */
}

.chat-box.resize-bottom-left,
.chat-box.resize-bottom-left .chat-panel {
  cursor: sw-resize; /* 左下-右上双向箭头 */
}

.chat-box.resize-bottom-right,
.chat-box.resize-bottom-right .chat-panel {
  cursor: se-resize; /* 右下-左上双向箭头 */
}

.chat-box.resize-top,
.chat-box.resize-top .chat-panel {
  cursor: n-resize; /* 上下双向箭头 */
}

.chat-box.resize-bottom,
.chat-box.resize-bottom .chat-panel {
  cursor: s-resize; /* 上下双向箭头 */
}

.chat-box.resize-left,
.chat-box.resize-left .chat-panel {
  cursor: w-resize; /* 左右双向箭头 */
}

.chat-box.resize-right,
.chat-box.resize-right .chat-panel {
  cursor: e-resize; /* 左右双向箭头 */
}

.icon-container {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 4px;
  z-index: 1001;
}

.icon-button {
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dialog-box {
  margin-top: 32px;
  flex: 1;
  overflow-y: auto;
  transition: background-color 0.3s ease;
}

.dialog-box.drag-over {
  border-color: rgba(0, 0, 0, 0.05);
  background-color: rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(5px);
}

.message {
  margin: 12px 0;
  display: flex;
  flex-direction: column;
}

.message.user {
  align-items: flex-end;
}

.message.ai {
  align-items: flex-start;
  display: flex;
}

.bubble {
  max-width: 80%;
  padding:0px 4px 0px 4px;
  border-radius: 12px;
  margin: 4px 0;
  font-size: 13px;
  display: flex;
}

.profolio {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  margin-right: 8px;
  margin-left: 8px;
}
.sub-info {
  display: flex;
  align-items: baseline;
  width: 100%;
  transform: translateY(-5px);
  padding: 0px 44px;
}

.copy-button {
  margin-left: 10px;
  transform: translateY(3px);
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.copy-button:hover {
  opacity: 1;
}

.message.user .sub-info {
  justify-content: flex-end;
}

.message.ai .sub-info {
  justify-content: flex-start;
}

.timestamp {
  display: flex;
  font-size: 12px;
  padding: 1px 0px;
  text-align: start;
  color: #9c9c9c;
}

.process-message {
  color: #999;
  font-size: 12px;
  padding: 0px 12px;
  width: 100%;
  text-align: left;
  align-items: center;
  justify-content: center;
}

/* 闪烁光标样式 */
.cursor-blink {
  animation: blink 1s infinite;
  font-weight: normal;
  display: inline-block;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0; }
  100% { opacity: 1; }
}

/* 明暗主题下的光标颜色 */
[data-theme="dark"] .cursor-blink {
  color: #ffffff;
}

[data-theme="light"] .cursor-blink {
  color: #000000;
}

/* 消息内容容器样式 */
.message-content {
  display: flex;
  align-items: center;
}

.markdown-content {
  display: flex;
}

.input-container {
  display: flex;
  align-items: center;
  padding: 10px;
}

.text-input {
  flex: 1;
  padding: 8px 12px;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  outline: none;
  color: black;
  font-size: 14px;
  backdrop-filter: blur(4px);
  border-radius: 20px;
  margin: 0 5px;
  box-shadow: inset 2px 2px 15px rgba(255, 255, 255, 0.74),
              0px 0px 5px rgba(113, 113, 113, 0.3);
  min-height: 24px;
  display: flex;
  align-items: center;
}

.text-input::placeholder {
  color: rgba(94, 94, 94, 0.7);
}

.process-message {
  color: #999;
  font-size: 12px;
  padding: 0px 12px;
  width: 100%;
  text-align: left;
  align-items: center;
  justify-content: center;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  flex-shrink: 0;
}

[data-theme="dark"] .text-input {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}
[data-theme="dark"] .text-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

/* 闪烁光标样式 */
.cursor-blink {
  animation: blink 1s infinite;
  font-weight: normal;
  display: inline-block;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0; }
  100% { opacity: 1; }
}

/* 明暗主题下的光标颜色 */
[data-theme="dark"] .cursor-blink {
  color: #ffffff;
}

[data-theme="light"] .cursor-blink {
  color: #000000;
}

/* 消息内容容器样式 */
.message-content {
  display: flex;
  align-items: center;
}

.markdown-content {
  display: inline-block;
  line-height: 1.5;
  width: 100%;
}

.markdown-content :deep(p) {
  margin: 0 0 10px 0;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin: 15px 0 10px 0;
  font-weight: 600;
}

.markdown-content :deep(h1) {
  font-size: 1.5em;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 5px;
}

.markdown-content :deep(h2) {
  font-size: 1.3em;
}

.markdown-content :deep(h3) {
  font-size: 1.1em;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 10px 0;
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 5px 0;
}

.markdown-content :deep(strong) {
  font-weight: 600;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(code) {
  background-color: #f0f0f0;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: -apple-system;
}

[data-theme="dark"] .markdown-content :deep(code) {
  font-family: monospace;
  background-color: #444;
}

.markdown-content :deep(pre) {
  font-family: 'Consolas', 'Courier New', monospace;
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}

.markdown-content :deep(pre code) {
  font-family: 'Consolas', 'Courier New', monospace;
  background-color: transparent;
  padding: 3px;
}

.markdown-content :deep(code) {
  font-family: 'Consolas', 'Courier New', monospace;
  background-color: rgba(0, 0, 0, 0.04);
  padding: 2px 4px;
  border-radius: 3px;
}

[data-theme="dark"] .markdown-content :deep(pre) {
  display: flex;
  font-family: 'Consolas', 'Courier New', monospace;
  background-color: #444;
}

[data-theme="dark"] .markdown-content :deep(code) {
  font-family: 'Consolas', 'Courier New', monospace;
  background-color: rgba(255, 255, 255, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
}

[data-theme="dark"] .markdown-content :deep(pre code) {
  font-family: 'Consolas', 'Courier New', monospace;
  background-color: transparent;
  padding: 3px;
}

.markdown-content :deep(blockquote) {
  border-left: 3px solid #4f46e5;
  margin: 10px 0;
  padding-left: 15px;
  color: #666;
}

[data-theme="dark"] .markdown-content :deep(blockquote) {
  color: #aaa;
}

.markdown-content :deep(a) {
  color: #4f46e5;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

[data-theme="dark"] .markdown-content :deep(a) {
  color: #818cf8;
}
</style>