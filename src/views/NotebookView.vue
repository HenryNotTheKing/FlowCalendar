<template>
  <div class="sub-left-panel">
    <SideBar />
  </div>
  <div class="divideline_left"></div>

  <div class="sub-center-panel">
    <EditingPage v-if="useSideBarParams.isShowPage && !useSideBarParams.showDocumentList && !useSideBarParams.isShowProjectCatalog" />
    <DocumentCatalog v-if="(useSideBarParams.isShowPage && useSideBarParams.showDocumentList && !useSideBarParams.isShowProjectCatalog) ||
      useSideBarParams.isShowRecycleBin" :is-recycle-bin="useSideBarParams.isShowRecycleBin"
      @select-document="handleSelectDocument" />
     <ProjectCatalog v-if="useSideBarParams.isShowProjectCatalog" @select-document="handleSelectDocument" />
  </div>


   <div 
    class="divideline-right-wrapper"
    @mouseenter="showHideButton = true" 
    @mouseleave="showHideButton = false"
    v-if="useSideBarParams.isRightPanelVisible"
  >
    <div class="divideline_right"></div>
    <button 
      v-if="showHideButton && useSideBarParams.isRightPanelVisible" 
      class="hide-button" 
      @click="toggleRightPanel"
    >
      <ChevronRight :size="20" />
    </button>
  </div>
  
  <div v-if="useSideBarParams.isRightPanelVisible" class="sub-right-panel">
    <EventList />
  </div>
  
  <div 
    v-if="!useSideBarParams.isRightPanelVisible" 
    class="show-button-container"
    @mouseenter="showShowButton = true"
    @mouseleave="showShowButton = false"
  >
    <button 
      v-if="showShowButton" 
      class="show-button" 
      @click="toggleRightPanel"
    >
      <ChevronLeft :size="20" />
    </button>
  </div>
</template>

<script setup lang="ts">
import EventList from '../component/Notebook/EventList.vue'
import EditingPage from '../component/Notebook/EditingPage.vue'
import SideBar from '../component/Notebook/SideBar.vue'
import DocumentCatalog from '../component/Notebook/DocumentCatalog.vue'
import ProjectCatalog from '../component/Notebook/ProjectCatalog.vue'
import { watch, onMounted, ref } from 'vue'
import { SideBarParams } from '../stores/NoteBook/SideBarParams'
import { ChevronRight, ChevronLeft } from 'lucide-vue-next';

const useSideBarParams = SideBarParams();
import { useRoute } from 'vue-router'
import { DocStore } from '../stores/NoteBook/DocumentStore'


// 控制隐藏按钮显示状态
const showHideButton = ref(false);
// 控制显示按钮显示状态
const showShowButton = ref(false);

// 切换右侧面板显示状态
const toggleRightPanel = () => {
  useSideBarParams.isRightPanelVisible= !useSideBarParams.isRightPanelVisible;
  showHideButton.value = false
  showShowButton.value = false
};

const route = useRoute()
const docStore = DocStore()

// 监听路由变化
watch(() => route.query, (query) => {
  if (query.eventId) {
    const doc = docStore.findDocByEventId(query.eventId as string)
    if (doc) {
      docStore.currentDocId = doc.id
      useSideBarParams.isShowPage = true
      useSideBarParams.showDocumentList = false;
    }
  }else {
    useSideBarParams.resetViews();
    useSideBarParams.showDocumentList= true;
    useSideBarParams.isShowPage = true;
    docStore.initializeDocuments();
  }
}, { immediate: true })

const handleSelectDocument = (docId: string) => {
  docStore.currentDocId = docId;
  useSideBarParams.showDocumentList = false;
}

onMounted(() => {

})
</script>

<style scoped>
.hide-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background: #F9F9F9;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.show-button{
  position: absolute;
  top: 50%;
  left: -12px;
  background: transparent;
  transform: translateY(-50%);
  border: none;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  background: #F9F9F9;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 999;
}
.hide-button {
  right: -12px;
}

.show-button-container {
  position: fixed;
  right: 0;
  top: 0;
  width: 24px;
  height: 100%;
  z-index: 99;
}

.divideline-right-wrapper {
  position: relative;
  width: 10px; /* 增大检测区域 */
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

[data-theme="dark"] .hide-button {
  background: #2d2d2d;
  color: #f0f0f0;
}
[data-theme="dark"] .show-button {
  background: #2d2d2d;
  color: #f0f0f0;
}
</style>