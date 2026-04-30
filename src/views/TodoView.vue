<template>
  <div class="sub-left-panel">
    <SideBar />
  </div>
  <div class="divideline_left"></div>

  <div class="sub-center-panel">
    <TodoList v-if="!useTodoSideBarParams.isShowMyProject" />
    <MyProject v-else />
  </div>


  <div class="divideline_right"></div>
  <div class="sub-right-panel">
    <EventList />
  </div>
</template>

<script setup lang="ts">
import { TodoSideBarParams } from '../stores/TodoList/TodoSideBarParams.ts';
import SideBar from '../component/Todolist/SideBar.vue'
import TodoList from '../component/Todolist/TodoList.vue'
import EventList from '../component/Todolist/EventList.vue'
import MyProject from '../component/Todolist/MyProject.vue'

const useTodoSideBarParams = TodoSideBarParams();

</script>

<style scoped>

</style>