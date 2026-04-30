<template>
  <div class="project-catalog">
    <!-- 空状态提示 -->
    <div v-if="!activeProject" class="empty-state">
      <h3>未选择项目</h3>
    </div>
    <div v-else>
      <div class="project-title" 
        v-if="!editingProjectTitle" 
        @click="editProjectTitle"
      >
        {{ activeProject.name }}
    </div>
      <input 
        v-else 
        v-model="projectTitleInput" 
        @blur="saveProjectTitle" 
        @keyup.enter="saveProjectTitle" 
        class="project-title-input" 
        ref="projectTitleInputRef"
      />
      <div class="create-document">
        <input 
          v-model="newDocTitle"
          placeholder="输入新文档标题"
          @keyup.enter="createDocument"
          @blur="createDocument"
          class="doc-input"
        />
      </div>
      
      <!-- 项目文档列表 -->
      <template v-if="activeProject.documents.length > 0">
        <ul class="document-list">
          <li 
            v-for="doc in sortedDocuments" 
            :key="doc.id" 
            @click="editingDocId === doc.id ? null : handleSelect(doc.id)" 
            class="doc-item-container"
          >
            <div class="doc-item">
              <FileText :size="16" class="file-icon" color="#666"/>
              <input 
                v-if="editingDocId === doc.id" 
                v-model="doc.title" 
                @blur="finishEditing(doc)" 
                @keyup.enter="finishEditing(doc)" 
                class="edit-input" 
                :data-doc-id="doc.id"
                :key="doc.id"
              />
              <span v-else class="doc-title">{{ doc.title }}</span>
              <span class="doc-date">{{ formatDate(doc.createdAt) }}</span>
              <FilePen v-if="activeProject.id !== 'rcwd'" :size="16" class="edit-icon" @click.stop="editDocTitle(doc)" color="#666"/>
              <Trash2 v-if="activeProject.id !== 'rcwd'" :size="16" class="delete-icon" @click.stop="deleteDoc(doc.id)" color="#666"/>
            </div>
          </li>
        </ul>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, nextTick } from 'vue'
import { ProjectParams } from '../../stores/NoteBook/ProjectParams'
import { DocStore } from '../../stores/NoteBook/DocumentStore'
import { FileText, Trash2, FilePen } from 'lucide-vue-next'
import { SideBarParams } from '../../stores/NoteBook/SideBarParams'

const useSideBarParams = SideBarParams();
const projectStore = ProjectParams()
const docStore = DocStore()

const emit = defineEmits(['select-document'])

const activeProject = computed(() => projectStore.activeProject)
const newDocTitle = ref('');

// 编辑项目标题相关
const editingProjectTitle = ref(false);
const projectTitleInput = ref('');
const projectTitleInputRef = ref(null);

const createDocument = () => {
  if (!newDocTitle.value.trim()) return;
  
  docStore.createDocumentToProject(activeProject.value.id, newDocTitle.value);

  newDocTitle.value = '';
};

// 编辑项目标题相关函数
const editProjectTitle = () => {
  // 检查项目是否是默认项目，如果是则不允许编辑
  if (activeProject.value && activeProject.value.id === 'rcwd') {
    return;
  }
  
  editingProjectTitle.value = true;
  projectTitleInput.value = activeProject.value.name;
  
  nextTick(() => {
    if (projectTitleInputRef.value) {
      projectTitleInputRef.value.focus();
      // 选中所有文本
      projectTitleInputRef.value.select();
    }
  });
};

const saveProjectTitle = async () => {
  if (projectTitleInput.value.trim() !== '' && activeProject.value) {
    try {
      await projectStore.updateProjectName(activeProject.value.id, projectTitleInput.value.trim());
    } catch (error) {
      console.error('更新项目标题失败:', error);
    }
  }
  
  editingProjectTitle.value = false;
};

const sortedDocuments = computed(() => {
  if (!activeProject.value) return [];
  // 获取最新文档列表
  const docs = projectStore.getProjectDocuments(activeProject.value.id);
  return docs.sort((a, b) => 
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );
});

const handleSelect = (id) => {
  docStore.currentDocId = id;
  docStore.selectedDocId = id; // 同时设置选中的文档ID
  useSideBarParams.resetViews();
  useSideBarParams.isShowPage = true;
  docStore.docChanged = !docStore.docChanged;
}

const deleteDoc = (docId) => {
  // 从项目中移除文档
  if (activeProject.value) {
    projectStore.removeDocumentFromProject(activeProject.value.id, docId)
  }
  
  // 从全局文档存储中删除文档
  docStore.deleteDocument(docId)
}

// 编辑文档标题相关
const editingDocId = ref(null)

const editDocTitle = (doc) => {
  // 检查文档是否属于默认项目，如果是则不允许编辑
  if (activeProject.value && activeProject.value.id === 'rcwd') {
    // 可以选择是否显示提示信息
    // alert('默认项目中的文档标题不能编辑');
    return;
  }
  
  editingDocId.value = doc.id
  nextTick(() => {
    // 通过DOM查询获取正确的输入框元素
    const inputElement = document.querySelector(`input[data-doc-id="${doc.id}"]`)
    if (inputElement) {
      inputElement.focus()
      // 使用 setSelectionRange 确保文本被选中
      inputElement.setSelectionRange(0, inputElement.value.length)
    }
  })
}

const finishEditing =async (doc) => {
  editingDocId.value = null;

  await docStore.getDocumentContent(doc.id);

  const docInStore = docStore.documents.find(d => d.id === doc.id);
  const contentInStore = docStore.contentCache.find(c => c.id === doc.id);
  if (docInStore && doc.title.trim() !== '') {
    contentInStore.content = contentInStore.content.replace(/<h1>(.*?)<\/h1>/, `<h1>${doc.title.trim()}</h1>`);
    docStore.saveCurrentDocument(contentInStore.content);
  }
};


const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  
  // 如果是今天
  if (date.toDateString() === now.toDateString()) {
    return '今天'
  }
  
  // 如果是昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  }
  
  // 其他日期格式
  return `${date.getMonth() + 1}月${date.getDate()}日`
}
</script>

<style scoped>
.project-catalog {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.create-document {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  margin-bottom: 20px;
}

.doc-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
}

.create-button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
}

.create-button:hover {
  background-color: #45a049;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  font-weight: 500;
  font-size: 18px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: #999;
}

.document-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.doc-item-container {
  padding: 0px 8px;
  cursor: pointer;
  border-radius: 4px;
}


.doc-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.2s;
}

.file-icon {
  margin-right: 12px;
  color: #666;
}

.doc-title {
  user-select: none;
  flex-grow: 1;
  margin-right: 10px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.doc-date {
  font-size: 12px;
  color: #999;
  margin-right: 8px;
  flex-shrink: 0;
}

/* 暗色主题样式 */
[data-theme="dark"] .project-catalog {
  background-color: #1e1e1e;
  color: #ffffff;
}

[data-theme="dark"] .create-document {
  background: #2d2d2d;
}

[data-theme="dark"] .doc-input {
  background: #3a3a3a;
  border: 1px solid #555;
  color: #ffffff;
}

[data-theme="dark"] .doc-input:focus {
  border-color: #333333;
}

[data-theme="dark"] .create-button {
  background-color: #333333;
  color: #ffffff;
}

[data-theme="dark"] .create-button:hover {
  background-color: #333333;
}

[data-theme="dark"] .empty-state {
  color: #aaaaaa;
}

[data-theme="dark"] .doc-item {
  background: transparent;
}
[data-theme="dark"] .doc-item-container {
  background: #1d1d1d;
}
[data-theme="dark"] .file-icon {
  color: #cccccc;
}

[data-theme="dark"] .doc-title {
  color: #ffffff;
}

[data-theme="dark"] .doc-date {
  color: #aaaaaa;
}

[data-theme="dark"] .edit-icon:hover {
  background: #2d3a2d;
}

[data-theme="dark"] .delete-icon:hover {
  background: #3a2d2d;
}

[data-theme="dark"] .edit-input {
  background: #3a3a3a;
  color: #ffffff;
}

[data-theme="dark"] .project-title {
  color: #ffffff;
}

[data-theme="dark"] .project-title-input {
  background: #3a3a3a;
  color: #ffffff;
  border: 1px solid #555;
}
[data-theme="dark"] .document-list li:hover {
  background: #3a3a3a;
}

[data-theme="dark"] .project-title-input:focus {
  border-color: #007acc;
}

.edit-icon, .delete-icon {
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
  margin-left: 8px;
  flex-shrink: 0;
}

.doc-item-container:hover .edit-icon,
.doc-item-container:hover .delete-icon {
  opacity: 1;
}

.edit-input {
  flex-grow: 1;
  border: none;
  outline: none;
  font-size: inherit;
  background: transparent;
}

.project-title {

  font-size: 2em;
  margin: 20px 0 10px;
  font-weight: 650;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  user-select: none;
}

.project-title-input {
  font-size: 2em;
  margin: 20px 0 0px;
  font-weight: 650;
  padding-bottom: 10.5px;
  border-bottom: 1px solid #eee;
  width: 100%;
  border-top:none;
  border-left: none;
  border-right: none;
  outline: none;
}
</style>