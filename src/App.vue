<template>
  <div>
    <header class="navbar" style="-webkit-app-region: drag">
      <div class = "left-bar"></div>
      <div class = "center-panel"></div>
      <div class = "right-bar">
        <div class="settings-entry" @click="settingsVisible = true" title="设置">
          <Settings :size="18" stroke-width="1.6" />
        </div>
      </div>
    </header>
    <SettingsPanel v-model:visible="settingsVisible" />
    <div class="container">
     <div class="left-panel">
      <div class="button-bar" @click="useChatParams.isChatBoxVisible=false">
        <router-link to = "/" class="btn-gray" @click="docStore.currentDocId = ''"><CalendarDays strokeWidth="1.8" class="icon-change-page"/></router-link>
        <router-link to = "/Notebook" class="btn-gray"><NotebookPen strokeWidth="1.8" class="icon-change-page"/></router-link>
        <router-link to = "/TodoList" class="btn-gray" @click="docStore.currentDocId = ''"><SquareCheckBig strokeWidth="1.9" class="icon-change-page" /></router-link>
      </div>
     </div>
     <div class="center-panel"></div>
     <div class="right-panel"><ChatBox v-if="useChatParams.isChatBoxVisible" />
      <div class="chat-button" :style="{backgroundColor: useThemeStore.theme === 'light' ? '#efefef' : '#2d2d2d'}">
          <img class="icon-send"  
            v-if = "useThemeStore.theme === 'light'"
            src=".\assets\Icons\send.svg" 
            alt="send" 
            @click="useChatParams.isChatBoxVisible ? useChatParams.isChatBoxVisible = false : useChatParams.toggleChatBox()">
          <img class="icon-send"  
            v-else
            src=".\assets\Icons\send-dark.svg" 
            alt="send" 
            @click="useChatParams.isChatBoxVisible ? useChatParams.isChatBoxVisible = false : useChatParams.toggleChatBox()">
      </div>
    </div>
     <div class="sub-container" ><router-view></router-view></div>
    </div>
  </div>

</template>

<script setup>
import ChatBox from './component/ChatBox.vue';
import SettingsPanel from './component/Settings/SettingsPanel.vue';
import { DocStore } from './stores/NoteBook/DocumentStore';
import {onMounted, ref} from 'vue'
import { CalendarDays, SquareCheckBig, NotebookPen, Settings } from 'lucide-vue-next';
import { ThemeStore } from './stores/ThemeStore.ts';

import { ChatParams } from './stores/ChatParams.ts';
import { useRouter } from 'vue-router'
import { SideBarParams } from './stores/NoteBook/SideBarParams';
const docStore = DocStore();
const useChatParams = ChatParams();
const router = useRouter()
router.push('/').catch(err => {
    console.log('Navigation duplicate:', err)
})
const useThemeStore = ThemeStore();
const settingsVisible = ref(false);

useThemeStore.initTheme();

</script>

<style>
.chat-button {
  position: absolute;  
  width: 55px;         
  height: 55px;        
  border-radius: 50%;
  bottom: 40px;      
  right: 30px;       
  z-index: 999;        
  display: flex;       
}

.chat-button.send {
 transform: translateX(20px); 
 transition: all 0.5s ease-in-out;
}
.icon-send {
  rotate: -90deg;
  transform: translateX(-3px) translateY(3px);
  width: 30px;         
  height: 30px;       
  margin: auto;
  transition: transform 0.5s ease;        
}

.icon-send.rotated {
  transform: rotate(90deg);
  transition: transform 0.5s ease;
}
img {
  user-select: none;
}

.right-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  /* 给 Windows 原生最小化/最大化/关闭按钮预留安全区，避免点击/视觉遮挡 */
  padding-right: 150px;
}

.settings-entry {
  -webkit-app-region: no-drag;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 22px;
  border-radius: 4px;
  color: #3d3d3d;
  transition: background-color 0.2s ease;
}

.settings-entry:hover {
  background-color: rgba(0, 0, 0, 0.06);
}

[data-theme="dark"] .settings-entry {
  color: #cccccc;
}

[data-theme="dark"] .settings-entry:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

</style>