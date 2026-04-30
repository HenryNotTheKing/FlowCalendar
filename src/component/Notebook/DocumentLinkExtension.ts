import { Node } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import DocumentLinkComponent from './DocumentLinkComponent.vue'
declare const DocumentLinkExtension: any;
export default Node.create({
  name: 'documentLink',

  group: 'inline',

  inline: true,

  selectable: false,

  atom: true,

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
    }
  },

  parseHTML() {
    return [
      {
        tag: 'document-link',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['document-link', HTMLAttributes]
  },

  addNodeView() {
    return VueNodeViewRenderer(DocumentLinkComponent)
  },
})