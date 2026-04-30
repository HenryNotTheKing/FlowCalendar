<template>
    <div class="document-catalog">
        <!-- 回收站模式 -->
        <template v-if="useSideBarParams.isShowRecycleBin">
            <div v-if="deletedDocuments.length === 0" class="empty-state">
                <h3>回收站为空</h3>
            </div>
            <template v-else>
                <template v-for="yearEntry in sortedDeletedYears" :key="yearEntry[0]">
                    <h1>{{ yearEntry[0] }}年</h1>
                    <template v-for="monthEntry in sortedDeletedMonths(yearEntry[1])" :key="monthEntry[0]">
                        <h2 @click="toggleMonth(yearEntry[0], monthEntry[0])" class="month-header">
                            <ChevronDown :size="20" :class="['collapse-icon', { 'collapsed': isMonthCollapsed(yearEntry[0], monthEntry[0]) }]" />
                            {{ monthEntry[0] }}月
                        </h2>
                        <ul class="document-list" v-show="!isMonthCollapsed(yearEntry[0], monthEntry[0])">
                            <li v-for="doc in sortedDeletedDocs(monthEntry[1])" :key="doc.id" class="doc-item-container">
                                <div class="doc-item">
                                    <FileText :size="16" class="file-icon" color="#666"/>
                                    <span class="doc-title">{{ doc.title }}</span>
                                    <div class="action-buttons">
                                        <RotateCcw :size="16" class="restore-icon" @click.stop="restoreDoc(doc.id)" color="#666"/>
                                        <Trash2 :size="16" class="delete-icon" @click.stop="deleteDoc(doc.id)" color="#666"/>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </template>
                </template>
            </template>
        </template>

        <!-- 正常模式 -->
        <template v-if="useSideBarParams.showDocumentList">
            <!-- 空状态提示 -->
            <div v-if="useProjectParams.projects.find(d => d.id === 'rcwd')?.documents.length === 0" class="empty-state">
                <h3>暂无文档</h3>
                <p>点击日程列表中的事件创建关联文档</p>
            </div>
            <!-- 原有目录结构 -->
            <template v-else>
                <template v-for="yearEntry in sortedYears" :key="yearEntry[0]">
                    <h1>{{ yearEntry[0] }}年</h1>
                    <template v-for="monthEntry in sortedMonths(yearEntry[1])" :key="monthEntry[0]">
                        <h2 @click="toggleMonth(yearEntry[0], monthEntry[0])" class="month-header">
                            <ChevronDown :size="20" :class="['collapse-icon', { 'collapsed': isMonthCollapsed(yearEntry[0], monthEntry[0]) }]" />
                            {{ monthEntry[0] }}月
                        </h2>
                        <ul class="document-list" v-show="!isMonthCollapsed(yearEntry[0], monthEntry[0])">
                            <li v-for="doc in sortedDocs(monthEntry[1])" :key="doc.id" @click="editingDocId === doc.id ? null : handleSelect(doc.id)" class="doc-item-container">
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
                                    <FilePen  :size="16" class="edit-icon" @click.stop="editDocTitle(doc)" color="#666"/>
                                    <Trash2  :size="16" class="delete-icon" @click.stop="deleteDoc(doc.id)" color="#666"/>
                                </div>
                            </li>
                        </ul>
                    </template>
                </template>
            </template>
        </template>
    </div>
</template>

<script setup>
import { computed, ref, onMounted, watch, nextTick } from 'vue'
import { DocStore } from '../../stores/NoteBook/DocumentStore'
import { useRouter } from 'vue-router'
import { FileText, Trash2, RotateCcw, ChevronDown, FilePen} from 'lucide-vue-next'
import { SideBarParams } from '../../stores/NoteBook/SideBarParams.ts';
import { ProjectParams } from '../../stores/NoteBook/ProjectParams.ts';
const useProjectParams = ProjectParams()
const useSideBarParams = SideBarParams();
const router = useRouter()
const docStore = DocStore()

const grouped = computed(() => docStore.getGroupedDocuments())

const sortedYears = computed(() => 
  Object.entries(grouped.value).sort((a, b) => Number(a[0]) - Number(b[0]))
)

const sortedMonths = (months) => 
  Object.entries(months).sort((a, b) => Number(a[0]) - Number(b[0]))

const sortedDocs = (docs) => 
  [...docs].sort((a, b) => 
    new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  )

const handleSelect = (docId) => {
  docStore.currentDocId = docId;
  useSideBarParams.resetViews();
  useSideBarParams.isShowPage = true;
  docStore.docChanged = !docStore.docChanged;
}

// 添加回收站模式判断
const deletedDocuments = computed(() => docStore.deletedDocuments);

// 添加操作方法
const deleteDoc = (docId) => {
  if(useSideBarParams.isShowRecycleBin) {
    docStore.permanentDelete(docId);
  } else {
    docStore.deleteDocument(docId);
  }
}

const restoreDoc = (docId) => {
  docStore.restoreDocument(docId);
}

// 为回收站文档添加分组和排序功能
const groupedDeletedDocuments = computed(() => {
  const grouped = {};
  deletedDocuments.value.forEach(doc => {
    const date = new Date(doc.createdAt);
    const year = date.getFullYear();
    const month = date.getMonth() + 1; // 月份从0开始，需要+1
    
    if (!grouped[year]) {
      grouped[year] = {};
    }
    if (!grouped[year][month]) {
      grouped[year][month] = [];
    }
    grouped[year][month].push(doc);
  });
  return grouped;
});

const sortedDeletedYears = computed(() => 
  Object.entries(groupedDeletedDocuments.value).sort((a, b) => Number(a[0]) - Number(b[0]))
)

const sortedDeletedMonths = (months) => 
  Object.entries(months).sort((a, b) => Number(a[0]) - Number(b[0]))

const sortedDeletedDocs = (docs) => 
  [...docs].sort((a, b) => 
    new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  )

// 添加折叠功能
const collapsedMonths = ref({});

// 从localStorage加载折叠状态
const loadCollapsedState = () => {
  const savedState = localStorage.getItem('documentCatalogCollapsedState');
  if (savedState) {
    collapsedMonths.value = JSON.parse(savedState);
  }
};

// 保存折叠状态到localStorage
const saveCollapsedState = () => {
  localStorage.setItem('documentCatalogCollapsedState', JSON.stringify(collapsedMonths.value));
};

// 在组件挂载时加载折叠状态
onMounted(() => {
  loadCollapsedState();
});

// 监听折叠状态变化并保存到localStorage
watch(collapsedMonths, () => {
  saveCollapsedState();
}, { deep: true });

const toggleMonth = (year, month) => {
  const key = `${year}-${month}`;
  collapsedMonths.value[key] = !collapsedMonths.value[key];
};

const isMonthCollapsed = (year, month) => {
  const key = `${year}-${month}`;
  return !!collapsedMonths.value[key];
};

// 编辑文档标题相关
const editingDocId = ref(null);

const editDocTitle = (doc) => {

  editingDocId.value = doc.id;
  docStore.currentDocId = doc.id;
  nextTick(() => {
    // 通过DOM查询获取正确的输入框元素
    const inputElement = document.querySelector(`input[data-doc-id="${doc.id}"]`);
    if (inputElement) {
      inputElement.focus();
      // 使用 setSelectionRange 确保文本被选中
      inputElement.setSelectionRange(0, inputElement.value.length);
    }
  });
};

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

// 格式化日期为 MM-DD 格式
const formatDate = (dateString) => {
  const date = new Date(dateString);
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  return `${month}-${day}`;
};
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.empty-state h3 {
  margin-bottom: 16px;
  font-size: 1.2em;
}

.empty-state button {
  margin-top: 20px;
  padding: 8px 16px;
  background-color: #0a84ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.empty-state button:hover {
  background-color: #007aff;
}

/* 保持原有样式不变 */
.document-catalog {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.doc-item-container {
  padding: 0px 8px;
  cursor: pointer;
  border-radius: 4px;
}

.file-icon {
  margin-right: 12px;
  color: #666;
}

.doc-title {
  user-select: none;
  flex-grow: 1;
  margin-right: 10px;
}

.delete-icon {
  cursor: pointer;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.doc-item-container:hover .delete-icon {
  opacity: 1;
}

.delete-icon:hover {
  background: #ffeceb;
}

.restore-icon {
  cursor: pointer;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  margin-right: 8px;
}

.doc-item-container:hover .restore-icon {
  opacity: 1;
}

.restore-icon:hover {
  background: #e8f5e9;
}

h1 {
  font-size: 2em;
  margin: 20px 0 10px;
  font-weight: 650;
}

h2 {
  font-size: 1.5em;
  margin: 15px 0 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.month-header {
  user-select: none;
}

.collapse-icon {
  transition: transform 0.2s;
  margin-right: 8px;
  margin-top: 4px;
}

.collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.document-list {
  list-style: none;
  padding: 0;
  margin: 0 0 20px 15px;
}

.document-list li {
  padding: 0px 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.document-list li:hover {
  background: #f0f0f0;
}

/* 添加回收站样式 */
.recycle-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.doc-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.2s;
}


.file-icon {
  margin-right: 10px;
  color: #666;
}

.delete-icon {
  margin-left: auto;
  cursor: pointer;
  color: #ff3b30;
}

.edit-icon {
  cursor: pointer;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  margin-right: 8px;
}

.doc-item-container:hover .edit-icon {
  opacity: 1;
}

.edit-icon:hover {
  background: #e8f5e9;
}

.action-buttons {
  margin-left: auto;
  display: flex;
  gap: 4px;
}

.restore-btn {
  background: #0a84ff;
  color: white;
  padding: 4px 8px;
  margin-right: 8px;
}

.delete-btn {
  background: #ff3b30;
  color: white;
  padding: 4px 8px;
}

/* 添加编辑输入框样式 */
.edit-input {
  flex-grow: 1;
  border: none;
  outline: none;
  font-size: inherit;
  background: transparent;
}

/* 添加文档日期样式 */
.doc-date {
  color: #999;
  font-size: 0.9em;
  margin-right: 10px;
  margin-left: auto;
}

/* 暗色主题样式 */
[data-theme="dark"] .document-catalog {
  background-color: #1e1e1e;
  color: #ffffff;
}

[data-theme="dark"] .empty-state {
  color: #aaaaaa;
}

[data-theme="dark"] .doc-item {
  background: transparent;
}

[data-theme="dark"] .file-icon {
  color: #cccccc;
}

[data-theme="dark"] .doc-title {
  color: #ffffff;
}

[data-theme="dark"] .delete-icon:hover {
  background: #3a2d2d;
}

[data-theme="dark"] .restore-icon:hover {
  background: #2d3a2d;
}

[data-theme="dark"] h1 {
  color: #ffffff;
}

[data-theme="dark"] h2 {
  color: #ffffff;
}

[data-theme="dark"] .month-header {
  color: #ffffff;
}

[data-theme="dark"] .document-list li:hover {
  background: #3a3a3a;
}

[data-theme="dark"] .edit-icon:hover {
  background: #2d3a2d;
}

[data-theme="dark"] .edit-input {
  background: #3a3a3a;
  color: #ffffff;
}

[data-theme="dark"] .doc-date {
  color: #aaaaaa;
}
</style>