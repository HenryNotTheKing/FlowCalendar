<template>
  <div class="file-sidebar">
    <!-- Overviews 部分 -->
    <div class="section fixed-overviews">
      <div class="section-title">总览</div>
      <ul class="section-list">
        <div @click=showPage() :class="{ 'active-item': useSideBarParams.isShowPage && !useSideBarParams.isShowProjectCatalog && useProjectParams.activeProjectId === 'rcwd' }">
          <FilePen :size="20" color="gray" strokeWidth="1.5" />
          <span class="label"> 日常文档</span>
        </div>
        <div @click="showRecycleBin" :class="{ 'active-item': useSideBarParams.isShowRecycleBin }">
          <Trash2 :size="20" color="gray" strokeWidth="1.5" />
          <span class="label"> 回收站</span>
        </div>
        <div @click="toggleSearch" class="search-toggle">
          <Search :size="20" color="gray" strokeWidth="1.5" />
          <span class="label"> 搜索文档</span>
        </div>
        <div @click="useDocStore.updateDatabase" class="search-toggle">
          <Upload :size="20" color="gray" strokeWidth="1.5" />
          <span class="label"> 更新知识库 </span>
          <Loader :size="20" color="gray" strokeWidth="1.5" class="loading-icon" v-if="useDocStore.isLoading"/>
        </div>
      </ul>
    </div>

    <!-- 搜索框弹出对话框 -->
    <div v-if="useSideBarParams.isShowSearchBox" class="search-overlay" @click="toggleSearch">
      <div class="search-dialog" @click.stop>
        <div class="search-input-container">
          <Search :size="16" color="gray" class="search-icon" />
          <input 
            v-model="searchQuery" 
            @input="performSearch" 
            placeholder="输入关键词搜索文档" 
            class="search-input"
            ref="searchInput"
          />
        </div>
        <ul v-if="searchResults.length > 0" class="search-results">
          <div 
            v-for="doc in searchResults" 
            :key="doc.id" 
            class="search-result-item"
          >
            <FileText :size="16" color="gray" class="result-icon" />
            <div class="result-content" @click="openDocument(doc.id)">
              <div class="result-title">{{ doc.title }}</div>
              <div v-if="doc.snippet" class="result-snippet" v-html="doc.snippet"></div>
            </div>
            <Trash2 :size="16" color="gray" class="delete-icon" @click.stop="deleteDocument(doc.id)" />
          </div>
        </ul>
        <div v-else-if="searchQuery.length > 0" class="no-results">
          未找到匹配的文档
        </div>
      </div>
    </div>

    <!-- Projects 部分 -->
    <div class="scrollable-projects">
      <div 
        class="section-title"
        @mouseover="showAddProjectIcon = true" 
        @mouseleave="showAddProjectIcon = false"
        @click="addNewProject"
      >
        我的项目
        <Plus 
          v-if="showAddProjectIcon" 
          :size="16" 
          color="gray" 
          class="add-project-icon" 
        />
      </div>
      <div class="project-list">
        <template v-for="project in projects.filter(p => !projects.some(pp => pp.projects.includes(p.id)) && p.id !== 'rcwd')" :key="project.id">
          <div 
            :class="{ 'active-item': project.id === useProjectParams.activeProjectId }"
            class="project-item"
            @click="selectProject(project.id)"
            @mouseover="showAddIcon[project.id] = true" 
            @mouseleave="showAddIcon[project.id] = false"
          >
            <ChevronRight 
              v-if="getSubProjects(project.id).length > 0 && showAddIcon[project.id] && project.projects.length > 0"

              :size="16" 
              strokeWidth="2"
              color="gray" 
              class="expand-icon" 
              :class="{ 'expanded': expandedProjects[project.id] }"
              @click.stop="toggleProjectExpansion(project.id)"
            />
            <Folder :size="16" color="gray" class="project-icon" v-if="!showAddIcon[project.id] || project.projects.length === 0"/>
            <span class="label">{{ project.name }}</span>
            
            <Plus 
              v-if="showAddIcon[project.id] && getProjectDepth(project) < 2"
              :size="17" 
              color="gray" 
              class="add-Project-icon" 
              @click.stop="addSubProject(project.id),toggleProjectExpansion(project.id)"
            />
            <Trash2 :size="17" color="gray" class="delete-icon" @click.stop="deleteProject(project.id)" />
          </div>
          <!-- 子项目 -->
          <div v-if="expandedProjects[project.id]" class="sub-projects">
            <template v-for="subProject in getSubProjects(project.id)" :key="subProject.id">
              <div 
                :class="{ 'active-item': subProject.id === useProjectParams.activeProjectId }"
                class="project-item sub-project-item"
                @click="selectProject(subProject.id)"
                @mouseover="showAddIcon[subProject.id] = true" 
                @mouseleave="showAddIcon[subProject.id] = false"
              >
                <ChevronRight 
                  v-if="getSubProjects(subProject.id).length > 0 && showAddIcon[subProject.id] && subProject.projects.length > 0"
                  :size="16" 
                  color="gray" 
                  class="expand-icon" 
                  :class="{ 'expanded': expandedProjects[subProject.id] }"
                  @click.stop="toggleProjectExpansion(subProject.id)"
                />
                <Folder :size="16" color="gray" class="project-icon" v-if="!showAddIcon[subProject.id] || subProject.projects.length === 0"/>

                <span class="label">{{ subProject.name }}</span>
                <Plus 
                  v-if="showAddIcon[subProject.id] && getProjectDepth(subProject) < 2"
                  :size="17" 
                  color="gray" 
                  class="add-Project-icon" 
                  @click.stop="addSubProject(subProject.id)"
                />
                <Trash2 :size="17" color="gray" class="delete-icon" @click.stop="deleteProject(subProject.id)" />
              </div>
              <!-- 子项目的子项目 -->
              <div v-if="expandedProjects[subProject.id]" class="sub-projects">
                <div 
                  v-for="subSubProject in getSubProjects(subProject.id)" 
                  :key="subSubProject.id"
                  :class="{ 'active-item': subSubProject.id === useProjectParams.activeProjectId }"
                  class="project-item sub-project-item"
                  @click="selectProject(subSubProject.id)"
                  @mouseover="showAddIcon[subSubProject.id] = true" 
                  @mouseleave="showAddIcon[subSubProject.id] = false"
                >
                  <Folder :size="16" color="gray" class="project-icon" />
                  <span class="label">{{ subSubProject.name }}</span>
                  <Trash2 :size="17" color="gray" class="delete-icon" @click.stop="deleteProject(subSubProject.id)" />
                </div>
              </div>
            </template>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'; 
import { SideBarParams } from '../../stores/NoteBook/SideBarParams.ts';
import { ProjectParams } from '../../stores/NoteBook/ProjectParams.ts';
import { LayoutList, FilePen, Trash2, Search, FileText, Plus, Folder, ChevronRight, Upload, UploadCloud, Loader } from 'lucide-vue-next'
const useSideBarParams = SideBarParams();
const useProjectParams = ProjectParams();

// 搜索功能相关
const searchQuery = ref('');
const searchInput = ref(null);

// 执行搜索
const performSearch = () => {
  // 搜索会在computed属性searchResults中自动执行
  console.log('执行搜索:', searchQuery.value);
}

// 项目管理相关
const showAddProjectIcon = ref(false);
const showAddIcon = ref({}); // 用于跟踪每个项目是否显示添加图标
const expandedProjects = ref({}); // 用于跟踪项目是否展开
const projects = computed(() => useProjectParams.projects);

// 获取子项目
const getSubProjects = (projectId) => {
  return useProjectParams.getSubProjects(projectId);
};

// 获取项目深度
const getProjectDepth = (project) => {
  let depth = 0;
  let currentProject = project;
  
  while (currentProject) {
    // 检查当前项目是否是另一个项目的子项目
    let parentFound = false;
    for (const p of projects.value) {
      if (p.projects.includes(currentProject.id)) {
        currentProject = p;
        depth++;
        parentFound = true;
        break;
      }
    }
    
    if (!parentFound) {
      break;
    }
    
    // 限制最大深度为2
    if (depth >= 2) {
      break;
    }
  }
  
  return depth;
};

// 切换项目展开状态
const toggleProjectExpansion = (projectId) => {
  expandedProjects.value[projectId] = !expandedProjects.value[projectId];
};

// 添加子项目
const addSubProject = async (projectId) => {
  const parentProject = projects.value.find(p => p.id === projectId);
  if (parentProject) {
    const newProjectName = '新项目';
    const newProject = await useProjectParams.createProject(newProjectName);
    await useProjectParams.addProjectToProject(projectId, newProject);
  }
};

const showPage = () => {
  useDocStore.currentDocId = ''
  useSideBarParams.resetViews();
  useSideBarParams.isShowPage = true;
  useSideBarParams.showDocumentList = true;
}

const showRecycleBin = () => {
  useDocStore.currentDocId = ''
  useSideBarParams.resetViews();
  useSideBarParams.isShowRecycleBin = true;
}

// 切换搜索框显示
const toggleSearch = () => {
  useSideBarParams.isShowSearchBox = !useSideBarParams.isShowSearchBox;
  searchQuery.value = '';
  
  // 延迟聚焦到输入框
  if (useSideBarParams.isShowSearchBox) {
    setTimeout(() => {
      if (searchInput.value) {
        searchInput.value.focus();
      }
    }, 100);
  }
};

// 添加新项目
async function addNewProject(){ 
  await useProjectParams.createProject('新项目');
  selectProject(useProjectParams.projects[useProjectParams.projects.length - 1].id);
};

const selectProject = (projectId) => {
  useDocStore.currentDocId = ''
  useProjectParams.activeProjectId = projectId;
  useSideBarParams.resetViews();
  useSideBarParams.isShowProjectCatalog = true;
};

const deleteProject = (projectId) => {
  useProjectParams.deleteProject(projectId);
  // 如果删除的是当前激活的项目，重置视图
  if (useSideBarParams.currentProjectId === projectId) {
    useSideBarParams.resetViews();
    useSideBarParams.isShowPage = true;
    useSideBarParams.showDocumentList = true;
  }
};

// 在项目中创建新文档
const createDocumentInProject = (projectId) => {
  const newDoc = useDocStore.createDocument('新文档');
  useProjectParams.addDocumentToProject(projectId, newDoc.id);
  useDocStore.currentDocId = newDoc.id;
  useSideBarParams.setCurrentProject(projectId);
  useSideBarParams.isShowPage = true;
};

import { DocStore } from '../../stores/NoteBook/DocumentStore'
import { UPDATE_MODEL_EVENT } from 'element-plus';

const useDocStore = DocStore()

// 搜索结果
const searchResults = ref([]);

// 监听搜索查询变化并执行搜索
watch(searchQuery, async (newQuery) => {
  if (newQuery.trim()) {
    searchResults.value = await useDocStore.searchDocuments(newQuery);
  } else {
    searchResults.value = [];
  }
});


// 打开文档
const openDocument = async (docId) => {
  DocStore.docChanged = !DocStore.docChanged
  useSideBarParams.resetViews();
  useSideBarParams.isShowPage = true
  useDocStore.currentDocId = docId
  // 添加滚动到当前文档的逻辑
  await nextTick()
  const activeItem = document.querySelector('.active-item')
  if (activeItem) {
    activeItem.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
  
  // 关闭搜索框
  useSideBarParams.isShowSearchBox = false;
  searchQuery.value = '';
}

// 删除文档
const deleteDocument = (docId) => {
  useDocStore.deleteDocument(docId);
}


onMounted(() => {
  useProjectParams.fetchProjects()
  useProjectParams.activeProjectId = 'rcwd'
  setTimeout(() => {
    if(!useSideBarParams.isShowPage){useSideBarParams.showDocumentList = true}
  }, 5)
})
</script>

<style scoped>
.file-sidebar {
  width: 250px;
  padding: 16px;
  font-family: -apple-system;
  height: 100vh;
  overflow-y: auto;
  box-sizing: border-box;
}

.section {
  margin-bottom: 24px;
}
.fixed-overviews {
  flex-shrink: 0;
  margin-bottom: 24px;
  border-bottom: 1px solid #e0e0e0; /* 淡灰色分割线 */
  padding-bottom: 16px;
}
.section-title {
  font-weight: 600;
  color: #8a8c8fdd; /* 中灰色 */
  padding: 4px 12px;
  font-weight: 500;
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  user-select: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.section-title:hover {
  color: #555555;
  background-color: #ececec;
}

.section-list {
  list-style: none;
  padding: 4px 6px;
  margin: 0;
}

.section-list div {
  display: flex;
  align-items: center;
  font-weight: 400;
  padding: 4px 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.section-list div:hover {
  background-color: #eeeeee;
}

.section-list span{
  transform: translateX(-3px);
}

.active-item {
  background-color: #eae9e9e7; /* 高亮背景色 */
  font-weight: 500;
}

.icon {
  margin-right: 10px;
  font-size: 16px;
  opacity: 0.7;
}

.active-item .icon {
  opacity: 1;
}

.label {
  flex-grow: 1;
  user-select: none;
}

.add-project-icon {
  transition: transform 0.2s ease;
}

.project-item .add-Project-icon {
  position:relative;
  left: -10px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.project-item:hover .add-Project-icon {
  opacity: 0.7;
}
.project-item:hover .add-Project-icon:hover {
  opacity: 1;
}

.expand-icon {
  position: relative;
  left: 4px;
  transition: all 0.2s ease;
  cursor: pointer;
  opacity: 0.7;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.expand-icon:hover {
  opacity: 1;
}

.project-list {
  display: flex;
  flex-direction: column;
  font-weight: 400;
  padding: 4px 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}


 .sub-project-item {
  padding-left: 0px;
  width: 100%;
  padding: 0px;
}

.sub-projects > .sub-project-item {
  width: 100%;
  padding-left: 15px;
}

.sub-projects > .sub-projects > .sub-project-item {
  width: 100%;
  padding-left: 30px;
}

.project-icon {
  position: relative;
  left: 2px;
  margin-right: 0px;
  font-size: 16px;
  opacity: 0.7;
  flex-shrink: 0;
}
.project-item {
  border-radius: 4px;
  padding: 2px 6px 2px 7px;
  margin-top: 2px;
  margin-bottom: 2px;
  width: 100%;
  display: flex;
  align-items: center;
}
.project-item:hover{
  background-color: #eeeeee;
}
.project-item .delete-icon {
  position:relative;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.project-item:hover .delete-icon {
  opacity: 0.7;
}
.project-item:hover .delete-icon:hover {
  opacity: 1;
}

.label {
  position:relative;
  left:10px;
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 搜索框弹出对话框样式 */
.search-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 15vh; /* 从顶部向下偏移15%视口高度 */
  z-index: 1000;
}

.search-dialog {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  width: 60%;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-top: 0px; /* 与顶部保持一定距离 */
}

.search-input-container {
  display: flex;
  align-items: center;
  background-color: #f5f5f5;
  border-radius: 6px;
  padding: 6px 10px;
}

.search-icon {
  margin-right: 6px;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
}

.search-results {
  list-style: none;
  padding: 0;
  margin: 10px 0 0 0;
  max-height: 300px;
  overflow-y: auto;
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-result-item:hover {
  background-color: #eeeeee;
}

.result-icon {
  margin-right: 8px;
  flex-shrink: 0;
}

.search-result-item .delete-icon {
  margin-left: 8px;
  flex-shrink: 0;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.search-result-item:hover .delete-icon {
  opacity: 0.7;
}

.search-result-item .delete-icon:hover {
  opacity: 1;
}

.result-content {
  flex-grow: 1;
  min-width: 0;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.result-title {
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-shrink: 0;
}

.result-snippet {
  font-size: 12px;
  color: #949494;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: right;
  margin-left: 10px;
}

.result-snippet strong {
  color: #000000;
  font-weight: normal;
}

.no-results {
  text-align: center;
  padding: 12px;
  color: #888;
  font-size: 14px;
}

.scrollable-projects {
  flex-grow: 1;
  overflow-y: auto;
  margin-bottom: 24px;
}

/* 暗色主题样式 */
[data-theme="dark"] .file-sidebar {
  background-color: #252526;
  color: #ffffff;
}

[data-theme="dark"] .section {
  border-bottom: 1px solid #333;
}

[data-theme="dark"] .fixed-overviews {
  border-bottom: 1px solid #484848;
}

[data-theme="dark"] .section-title {
  color: #cccccc;
}

[data-theme="dark"] .section-title:hover {
  color: #ffffff;
  background-color: #333333;
}

[data-theme="dark"] .section-list div:hover {
  background-color: #333333;
}

[data-theme="dark"] .active-item {
  background-color: #333333;
  color: #ffffff;
}

[data-theme="dark"] .active-item .icon,
[data-theme="dark"] .active-item .label {
  color: #ffffff;
}

[data-theme="dark"] .icon,
[data-theme="dark"] .label {
  color: #cccccc;
}

[data-theme="dark"] .project-item:hover {
  background-color: #333333;
}

[data-theme="dark"] .project-item .delete-icon:hover {
  opacity: 1;
}

[data-theme="dark"] .project-item:hover .delete-icon {
  opacity: 0.7;
}

[data-theme="dark"] .project-item:hover .add-Project-icon {
  opacity: 0.7;
}

[data-theme="dark"] .project-item:hover .add-Project-icon:hover {
  opacity: 1;
}

[data-theme="dark"] .search-overlay {
  background-color: rgba(30, 30, 30, 0.8);
}

[data-theme="dark"] .search-dialog {
  background-color: #2d2d2d;
}

[data-theme="dark"] .search-input-container {
  background-color: #3a3a3a;
  border: 1px solid #555;
}

[data-theme="dark"] .search-input {
  background-color: #3a3a3a;
  color: #ffffff;
}

[data-theme="dark"] .search-input:focus {
  border-color: #007acc;
}

[data-theme="dark"] .search-results {
  background-color: #2d2d2d;
}

[data-theme="dark"] .search-result-item {
  color: #ffffff;
  border-bottom: 1px solid #444;
}

[data-theme="dark"] .search-result-item:hover {
  background-color: #3a3a3a;
}

[data-theme="dark"] .search-result-item .delete-icon:hover {
  opacity: 1;
}

[data-theme="dark"] .search-result-item:hover .delete-icon {
  opacity: 0.7;
}

[data-theme="dark"] .result-snippet {
  color: #aaaaaa;
}

[data-theme="dark"] .result-snippet strong {
  color: #ffffff;
}

[data-theme="dark"] .no-results {
  color: #aaaaaa;
}
.loading-icon {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>