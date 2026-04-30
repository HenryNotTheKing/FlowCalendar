<template>
  <div class="file-sidebar">
    <!-- Overviews 部分 -->
    <div class="section fixed-overviews" @click="useTodoSideBarParams.isShowMyProject = false">
      <div class="section-title">总览</div>
      <ul class="section-list">
        <div @click=showToday() :class="{ 'active-item': useTodoSideBarParams.isShowToday }">
          <LayoutList :size="20" color="gray" strokeWidth="1.5" />
          <span class="label"> 今日待办</span>
        </div>
        <div @click=showCompleted() :class="{ 'active-item': useTodoSideBarParams.isShowCompleted }">
          <ListChecks :size="21" color="gray" strokeWidth="1.6" />
          <span class="label"> 已完成</span>
        </div>
        <div @click="showAll()" :class="{ 'active-item': useTodoSideBarParams.isShowAll }">
          <Logs :size="20" color="gray" strokeWidth="1.7" />
          <span class="label"> 所有代办</span>
        </div>
      </ul>
    </div>

    <!-- 搜索框弹出对话框 -->
    <div v-if="useTodoSideBarParams.isShowSearchBox" class="search-overlay" @click="toggleSearch">
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
      <ul class="section-list">
        <div 
          v-for="project in projects.filter(p => p.id !== 'daily_todos')" 
          :key="project.id"
          :class="{ 'active-item': project.id === useProjectStore.activeProjectId }"
          class="project-item"
          @click="selectProject(project.id)"
        >
          <FileText :size="16" color="gray" class="project-icon" />
          <span class="label">{{ project.name }}</span>
          <Trash2 v-if="project.id !== 'daily_todos'" :size="17" color="gray" class="delete-icon" @click.stop="deleteProject(project.id)" />
        </div>
      </ul>
    </div>
  
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { TodoSideBarParams } from '../../stores/TodoList/TodoSideBarParams';
import { ProjectParams } from '../../stores/TodoList/ProjectParams.ts';
import { LayoutList, ListChecks, Logs, Plus, FileText, Search, Trash2 } from 'lucide-vue-next'
import { TodoApi } from '../../stores/TodoList/TodoAPI.ts';
const useTodoSideBarParams = TodoSideBarParams();
const useProjectStore = ProjectParams();
const api = TodoApi();
// 搜索功能相关
const searchQuery = ref('');
const searchInput = ref(null);

// 项目功能相关=
const showAddProjectIcon = ref(false);
const projects = computed(() => useProjectStore.projects);

const showToday = () => {
  useTodoSideBarParams.resetViews();
  useProjectStore.activeProjectId = 'daily_todos';
  useTodoSideBarParams.isShowToday = true;
}

const showCompleted = () => {
  useTodoSideBarParams.resetViews();
  useProjectStore.activeProjectId = 'daily_todos';
  useTodoSideBarParams.isShowCompleted = true;
}

const showAll = () => {
  useTodoSideBarParams.resetViews();
  useProjectStore.activeProjectId = 'daily_todos';  
  useTodoSideBarParams.isShowAll = true;
}

const addNewProject = () => {
  useProjectStore.addProject('新项目');
  api.projectAPI.createProject('新项目');
  selectProject(useProjectStore.projects[useProjectStore.projects.length - 1].id);
}

const selectProject = (id) => {
  useTodoSideBarParams.isDisableTransition = true;
  useProjectStore.activeProjectId = id;
  useTodoSideBarParams.resetViews();
  useTodoSideBarParams.isShowMyProject = true;

  // 在下一个tick重置过渡动画状态
  setTimeout(() => {
    useTodoSideBarParams.isDisableTransition = false;
  }, 0);
}

const deleteProject = (id) => {
  useProjectStore.removeProject(id);
  api.projectAPI.deleteProject(id);

}

onMounted(() => {
  // 项目数据现在通过Pinia store管理，无需手动加载
});
</script>

<style scoped>
.file-sidebar {
  width: 250px;
  padding: 16px;
  font-family: -apple-system;
  height: 100vh;
  overflow-y: hidden;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.fixed-overviews {
  flex-shrink: 0;
  margin-bottom: 24px;
  border-bottom: 1px solid #e0e0e0; /* 淡灰色分割线 */
  padding-bottom: 16px;
}

.scrollable-projects {
  flex-grow: 1;
  overflow-y: auto;
  margin-bottom: 24px;
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
  background-color: #eeeeee; /* 悬停效果 */
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
  position:relative;
  left:7px;
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  user-select: none;
}

.add-project-icon {
  margin-left: auto;
  transition: transform 0.2s ease;
}

.project-icon {
  margin-right: 4px;
  font-size: 16px;
  opacity: 0.7;
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

.project-item .delete-icon {
  position:relative;
  left:110px;
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

[data-theme="dark"] .fixed-overviews {
  border-bottom: 1px solid #484848;
}
/* 暗色主题样式 */
[data-theme="dark"] .file-sidebar {
  background-color: #252526;
  color: #ffffff;
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
}
[data-theme="dark"] .active-item .label{
  color: #ffffff;
}
[data-theme="dark"] .label {
  color: #cccccc;
}

[data-theme="dark"] .search-overlay {
  background-color: rgba(0, 0, 0, 0.7);
}

[data-theme="dark"] .search-dialog {
  background-color: #2d2d2d;
  color: #ffffff;
}

[data-theme="dark"] .search-input-container {
  background-color: #3c3c3c;
}

[data-theme="dark"] .search-input {
  color: #ffffff;
}

[data-theme="dark"] .search-result-item:hover {
  background-color: #333333;
}

[data-theme="dark"] .result-title {
  color: #ffffff;
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

[data-theme="dark"] .project-item:hover .delete-icon {
  opacity: 0.7;
}

[data-theme="dark"] .project-item:hover .delete-icon:hover {
  opacity: 1;
}
</style>