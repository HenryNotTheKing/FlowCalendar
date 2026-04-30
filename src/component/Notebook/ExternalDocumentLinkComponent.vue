<template>
  <node-view-wrapper class="external-document-link-component">
    <div class="external-document-link-content">
      <div class="doc-item-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="doc-item loading">
          <div class="loading-spinner"></div>
          <span class="doc-title">{{ fileName }} (上传中...)</span>
        </div>
        
        <!-- 正常状态 -->
        <div v-else class="doc-item" @click="openDocument" @mouseenter="showDeleteIcon = true" @mouseleave="showDeleteIcon = false">
          <component :is="showDeleteIcon ? X : FileText" :size="16" class="file-icon" @click.stop="deleteDocument" />
          <span class="doc-title">{{ fileName }}</span>
        </div>
      </div>
    </div>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'
import { ref, onMounted } from 'vue'
import { FileText, X } from 'lucide-vue-next'

const props = defineProps(nodeViewProps)

const fileName = ref('')
const showDeleteIcon = ref(false)
const loading = ref(false)

// 获取文件名和加载状态
onMounted(() => {
  fileName.value = props.node.attrs.fileName || '外部文档'
  loading.value = props.node.attrs.loading || false
})

// 监听节点属性变化
import { watch } from 'vue'
watch(() => props.node.attrs.loading, (newLoading) => {
  loading.value = newLoading || false
})

// 打开文档
const openDocument = async () => {
  if (props.node.attrs.filePath) {
    // 使用electron API打开文件
    try {
      if ((window as any).ipcRenderer) {
        await (window as any).ipcRenderer.invoke('open-file', props.node.attrs.filePath);
      } else {
        // 如果ipcRenderer不可用，尝试使用系统默认方式打开
        window.open(`file://${props.node.attrs.filePath}`, '_blank');
      }
    } catch (error) {
      console.error('打开文件失败:', error);
      alert('无法打开文件: ' + (error as Error).message);
    }
  } else if (props.node.attrs.fileUrl) {
    // 在新标签页中打开文件URL
    window.open(props.node.attrs.fileUrl, '_blank');
  } else {
    // 如果Electron API不可用，提示用户
    alert('无法打开文件，缺少文件路径信息');
  }
}

// 删除文档
const deleteDocument = async () => {
  console.log('开始删除外部文档链接...')
  
  try {
    // 首先调用Flask后端API删除转换文档记录
    const axios = (await import('axios')).default
    const convertedDocId = props.node.attrs.id
    
    console.log('删除转换文档记录，ID:', convertedDocId)
    
    const response = await axios.delete(`http://localhost:5000/api/converted_documents/${convertedDocId}`)
    
    if (response.status === 204) {
      console.log('转换文档记录删除成功')
    } else {
      console.warn('转换文档记录删除失败，但继续执行前端删除')
    }
  } catch (error) {
    console.error('调用删除API失败:', error)
    console.warn('继续执行前端删除操作')
  }
  
  // 执行前端删除操作
  setTimeout(() => {
    const { state, dispatch } = props.editor.view
    if (typeof props.getPos === 'function') {
      try {
        const nodePos = props.getPos()
        
        if (nodePos !== undefined && nodePos >= 0) {
          const nodeSize = props.node.nodeSize
          const tr = state.tr.delete(nodePos, nodePos + nodeSize)
          if (dispatch) {
            dispatch(tr)
            console.log('前端删除操作成功')
            return
          } else {
            console.error('无法dispatch事务')
          }
        }
      } catch (error) {
        console.error('getPos()方法错误:', error)
      }
    }
    
    let nodePos = -1
    let nodeSize = 0
    
    // 在文档中查找externalDocumentLink节点
    state.doc.descendants((node, pos) => {
      if (node.type.name === 'externalDocumentLink') {
        console.log('找到externalDocumentLink节点:', { pos, nodeSize: node.nodeSize, attrs: node.attrs })
        
        // 检查这个节点是否与当前组件节点匹配
        if (node.attrs.id === props.node.attrs.id) {
          nodePos = pos
          nodeSize = node.nodeSize
          console.log('匹配的节点位置:', { nodePos, nodeSize })
          return false
        }
      }
      return true
    })
    
    if (nodePos !== -1) {
      console.log('执行前端删除操作...')
      const tr = state.tr.delete(nodePos, nodePos + nodeSize)
      if (dispatch) {
        dispatch(tr)
        console.log('前端删除操作成功')
      } else {
        console.error('无法dispatch事务')
      }
    } else {
      console.error('未找到匹配的节点位置')
      
      // 方法2.3: 尝试使用更简单的删除方法
      console.log('方法2.3: 尝试直接删除当前节点')
      try {
        // 使用Tiptap的焦点和删除命令组合
        props.editor.commands.focus()
        props.editor.commands.deleteSelection()
        console.log('直接删除命令执行完成')
      } catch (error) {
        console.error('直接删除命令错误:', error)
      }
    }
  }, 100)
}
</script>

<style scoped>
.external-document-link-component {
  display: inline-block;
  position: relative;
}

.doc-item {
  display: flex;
  align-items: baseline;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
  cursor: pointer;
  background: #f0f0f0;
}

.doc-item:hover {
  background: #e0e0e0;
}

.doc-item.loading {
  cursor: default;
  opacity: 0.7;
}

.doc-item.loading:hover {
  background: #f0f0f0;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ccc;
  border-top: 2px solid #666;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 5px;
  transform: translateY(2px);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.file-icon {
  margin-right: 5px;
  transform: translateY(2px);
  color: #666;
}

.doc-title {
  flex-grow: 1;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 暗色主题样式 */
[data-theme="dark"] .doc-item {
  background: #2d2d2d;
}

[data-theme="dark"] .doc-item:hover {
  background: #3a3a3a;
}

[data-theme="dark"] .doc-item.loading:hover {
  background: #2d2d2d;
}

[data-theme="dark"] .loading-spinner {
  border: 2px solid #666;
  border-top: 2px solid #ccc;
}

[data-theme="dark"] .doc-title {
  color: #ffffff;
}

[data-theme="dark"] .file-icon {
  color: #cccccc;
}
</style>