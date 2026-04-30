<template>
  <node-view-wrapper class="document-link-component">
    <div class="document-link-content">
      <div v-if="!selectedDocumentForDisplay" @click="toggleDropdown" class="document-link-button">
        <Link :size="16" />
        <span>链接文档  </span>
      </div>
      <div v-else class="doc-item-container">
        <div class="doc-item" @click="handleSelect">
          <FileText :size="16" class="file-icon" color="#666"/>
          <span class="doc-title">{{ selectedDocumentForDisplay.title }}</span>
        </div>
      </div>
      <div v-if="showDropdown" class="document-dropdown">
        <input 
          v-model="searchQuery" 
          placeholder="搜索文档" 
          class="document-search-input"
          @input="performSearch"
        />
        <div class="document-list-container">
          <div class="document-list">
            <div 
              v-for="doc in paginatedDocuments" 
              :key="doc.id" 
              @click="selectDocument(doc)"
              :class="['document-item', { selected: selectedDocument && selectedDocument.id === doc.id }]"
              class="document-item"
            >
            <FileText :size="16" class="file-icon" color="#666"/>
              {{ doc.title }}
            </div>
          </div>
          <div v-if="totalPages > 1" class="pagination">
            <ChevronLeft :size="16" @click="prevPage" :class="{ disabled: currentPage === 1 }" />
            <span>{{ currentPage }} / {{ totalPages }}</span>
            <ChevronRight :size="16" @click="nextPage" :class="{ disabled: currentPage === totalPages }" />
          </div>
        </div>
        <button 
          v-if="selectedDocument" 
          @click="confirmSelection" 
          class="confirm-button"
        >
          确认选择
        </button>
      </div>
    </div>
  </node-view-wrapper>
</template>

<script setup>
import { nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'
import { ref, computed, watch, onMounted } from 'vue'
import { Link, FileText, Trash2, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { DocStore } from '../../stores/NoteBook/DocumentStore'
import { SideBarParams } from '../../stores/NoteBook/SideBarParams'

const props = defineProps(nodeViewProps)

const docStore = DocStore()
const useSideBarParams = SideBarParams()
const showDropdown = ref(false)
const searchQuery = ref('')
const selectedDocument = ref(null)
const selectedDocumentForDisplay = ref(null)
const currentPage = ref(1)
const itemsPerPage = 5

// Load selectedDocumentForDisplay from localStorage on component mount
const loadSelectedDocument = () => {
  const savedDocument = localStorage.getItem(`selectedDocumentForDisplay-${props.node.attrs.id}`)
  if (savedDocument) {
    selectedDocumentForDisplay.value = JSON.parse(savedDocument)
  }
}

// Save selectedDocumentForDisplay to localStorage
const saveSelectedDocument = () => {
  if (selectedDocumentForDisplay.value) {
    localStorage.setItem(`selectedDocumentForDisplay-${props.node.attrs.id}`, JSON.stringify(selectedDocumentForDisplay.value))
  } else {
    localStorage.removeItem(`selectedDocumentForDisplay-${props.node.attrs.id}`)
  }
}

// Watch for changes to selectedDocumentForDisplay and save to localStorage
watch(selectedDocumentForDisplay, saveSelectedDocument, { deep: true })

// Load the selected document when the component is mounted
onMounted(() => {
  loadSelectedDocument()
})

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
  searchQuery.value = ''
  selectedDocument.value = null
  currentPage.value = 1
}

const filteredDocuments = computed(() => {
  if (!searchQuery.value.trim()) {
    return docStore.documents
  }
  return docStore.documents.filter(doc => 
    doc.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const totalPages = computed(() => {
  return Math.ceil(filteredDocuments.value.length / itemsPerPage)
})

const paginatedDocuments = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredDocuments.value.slice(start, end)
})

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const performSearch = () => {
  // 搜索会在computed属性filteredDocuments中自动执行
}

const selectDocument = (doc) => {
  selectedDocument.value = doc
}

const confirmSelection = () => {
  if (selectedDocument.value) {
    selectedDocumentForDisplay.value = selectedDocument.value
    docStore.selectedDocId = selectedDocument.value.id // 设置选中的文档ID
    showDropdown.value = false
    // 更新节点属性
    props.updateAttributes({ id: selectedDocument.value.id })
    // Save to localStorage immediately after selection
    saveSelectedDocument()
    // 重置selectedDocId
    setTimeout(() => {
      docStore.selectedDocId = '';
    }, 0);
  }
}

const handleSelect = () => {
  if (selectedDocumentForDisplay.value) {
    docStore.currentDocId = selectedDocumentForDisplay.value.id
    docStore.selectedDocId = selectedDocumentForDisplay.value.id // 同时设置selectedDocId
    useSideBarParams.resetViews();
    useSideBarParams.isShowPage = true;
    docStore.docChanged = !docStore.docChanged;
    // 更新节点属性以确保ID正确
    props.updateAttributes({ id: selectedDocumentForDisplay.value.id })
    // 重置selectedDocId
    setTimeout(() => {
      docStore.selectedDocId = '';
    }, 0);
  }
}

const removeLink = () => {
  selectedDocumentForDisplay.value = null
  // 调用 Tiptap 的 deleteNode 命令删除当前节点
  props.editor.commands.deleteNode('documentLink')
  // Remove from localStorage
  localStorage.removeItem(`selectedDocumentForDisplay-${props.node.attrs.id}`)
}
</script>

<style scoped>
.document-link-component {
  display: inline-block;
  position: relative;
}

.document-link-button {
  display: flex;
  align-items: baseline;
  color: #333333;
  gap: 4px;
  padding: 0px 8px;
  border-radius: 4px;
  cursor: pointer;
}

.document-link-button:hover {
  text-decoration: underline;
}

.document-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 250px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  padding: 8px;
}

.document-search-input {
  width: 100%;
  padding: 6px;
  margin-bottom: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
}

.document-list-container {
  display: flex;
  flex-direction: column;
}

.document-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  padding: 0;
  padding-left: 0;
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.pagination svg {
  cursor: pointer;
}

.pagination svg.disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.document-item {
  width: 100%;
  padding: 6px;
  cursor: pointer;
  border-radius: 4px;
}

.document-item:hover {
  background-color: #f0f0f0;
}

.document-item.selected {
  background-color: #f0f0f0;
}

.doc-title:hover {
  text-decoration: underline;
}

.confirm-button {
  width: 100%;
  padding: 6px;
  margin-top: 8px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.confirm-button:hover {
  background-color: #0056b3;
}



.doc-item {
  display: flex;
  align-items: baseline;
  padding: 0px 0px;
  border-radius: 6px;
  transition: background 0.2s;
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

.doc-item-container:hover .delete-icon {
  opacity: 1;
}

/* 暗色主题样式 */
[data-theme="dark"] .document-link-component {
  background-color: #1e1e1e;
}

[data-theme="dark"] .document-link-button {
  color: #ffffff;
}

[data-theme="dark"] .document-dropdown {
  background: #2d2d2d;
  border: 1px solid #444;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

[data-theme="dark"] .document-search-input {
  background: #3a3a3a;
  border: 1px solid #555;
  color: #ffffff;
}

[data-theme="dark"] .document-search-input:focus {
  border-color: #007acc;
}

[data-theme="dark"] .document-item {
  color: #ffffff;
}

[data-theme="dark"] .document-item:hover {
  background-color: #3a3a3a;
}

[data-theme="dark"] .document-item.selected {
  background-color: #3a3a3a;
}

[data-theme="dark"] .doc-title {
  color: #ffffff;
}

[data-theme="dark"] .confirm-button {
  background-color: #007acc;
  color: #ffffff;
}

[data-theme="dark"] .confirm-button:hover {
  background-color: #005a9e;
}

[data-theme="dark"] .doc-item-container {
  background: #1d1d1d;
}

[data-theme="dark"] .file-icon {
  color: #cccccc;
}
</style>