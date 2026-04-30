<template>
  <div class="editor-container" spellcheck="false">
    <div v-if="editor">
      <floating-menu :editor="editor" v-if="showFloatingMenu" :tippy-options="{ placement: 'top' }">
        <div class="floating-menu">
          <div class="dropdown-container">
            <button @click="toggleHeadingDropdown" title="标题">
              <HeadingIcon :size="18" />
            </button>
            <div v-if="showHeadingDropdown" class="dropdown-menu">
              <button @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
                :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }" title="一级标题">
                <Heading1 :size="18" />
              </button>
              <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
                :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }" title="二级标题">
                <Heading2 :size="18" />
              </button>
              <button @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
                :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }" title="三级标题">
                <Heading3 :size="18" />
              </button>
            </div>
          </div>

          <button @click="editor.chain().focus().toggleCodeBlock().run()"
            :class="{ 'is-active': editor.isActive('codeBlock') }" title="代码块">
            <CodeXml :size="18" />
          </button>
          <button @click="editor.chain().focus().toggleBlockquote().run()"
            :class="{ 'is-active': editor.isActive('blockquote') }" title="引用">
            <TextQuote :size="18" />
          </button>
          <button @click="editor.chain().focus().setHorizontalRule().run()" title="分割线">
            <Minus :size="18" />
          </button>

          <!-- 表格按钮 -->
          <button @click="editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()" title="插入表格">
            <TableIcon :size="18" />
          </button>

          <!-- 列表下拉菜单 -->
          <div class="dropdown-container">
            <button @click="toggleListDropdown" title="列表">
              <List :size="18" />
            </button>
            <div v-if="showListDropdown" class="dropdown-menu">
              <button @click="editor.chain().focus().toggleBulletList().run()"
                :class="{ 'is-active': editor.isActive('bulletList') }" title="无序列表">
                <List :size="18" />
              </button>
              <button @click="editor.chain().focus().toggleOrderedList().run()"
                :class="{ 'is-active': editor.isActive('orderedList') }" title="有序列表">
                <ListOrdered :size="18" />
              </button>
              <button @click="editor.chain().focus().toggleTaskList().run()"
                :class="{ 'is-active': editor.isActive('taskList') }" title="任务列表">
                <ListTodo :size="18" />
              </button>
            </div>
          </div>
          <button @click="editor.chain().focus().setTextAlign('left').run()"
            :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }" title="左对齐">
            <AlignLeft :size="18" />
          </button>
          <button @click="editor.chain().focus().setTextAlign('center').run()"
            :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }" title="居中对齐">
            <AlignCenter :size="18" />
          </button>
          <button @click="editor.chain().focus().setTextAlign('right').run()"
            :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }" title="右对齐">
            <AlignRight :size="18" />
          </button>
          <!-- 添加内容 -->
          <button @click="addImage" title="添加图片">
            <ImageUp :size="18" />
          </button>
          <!-- 添加文档链接 -->
           <button @click="addExternalDocumentLink" title="添加外部文档">
            <FilePlus2 :size="18" />
          </button>
          <button @click="addDocumentLink" title="添加文档链接">
            <LinkIcon :size="18" />
          </button>
        </div>
      </floating-menu>

      <bubble-menu :editor="editor">
        <div class="floating-menu" :style="{ transform: `translateY(200%)` }">
          <div class="dropdown-container">
            <button @click="toggleHeadingDropdown" title="标题">
              <HeadingIcon :size="18" />
            </button>
            <div v-if="showHeadingDropdown" class="dropdown-menu">
              <button @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
                :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }" title="一级标题">
                <Heading1 :size="18" />
              </button>
              <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
                :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }" title="二级标题">
                <Heading2 :size="18" />
              </button>
              <button @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
                :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }" title="三级标题">
                <Heading3 :size="18" />
              </button>
            </div>
          </div>
          <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }" title="粗体">
            <Bold :size="18" />
          </button>
          <button @click="editor.chain().focus().toggleItalic().run()"
            :class="{ 'is-active': editor.isActive('italic') }" title="斜体">
            <Italic :size="18" />
          </button>
          <button @click="editor.chain().focus().toggleUnderline().run()"
            :class="{ 'is-active': editor.isActive('underline') }" title="下划线">
            <UnderlineIcon :size="18" />
          </button>
          <button @click="editor.chain().focus().toggleStrike().run()"
            :class="{ 'is-active': editor.isActive('strike') }" title="删除线">
            <Strikethrough :size="18" />
          </button>
          <button @click="editor.chain().focus().toggleHighlight().run()"
            :class="{ 'is-active': editor.isActive('highlight') }" title="高亮">
            <Highlighter :size="18" />
          </button>
          <button @click="increaseFontSize" title="增大字体">
            <AArrowUp :size="18" />
          </button>
          <button @click="decreaseFontSize" title="减小字体">
            <AArrowDown :size="18" />
          </button>
          <button @click="editor.chain().focus().setTextAlign('left').run()"
            :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }" title="左对齐">
            <AlignLeft :size="18" />
          </button>
          <button @click="editor.chain().focus().setTextAlign('center').run()"
            :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }" title="居中对齐">
            <AlignCenter :size="18" />
          </button>
          <button @click="editor.chain().focus().setTextAlign('right').run()"
            :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }" title="右对齐">
            <AlignRight :size="18" />
          </button>
        </div>
      </bubble-menu>

    </div>
    <editor-content :editor="editor" class="editor-content" />
  </div>
</template>

<script setup>
import { Heading as HeadingIcon, Heading1, Heading2, Heading3, TextQuote, List, AArrowDown,AArrowUp, Highlighter, Minus, FilePlus2} from 'lucide-vue-next'
import { CodeXml, ImageUp, AlignCenter, AlignLeft, AlignRight, ListOrdered, ListTodo, Italic, Bold, Underline as UnderlineIcon, Strikethrough, Table as TableIcon } from 'lucide-vue-next'
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useEditor, EditorContent, VueNodeViewRenderer } from '@tiptap/vue-3'
import { FloatingMenu, BubbleMenu } from '@tiptap/vue-3/menus'
import { TableKit } from '@tiptap/extension-table'
import StarterKit from '@tiptap/starter-kit'
import Document from '@tiptap/extension-document'
import Underline from '@tiptap/extension-underline'
import TaskItem from '@tiptap/extension-task-item'
import Strike from '@tiptap/extension-strike'
import BulletList from '@tiptap/extension-bullet-list'
import OrderedList from '@tiptap/extension-ordered-list'
import TaskList from '@tiptap/extension-task-list'
import Heading from '@tiptap/extension-heading'
import Blockquote from '@tiptap/extension-blockquote'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import HorizontalRule from '@tiptap/extension-horizontal-rule'
import Image from '@tiptap/extension-image'
import Highlight from '@tiptap/extension-highlight'
import TextAlign from '@tiptap/extension-text-align'
import Link from '@tiptap/extension-link'
import {TextStyle, FontSize} from '@tiptap/extension-text-style'
import { Placeholder } from '@tiptap/extensions'
import { DocStore } from '../../stores/NoteBook/DocumentStore'
import css from 'highlight.js/lib/languages/css'
import js from 'highlight.js/lib/languages/javascript'
import ts from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import html from 'highlight.js/lib/languages/xml'
import cpp from 'highlight.js/lib/languages/cpp'
import java from 'highlight.js/lib/languages/java'
import c from 'highlight.js/lib/languages/c'
import { createLowlight } from 'lowlight'
import CodeBlockComponent from './CodeBlockComponent.vue'
import DocumentLinkExtension from './DocumentLinkExtension.ts'
import ExternalDocumentLinkExtension from './ExternalDocumentLinkExtension.js'
import { Link as LinkIcon } from 'lucide-vue-next'


const CustomDocument = Document.extend({
  content: 'heading block*',
})

const docStore = DocStore()
// 将编辑器实例传递给DocumentStore

// create a lowlight instance
const lowlight = createLowlight()
const showFloatingMenu = ref(false)

// you can also register languages
lowlight.register('html', html)
lowlight.register('css', css)
lowlight.register('javascript', js)
lowlight.register('typescript', ts)
lowlight.register('python', python)
lowlight.register('c++', cpp)
lowlight.register('java', java)
lowlight.register('c', c)

const editor = useEditor({
  extensions: [
    CustomDocument,
    StarterKit.configure({
      document: false,
      codeBlock: false, // 禁用默认的 CodeBlock 扩展
    }),
    Placeholder.configure({
      placeholder: ({ node }) => {
        if (node.type.name === 'heading') {
          return 'What’s the title?'
        }

        return '按下 "/" 打开菜单'
      },
    }),
    Underline,
    Strike,
    Heading.configure({
      levels: [1, 2, 3],
    }),
    BulletList,
    OrderedList,
    TaskList,
    TaskItem,
    Link,
    Blockquote,
    CodeBlockLowlight.extend({
          addNodeView() {
            return VueNodeViewRenderer(CodeBlockComponent)
          },
        }).configure({ lowlight }),
    HorizontalRule,
    Image.configure({
      HTMLAttributes: {
        class: 'editor-image',
      },
    }),
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
    Highlight,
    TextStyle,
    FontSize,
    DocumentLinkExtension,
    ExternalDocumentLinkExtension,
    // 表格扩展
    TableKit.configure({
      table: {
            resizable: true,
          },
    }),
  ],
  content: `

  `,
  onUpdate: ({ editor }) => {
    if (docStore.currentDocId) {
      docStore.saveCurrentDocument(editor.getHTML())
      console.log('文档内容已更新')
    }
    
    // 检测当前行的前几个字符是否为'<p>/</p>'
    const { state } = editor
    const { selection } = state
    const { $from } = selection
    
    // 获取当前行的内容
    const lineContent = state.doc.textBetween($from.start(), $from.end(), '\n')
    console.log('当前行内容:', lineContent)
    
    if (lineContent.startsWith('/')) {
      // 删除'<p>/</p>'字符
      console.log('删除斜杠')
      
      editor.commands.deleteRange({ from: $from.pos - 1, to: $from.pos });
      showFloatingMenu.value = true
      // 显示浮动菜单
    }else{
      showFloatingMenu.value = false
    }
  },
})

watch(() => docStore.docChanged, async () => {
  
  if (docStore.currentDocId && editor.value) {
    // 使用新的内容获取方法
    const content = await docStore.getDocumentContent(docStore.currentDocId)
    editor.value.commands.setContent(content || '没找到')
    const currentDoc = docStore.documents.find(d => d.id === docStore.currentDocId)
    selectedProjectId.value = currentDoc?.projectId || null
  }
})

// 列表下拉菜单状态
const showListDropdown = ref(false)
const toggleListDropdown = () => showListDropdown.value = !showListDropdown.value

// 标题下拉菜单状态
const showHeadingDropdown = ref(false)
const toggleHeadingDropdown = () => showHeadingDropdown.value = !showHeadingDropdown.value

// 项目下拉菜单状态
const showProjectDropdown = ref(false)
const selectedProjectId = ref(null)

const increaseFontSize = () => {
  const currentSize = getCurrentFontSize();
  if (currentSize < 48 && editor.value) { // 设置最大阈值为72px
    editor.value.chain().focus()
      .setFontSize(`${currentSize + 3}px`)
      .run();
  }
};

const decreaseFontSize = () => {
  const currentSize = getCurrentFontSize();
  if (currentSize > 16 && editor.value) { // 设置最小阈值为12px
    editor.value.chain().focus()
      .setFontSize(`${currentSize - 3}px`)
      .run();
  }
};

const getCurrentFontSize = () => {
  if (!editor.value) return 16;
  const fontSize = editor.value.getAttributes('textStyle').fontSize;
  if (fontSize) {
    return parseInt(fontSize);
  }
  // 返回默认字体大小
  return 16;
};

// 关闭下拉菜单（点击外部时）
const closeDropdown = (e) => {
  const target = e.target;
  if (!target.closest('.dropdown-container')) {
    showListDropdown.value = false
    showHeadingDropdown.value = false
    showProjectDropdown.value = false
  }
}


// 初始化时添加点击监听
onMounted(() => {
  document.addEventListener('click', closeDropdown)
  docStore.docChanged = !docStore.docChanged
})

// 清理
onBeforeUnmount(() => {
  document.removeEventListener('click', closeDropdown)
  editor.value?.destroy()
})


// 添加文档链接
const addDocumentLink = () => {
  if (editor.value && docStore.selectedDocId) {
    // 使用选中的文档ID
    editor.value.chain().focus().insertContent({ type: 'documentLink', attrs: { id: docStore.selectedDocId } }).run()
    docStore.docChanged = !docStore.docChanged;
    // 重置selectedDocId
    docStore.selectedDocId = '';
  } else if (editor.value) {
    // 如果没有选中的文档，则生成唯一ID
    const uniqueId = `doc-link-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    editor.value.chain().focus().insertContent({ type: 'documentLink', attrs: { id: uniqueId } }).run()
    docStore.docChanged = !docStore.docChanged;
  }
}

const addExternalDocumentLink = async () => {
  if (editor.value) {
    const input = document.createElement('input')
    input.type = 'file'
    input.onchange = async (e) => {
      const target = e.target
      const file = target.files?.[0]
      if (!file) return

      // 文件类型验证
      const allowedTypes = [
        'text/plain',
        'text/markdown',
        'text/csv',
        'text/xls',
        'text/xlsx',
        'application/json',
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/gif'
      ];
      
      // 文件大小限制 (50MB)
      const maxSize = 50 * 1024 * 1024;
      
      // 验证文件类型
      if (!allowedTypes.includes(file.type) && !file.name.match(/\.(txt|md|csv|xls|xlsx|json|pdf|jpe?g|png|gif)$/i)) {
        alert('不支持的文件类型！请上传文本、Markdown、CSV、JSON、PDF或图片文件。');
        return;
      }
      
      // 验证文件大小
      if (file.size > maxSize) {
        alert('文件过大！最大支持50MB。');
        return;
      }

      try {
        // 生成UUID
        const uniqueId = crypto.randomUUID()
        
        // 先插入加载中的文档链接节点
        if (!editor.value) return
        
        // 插入加载状态的节点
        editor.value.chain().focus().insertContent({
          type: 'externalDocumentLink',
          attrs: { 
            id: uniqueId,
            fileName: file.name,
            filePath: '',
            fileUrl: '',
            loading: true  // 添加loading状态标记
          }
        }).run()
        
        
        // 异步处理文件上传和API调用
        setTimeout(async () => {
          try {
            // 读取文件内容
            const arrayBuffer = await file.arrayBuffer()
            const buffer = new Uint8Array(arrayBuffer)
            
            // 保存文件到用户文档目录
            const result = await (window).ipcRenderer.invoke('save-file', {
              fileName: file.name,
              fileData: buffer
            })
            
            if (result.success) {
              // 获取当前文档的content_id
              const contentId = docStore.currentDocId || 'default-content-id'
              
              // 调用Flask后端API创建转换文档记录
              const axios = (await import('axios')).default
              const response = await axios.post('http://localhost:5000/api/converted_documents', {
                id: uniqueId,
                content_id: contentId,
                file_path: result.filePath
              })
              
              if (response.status === 201) {
                // 更新节点状态为正常显示
                if (editor.value) {
                  editor.value.chain().focus().command(({ tr, dispatch }) => {
                    if (dispatch) {
                      // 查找并更新对应的节点
                      tr.doc.descendants((node, pos) => {
                        if (node.type.name === 'externalDocumentLink' && node.attrs.id === uniqueId) {
                          tr.setNodeMarkup(pos, undefined, {
                            ...node.attrs,
                            filePath: result.filePath,
                            fileUrl: `file://${result.filePath}`,
                            loading: false  // 移除loading状态
                          })
                        }
                      })
                    }
                    return true
                  }).run()
                }
                
                docStore.docChanged = !docStore.docChanged
                
                console.log('文件已保存到:', result.filePath)
                console.log('转换文档记录已创建，ID:', uniqueId)
              } else {
                throw new Error('创建转换文档记录失败')
              }
            } else {
              throw new Error(result.error)
            }
          } catch (error) {
            console.error('文件处理失败:', error)
            
            // 删除加载中的节点
            if (editor.value) {
              editor.value.chain().focus().command(({ tr, dispatch }) => {
                if (dispatch) {
                  // 查找并删除对应的节点
                  tr.doc.descendants((node, pos) => {
                    if (node.type.name === 'externalDocumentLink' && node.attrs.id === uniqueId) {
                      tr.delete(pos, pos + node.nodeSize)
                    }
                  })
                }
                return true
              }).run()
            }
            
            alert('文件保存失败: ' + (error).message)
          }
        }, 0)
        
      } catch (error) {
        console.error('文件处理失败:', error)
        alert('文件处理失败: ' + (error).message)
      }
    }
    input.click()
  }
}

// 图片上传处理
const addImage = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const target = e.target;
    const file = target.files?.[0]
    if (!file) return

    try {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => {
        if (editor.value && typeof reader.result === 'string') {
          editor.value.chain().focus()
            .setImage({ src: reader.result })
            .run()
        }
      }
    } catch (error) {
      console.error('图片上传失败:', error)
    }
  }
  input.click()
}

// 初始化编辑器

</script>

<style>

.floating-menu {
  z-index: 9999;
  display: flex;
  position: relative;
  gap: 0;
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
  padding: 3px;
  border: 1px solid #eee;
  transform: translateY(80%);
}

.floating-menu button {
  min-width: 32px;
  height: 32px;
  border: none;
  background: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.floating-menu button:hover {
  background: #f5f5f5;
}

.floating-menu button.is-active {
  background: #000;
  color: white;
}

/* 下拉菜单容器 */
.dropdown-container {
  position: relative;
}

/* 下拉菜单样式 */
.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px;
  z-index: 100;
  margin-top: 8px;
  border: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dropdown-menu button {
  text-align: left;
  font-weight: normal;
  border-radius: 4px;
  white-space: nowrap;
}

.dropdown-menu button:hover {
  background: #f5f5f5;
}

.remove-project-btn {
  color: #ff4757;
  font-weight: 500;
  border-top: 1px solid #eee;
  margin-top: 4px;
  padding-top: 4px;
}

/* 编辑器基本样式 */
.editor-container {
  height: 100vh;
  width: 98%;
  margin: 0 auto;
  overflow: hidden;
  background: white;
}

.editor-content {
  padding: 20px;
  height: calc(100% - 60px);
  overflow-y: auto;
}

/* 富文本内容样式 */
.ProseMirror {
  font-family: -apple-system, "Segoe UI", sans-serif;
  line-height: 1.6;
  font-size: 16px;
  outline: none !important;
}

.ProseMirror:focus {
  box-shadow: none !important;
}
.ProseMirror hr {
  margin: 10px 0px;
}

.ProseMirror h1 {
  font-size: 2.8em;
  margin: 0.3em 0;
}

.ProseMirror h2 {
  font-size: 1.9em;
  margin: 0.5em 0;
}
.ProseMirror h3 {
  font-size: 1.4em;
  margin: 0.4em 0;
}

.ProseMirror ul,
.ProseMirror ol {
  padding-left: 30px;
}

.ProseMirror blockquote {
  border-left: 3px solid #ddd;
  margin-left: 0;
  padding-left: 1em;
  color: #666;
}

.editor-image {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 10px 0;
}

.ProseMirror p.is-empty::before {
  content: attr(data-placeholder);
  float: left;
  color: #adb5bd;
  pointer-events: none;
  height: 0;
}
.ProseMirror p{
  padding-bottom: 3px;
  padding-top: 3px;
}

/* Table-specific styling */
table {
  border-collapse: collapse;
  margin: 0;
  overflow: hidden;
  table-layout: fixed;
  width: 100%;
}

table td,
table th {
  border: 1px solid #ddd;
  box-sizing: border-box;
  min-width: 1em;
  padding: 6px 8px;
  position: relative;
  vertical-align: top;
}

table th {
  background-color: #f8f9fa;
  font-weight: bold;
  text-align: left;
}

.selectedCell:after {
  background: rgba(0, 0, 0, 0.1);
  content: '';
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  pointer-events: none;
  position: absolute;
  z-index: 2;
}

.column-resize-handle {
  background-color: #007bff;
  bottom: -2px;
  pointer-events: none;
  position: absolute;
  right: -2px;
  top: 0;
  width: 4px;
}

.tableWrapper {
  margin: 1.5rem 0;
  overflow-x: auto;
}

.resize-cursor {
  cursor: ew-resize;
  cursor: col-resize;
}

/* 代码块样式 */
.ProseMirror pre {
  background: #f9f9f9; /* 更明亮的背景 */
  border-radius: 6px;
  padding: 0px 16px;
  margin: 10px 0px;
  overflow: auto;
  font-family: 'Consolas';
  font-size: 14px;
  line-height: 1.5;
  color: #333333; /* 更深的文本颜色 */
}

.ProseMirror code {
  font-family: 'Consolas';
  font-size: 16px;
  background-color: #f4f3f3;
  padding: 2px 4px;
  margin: 0px 4px;
  border-radius: 3px;
  color: #333333;
}

.ProseMirror pre code {
  background-color: transparent;
  border-radius: 0;
  color: inherit;
}

/* Code styling for light theme */
.hljs-comment,
.hljs-quote {
  color: #999999; /* 更柔和的注释颜色 */
}
 .hljs-string,
 .hljs-symbol,
 .hljs-bullet {
  color: #3a75b8; /* 调整为更适合暗色主题的绿色 */
}
.hljs-variable,
.hljs-template-variable,
.hljs-attribute,
.hljs-tag,
.hljs-name,
.hljs-regexp,
.hljs-link,
.hljs-name,
.hljs-selector-id,
.hljs-selector-class {
  color: #d73a49; /* GitHub 风格的红色 */
}

.hljs-number,
.hljs-meta,
.hljs-built_in,
.hljs-builtin-name,
.hljs-literal,
.hljs-type,
.hljs-params {
  color: #005cc5; /* GitHub 风格的蓝色 */
}

.hljs-string,
.hljs-symbol,
.hljs-bullet {
  color: #032f62; /* GitHub 风格的深蓝色 */
}

.hljs-title,
.hljs-section {
  color: #6f42c1; /* GitHub 风格的紫色 */
}

.hljs-keyword,
.hljs-selector-tag {
  color: #d73a49; /* GitHub 风格的红色 */
}

.hljs-emphasis {
  font-style: italic;
}

.hljs-strong {
  font-weight: 700;
}

.hljs-punctuation {
  color: #e49149; /* 括号颜色 */
}

.hljs-bracket {
  color: #24292e; /* GitHub 风格的深灰色 */
}

.hljs-curly-bracket {
  color: #24292e; /* 花括号颜色 */
  font-weight: bold; /* 加粗以突出层级 */
}

/* 暗色主题样式 */
[data-theme="dark"] .editor-container {
  background-color: #1e1e1e;
  color: #ffffff;
}

[data-theme="dark"] .floating-menu {
  background-color: #2d2d2d;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid #444;
}

[data-theme="dark"] .floating-menu button {
  color: #ffffff;
  background: none;
}

[data-theme="dark"] .floating-menu button:hover {
  background: #3a3a3a;
}

[data-theme="dark"] .floating-menu button.is-active {
  background: #007acc;
  color: #ffffff;
}
[data-theme="dark"] .dropdown-container .dropdown-menu {
  background: #2d2d2d;
  border: 1px solid #444;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

[data-theme="dark"] .dropdown-container .dropdown-menu button {
  color: #ffffff;
}

[data-theme="dark"] .dropdown-container .dropdown-menu button:hover {
  background: #3a3a3a;
}

[data-theme="dark"] .editor-content {
  background-color: #1e1e1e;
  color: #ffffff;
}

[data-theme="dark"] .ProseMirror {
  color: #ffffff;
}

[data-theme="dark"] .ProseMirror p a {
  color: #bb86fc !important;
}


[data-theme="dark"] .ProseMirror h1,
[data-theme="dark"] .ProseMirror h2,
[data-theme="dark"] .ProseMirror h3 {
  color: #ffffff !important;
}

[data-theme="dark"] .ProseMirror blockquote {
  border-left: 3px solid #555;
  color: #cccccc;
}
[data-theme="dark"] .ProseMirror hr {
  border-color: #555;
}


[data-theme="dark"] .ProseMirror code {
  background-color: #2D2D2D;
  color: #ffffff;
}


[data-theme="dark"] .ProseMirror p.is-empty:first-child::before {
  color: #666666;
}



/* 暗色主题代码高亮样式 */
[data-theme="dark"] .hljs-comment,
[data-theme="dark"] .hljs-quote {
  color: #999999;
}

[data-theme="dark"] .hljs-variable,
[data-theme="dark"] .hljs-template-variable,
[data-theme="dark"] .hljs-attribute,
[data-theme="dark"] .hljs-tag,
[data-theme="dark"] .hljs-name,
[data-theme="dark"] .hljs-regexp,
[data-theme="dark"] .hljs-link,
[data-theme="dark"] .hljs-selector-id,
[data-theme="dark"] .hljs-selector-class {
  color: #ff7b85; /* 调整为更适合暗色主题的红色 */
}

[data-theme="dark"] .hljs-number,
[data-theme="dark"] .hljs-meta,
[data-theme="dark"] .hljs-built_in,
[data-theme="dark"] .hljs-builtin-name,
[data-theme="dark"] .hljs-literal,
[data-theme="dark"] .hljs-type,
[data-theme="dark"] .hljs-params {
  color: #66d9ef; /* 调整为更适合暗色主题的蓝色 */
}

[data-theme="dark"] .hljs-string,
[data-theme="dark"] .hljs-symbol,
[data-theme="dark"] .hljs-bullet {
  color: #9ECBFF; /* 调整为更适合暗色主题的绿色 */
}

[data-theme="dark"] .hljs-title,
[data-theme="dark"] .hljs-section {
  color: #ae81ff; /* 调整为更适合暗色主题的紫色 */
}

[data-theme="dark"] .hljs-keyword,
[data-theme="dark"] .hljs-selector-tag {
  color: #f92672; /* 调整为更适合暗色主题的粉色 */
}

[data-theme="dark"] .hljs-emphasis {
  font-style: italic;
}

[data-theme="dark"] .hljs-strong {
  font-weight: 700;
}

[data-theme="dark"] .hljs-punctuation {
  color: #e49149;
}

[data-theme="dark"] .hljs-bracket {
  color: #f8f8f2;
}

[data-theme="dark"] .hljs-curly-bracket {
  color: #f8f8f2;
  font-weight: bold;
}

/* Table-specific styling */
[data-theme="dark"] table {
  border-collapse: collapse;
  margin: 0;
  overflow: hidden;
  table-layout: fixed;
  width: 100%;
}

[data-theme="dark"] table td,
[data-theme="dark"] table th {
  border: 1px solid #444;
  box-sizing: border-box;
  min-width: 1em;
  padding: 6px 8px;
  position: relative;
  vertical-align: top;
}

[data-theme="dark"] table th {
  background-color: #2d2d2d;
  font-weight: bold;
  text-align: left;
}

[data-theme="dark"] .selectedCell:after {
  background: rgba(255, 255, 255, 0.2);
  content: '';
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  pointer-events: none;
  position: absolute;
  z-index: 2;
}

[data-theme="dark"] .column-resize-handle {
  background-color: #bb86fc;
  bottom: -2px;
  pointer-events: none;
  position: absolute;
  right: -2px;
  top: 0;
  width: 4px;
}

[data-theme="dark"] .tableWrapper {
  margin: 1.5rem 0;
  overflow-x: auto;
}

[data-theme="dark"] .resize-cursor {
  cursor: ew-resize;
  cursor: col-resize;
}
</style>