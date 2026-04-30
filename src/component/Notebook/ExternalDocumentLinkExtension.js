import { Node } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import ExternalDocumentLinkComponent from './ExternalDocumentLinkComponent.vue'

export default Node.create({
  name: 'externalDocumentLink',

  group: 'inline',

  inline: true,

  selectable: false,

  atom: true,

  addCommands() {
    return {
      deleteExternalDocumentLink: () => ({ state, dispatch }) => {
        const { $from } = state.selection
        let nodePos = -1
        let nodeSize = 0
        
        // 遍历文档查找当前节点
        state.doc.descendants((node, pos) => {
          if (node.type.name === 'externalDocumentLink' && pos <= $from.pos && pos + node.nodeSize > $from.pos) {
            nodePos = pos
            nodeSize = node.nodeSize
            return false
          }
          return true
        })
        
        if (nodePos !== -1) {
          const tr = state.tr.delete(nodePos, nodePos + nodeSize)
          if (dispatch) dispatch(tr)
          return true
        }
        
        return false
      },
    }
  },

  addKeyboardShortcuts() {
    return {
      'Backspace': ({ editor }) => {
        const { state } = editor
        const { $from, $to } = state.selection
        
        console.log('Backspace按键触发 - 光标位置:', $from.pos, '到', $to.pos)
        
        // 检查删除范围是否包含externalDocumentLink节点
        let containsExternalDocumentLink = false
        
        // 遍历删除范围内的所有节点
        state.doc.nodesBetween($from.pos, $to.pos, (node, pos) => {
          console.log('检查节点:', node.type.name, '位置:', pos)
          if (node.type.name === 'externalDocumentLink') {
            containsExternalDocumentLink = true
            console.log('发现externalDocumentLink节点在删除范围内')
            return false // 停止遍历
          }
          return true
        })
        
        // 如果删除范围包含externalDocumentLink节点，阻止删除操作
        if (containsExternalDocumentLink) {
          console.log('阻止Backspace删除 - 删除范围内包含externalDocumentLink节点')
          return true
        }
        
        // 检查光标是否紧挨着externalDocumentLink节点
        // 当光标在节点前面时，Backspace会删除节点
        const nodeBefore = $from.nodeBefore
        const nodeAfter = $from.nodeAfter
        
        console.log('前一个节点:', nodeBefore?.type.name, '后一个节点:', nodeAfter?.type.name)
        
        if (nodeBefore && nodeBefore.type.name === 'externalDocumentLink') {
          console.log('阻止Backspace删除 - 光标在externalDocumentLink节点前面')
          return true
        }
        
        if (nodeAfter && nodeAfter.type.name === 'externalDocumentLink') {
          console.log('阻止Backspace删除 - 光标在externalDocumentLink节点后面')
          return true
        }
        
        // 检查光标是否在externalDocumentLink节点内
        let isInExternalDocumentLink = false
        state.doc.descendants((node, pos) => {
          if (node.type.name === 'externalDocumentLink' && pos <= $from.pos && pos + node.nodeSize > $from.pos) {
            isInExternalDocumentLink = true
            console.log('光标在externalDocumentLink节点内')
            return false
          }
          return true
        })
        
        if (isInExternalDocumentLink) {
          console.log('阻止Backspace删除 - 光标在externalDocumentLink节点内')
          return true
        }
        
        console.log('允许Backspace删除 - 未检测到externalDocumentLink节点')
        return false
      },
      'Delete': ({ editor }) => {
        const { state } = editor
        const { $from, $to } = state.selection
        
        // 检查删除范围是否包含externalDocumentLink节点
        let containsExternalDocumentLink = false
        
        // 遍历删除范围内的所有节点
        state.doc.nodesBetween($from.pos, $to.pos, (node, pos) => {
          if (node.type.name === 'externalDocumentLink') {
            containsExternalDocumentLink = true
            return false // 停止遍历
          }
          return true
        })
        
        // 如果删除范围包含externalDocumentLink节点，阻止删除操作
        if (containsExternalDocumentLink) {
          return true
        }
        
        // 检查光标是否紧挨着externalDocumentLink节点
        const nodeBefore = $from.nodeBefore
        const nodeAfter = $from.nodeAfter
        
        if (nodeBefore && nodeBefore.type.name === 'externalDocumentLink') {
          return true
        }
        
        if (nodeAfter && nodeAfter.type.name === 'externalDocumentLink') {
          return true
        }
        
        // 检查光标是否在externalDocumentLink节点内
        let isInExternalDocumentLink = false
        state.doc.descendants((node, pos) => {
          if (node.type.name === 'externalDocumentLink' && pos <= $from.pos && pos + node.nodeSize > $from.pos) {
            isInExternalDocumentLink = true
            return false
          }
          return true
        })
        
        if (isInExternalDocumentLink) {
          return true
        }
        
        return false
      },
    }
  },

  addAttributes() {
    return {
      id: {
        default: null,
        parseHTML: element => element.getAttribute('data-id'),
        renderHTML: attributes => {
          if (!attributes.id) {
            return {}
          }
          return {
            'data-id': attributes.id,
          }
        },
      },
      fileName: {
        default: null,
        parseHTML: element => element.getAttribute('data-file-name'),
        renderHTML: attributes => {
          if (!attributes.fileName) {
            return {}
          }
          return {
            'data-file-name': attributes.fileName,
          }
        },
      },
      filePath: {
        default: null,
        parseHTML: element => element.getAttribute('data-file-path'),
        renderHTML: attributes => {
          if (!attributes.filePath) {
            return {}
          }
          return {
            'data-file-path': attributes.filePath,
          }
        },
      },
      fileUrl: {
        default: null,
        parseHTML: element => element.getAttribute('data-file-url'),
        renderHTML: attributes => {
          if (!attributes.fileUrl) {
            return {}
          }
          return {
            'data-file-url': attributes.fileUrl,
          }
        },
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'external-document-link',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['external-document-link', HTMLAttributes]
  },

  addNodeView() {
    return VueNodeViewRenderer(ExternalDocumentLinkComponent)
  },
})