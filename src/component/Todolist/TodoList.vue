<template>
  <div class="todo-app">
    <!-- 顶部标题区 -->
    <div v-if="useTodoSideBarParams.isShowToday">
      <div class="header">
        <div class="today-title">今天</div>
      </div>

      <!-- 未完成任务列表 -->
      <div class="tasks-list">
        <transition-group name="task" tag="div"
          :css="useTodoSideBarParams.isDisableTransition || useEditParams.isAdding ? false : true">
          <div v-for="(task, index) in useTodoList.TodayIncompletedTasks" :key="task.id || index" class="task-item"
            :class="{ 'completed': task.completionTimer, 'fade-out': task.fadeOut, 'fade-in': task.fadeIn }">
            <div class="checkbox" @click="completeTask(task)" :style="{ borderColor: getPriorityColor(task.priority) }">
              <div :class="{ 'checkmark': task.completionTimer }"
                :style="{ 'background-color': getPriorityColor(task.priority) }"></div>
            </div>
            <div class="task-content" @click="completeTask(task)">
              <div class="task-title">
                {{ task.title }}
              </div>
              <div class="task-meta">
                <div class="icon">
                  <SquarePen :size="20" color="gray" strokeWidth="1.5" class="hidden-icon"
                    @mousedown.prevent="useEditParams.openEditModal(task)" />
                  <Trash2 :size="20" color="gray" strokeWidth="1.5" @mousedown.prevent="useTodoList.deleteTask(task.id)"
                    class="hidden-icon" />
                </div>
                <div v-if="task.date" class="task-time">{{ formatTimeTo24Hour(task.date) }}</div>
                <div v-if="task.tag" class="task-tag"
                  :style="{ backgroundColor: useProjectParams.projects.find(p => p.id === 'daily_todos')?.tags.find(t => t.name === task.tag)?.color || '#e0e0e0' }">
                  {{ "#" + task.tag }}
                </div>
              </div>
            </div>
          </div>
          <!-- 新增添加入口 -->
          <div class="task-item add-task-item" @click="startAdding" v-if="!useEditParams.isAdding">
            <div class="checkbox placeholder-checkbox">
              <div class="checkmark"></div>
            </div>
            <div class="task-content">
              <div class="task-title placeholder-title">
                添加新待办
              </div>
            </div>
          </div>
        </transition-group>
        <!-- 编辑状态 -->
        <div class="task-item editing-task" v-if="useEditParams.isAdding">
          <div class="checkbox">
            <div class="checkmark"></div>
          </div>
          <input ref="inputRef" v-model="newTask.title" class="task-input" @blur="finishAdding"
            @keyup.enter="handleEnter">
          <div class="edit" @mousedown.prevent="useEditParams.openEditModal(newTask)">
            <Settings2 :size="20" color="gray" strokeWidth="1.5" class="hidden-icon" />
          </div>
        </div>
      </div>
    </div>

    <!-- 已完成任务列表 -->
    <div class="completed-tasks-section" v-if="useTodoSideBarParams.isShowCompleted">
      <div class="header">
        <div class="today-title">今日完成</div>
      </div>
      <div v-if="useTodoList.TodayCompletedTasks.length === 0" class="no-tasks-message">
        今天没有已完成的任务
      </div>
      <div class="tasks-list">
        <transition-group name="task" tag="div" :css="useTodoSideBarParams.isDisableTransition ? false : true">
          <div v-for="(task, index) in useTodoList.TodayCompletedTasks" :key="task.id || 'completed-' + index"
            class="task-item completed-task-item" :class="{ 'fade-out': task.fadeOut, 'fade-in': task.fadeIn }">
            <div class="checkbox" @click="incompleteTask(task)"
              :style="{ borderColor: getPriorityColor(task.priority) }">
              <div class="checkmark" :style="{ 'background-color': getPriorityColor(task.priority) }"></div>
            </div>
            <div class="task-content" @click="incompleteTask(task)">
              <div class="task-title">
                {{ task.title }}
              </div>
              <div class="task-meta">
                <div class="icon">
                  <SquarePen :size="20" color="gray" strokeWidth="1.5" class="hidden-icon"
                    @mousedown.prevent="useEditParams.openEditModal(task)" />
                  <Trash2 :size="20" color="gray" strokeWidth="1.5" @mousedown.prevent="useTodoList.deleteTask(task.id)"
                    class="hidden-icon" />
                </div>
                <div v-if="task.date" class="task-time">{{ formatTimeTo24Hour(task.date) }}</div>
                <div v-if="task.tag" class="task-tag"
                  :style="{ backgroundColor: useProjectParams.projects.find(p => p.id === 'daily_todos')?.tags.find(t => t.name === task.tag)?.color || '#e0e0e0' }">
                  {{ "#" + task.tag }}
                </div>
              </div>
            </div>

          </div>
        </transition-group>
      </div>

    </div>

    <!-- 所有任务列表 -->
    <div v-if="useTodoSideBarParams.isShowAll">
      <div class="header">
        <div class="today-title">所有待办</div>
      </div>

      <div class="tasks-list scrollable">
        <div class="task-item add-task-item" @click="startAdding" v-if="!useEditParams.isAdding">
          <div class="checkbox placeholder-checkbox">
            <div class="checkmark"></div>
          </div>
          <div class="task-content">
            <div class="task-title placeholder-title">
              添加新待办
            </div>
          </div>
        </div>
        <!-- 编辑状态 -->
        <div class="task-item editing-task" v-if="useEditParams.isAdding">
          <div class="checkbox">
            <div class="checkmark"></div>
          </div>
          <input ref="inputRef" v-model="newTask.title" class="task-input" @blur="finishAdding"
            @keyup.enter="handleEnter">
          <div class="edit" @mousedown.prevent="useEditParams.openEditModal(newTask)">
            <Settings2 :size="20" color="gray" strokeWidth="1.5" class="hidden-icon" />
          </div>
        </div>
        <div v-for="(group, index) in groupedTasksByDate" :key="index" class="date-group">
          <!-- 未完成任务 -->
          <transition-group name="task" tag="div" :css="useTodoSideBarParams.isDisableTransition ? false : true">
            <div :key="'date-title-' + index">
              <h2 class="date-title">{{ formatDateHeader(group.date) }}</h2>
            </div>

            <div v-for="task in group.incomplete" :key="task.id" class="task-item"
              :class="{ 'completed': task.completionTimer, 'fade-out': task.fadeOut, 'fade-in': task.fadeIn }">
              <div class="checkbox" @click="completeTask(task)"
                :style="{ borderColor: getPriorityColor(task.priority) }">
                <div class="checkmark" @click="completeTask(task)"
                  :style="{ 'background-color': getPriorityColor(task.priority) }"></div>
              </div>
              <div class="task-content" @click="completeTask(task)">

                <div class="task-title">
                  {{ task.title }}
                </div>
                <div class="task-meta">
                  <div class="icon">
                    <SquarePen :size="20" color="gray" strokeWidth="1.5" class="hidden-icon"
                      @mousedown.prevent="useEditParams.openEditModal(task)" />
                    <Trash2 :size="20" color="gray" strokeWidth="1.5"
                      @mousedown.prevent="useTodoList.deleteTask(task.id)" class="hidden-icon" />
                  </div>
                  <div v-if="task.date" class="task-time">{{ formatTimeTo24Hour(task.date) }}</div>
                  <div v-if="task.tag" class="task-tag"
                    :style="{ backgroundColor: useProjectParams.projects.find(p => p.id === 'daily_todos')?.tags.find(t => t.name === task.tag)?.color || '#e0e0e0' }">
                    {{ "#" + task.tag }}
                  </div>
                </div>
              </div>

            </div>
          </transition-group>

          <!-- 已完成任务 -->
          <transition-group name="task" tag="div" :css="useTodoSideBarParams.isDisableTransition ? false : true">
            <div v-for="task in group.completed" :key="task.id" class="task-item completed-task-item"
              :class="{ 'completed': task.completionTimer, 'fade-out': task.fadeOut, 'fade-in': task.fadeIn }">
              <div class="checkbox" @click="incompleteTask(task)"
                :style="{ borderColor: getPriorityColor(task.priority) }">
                <div class="checkmark" @click="incompleteTask(task)"
                  :style="{ 'background-color': getPriorityColor(task.priority) }"></div>
              </div>
              <div class="task-content" @click="incompleteTask(task)">
                <div class="task-title">
                  {{ task.title }}
                </div>
                <div class="task-meta">
                  <div class="icon">
                    <SquarePen :size="20" color="gray" strokeWidth="1.5" class="hidden-icon"
                      @mousedown.prevent="useEditParams.openEditModal(task)" />
                    <Trash2 :size="20" color="gray" strokeWidth="1.5"
                      @mousedown.prevent="useTodoList.deleteTask(task.id)" class="hidden-icon" />
                  </div>
                  <div v-if="task.date" class="task-time">{{ formatTimeTo24Hour(task.date) }}</div>
                  <div v-if="task.tag" class="task-tag"
                    :style="{ backgroundColor: useProjectParams.projects.find(p => p.id === 'daily_todos')?.tags.find(t => t.name === task.tag)?.color || '#e0e0e0' }">
                    {{ "#" + task.tag }}
                  </div>
                </div>
              </div>

            </div>
          </transition-group>
        </div>
      </div>
    </div>
    <EditPanel v-if="useEditParams.isEditModalOpen" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, onMounted } from 'vue';
import { TodoTask } from '../../types/todolist.ts';
import { Trash2, SquarePen, Settings2 } from 'lucide-vue-next';
import { TodoList } from '../../stores/TodoList/TodoList.ts';
import { TodoSideBarParams } from '../../stores/TodoList/TodoSideBarParams.ts';
import { EditParams } from '../../stores/TodoList/EditParams.ts';
import EditPanel from './EditPanel.vue';

const useEditParams = EditParams();
const useTodoSideBarParams = TodoSideBarParams();
const useTodoList = TodoList();
// 新增状态
const inputRef = ref<HTMLInputElement | null>(null);

function getPriorityColor(priority: number) {
  switch (priority) {
    case 1:
      return 'green';
    case 2:
      return 'orange';
    case 3:
      return 'red';
    default:
      return 'gray';
  }
}

// 启动添加
function startAdding() {
  useEditParams.isAdding = true;
  newTask.title = "";

  // 在DOM更新后聚焦到输入框
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.focus();
    }
  });
}

// 处理回车事件
function handleEnter() {
  finishAdding();
  startAdding()
}

import { TodoApi } from '../../stores/TodoList/TodoAPI.ts';
const api = TodoApi();

// 完成添加
function finishAdding() {
  // 防止重复触发
  if (!useEditParams.isAdding || useEditParams.isEditModalOpen) return;

  if (newTask.title.trim()) {
    useProjectParams.addTodoToProject('daily_todos', newTask.title.trim(), new Date(useEditParams.lastAddedDate));
  }
  useEditParams.isAdding = false;
}

// 标记任务为完成
function completeTask(task: TodoTask) {

  // 如果已经处于淡出过程中，清除定时器
  if (task.completionTimer) {
    clearTimeout(task.completionTimer);
    task.completionTimer = null;
    // 恢复到未完成状态
    task.completed = false;
    return;
  }

  // 设置定时器
  task.completionTimer = setTimeout(() => {
    task.fadeOut = true;

    // 动画结束后将任务移动到已完成列表
    setTimeout(() => {
      task.fadeOut = false;
      task.completed = true;
      api.taskAPI.updateTask(task.id, {
        completed: true
      });

      task.fadeIn = true;
      task.completionTimer = null; // 清除定时器引用

      // 淡入动画结束后清除标记
      setTimeout(() => {
        task.fadeIn = false;
      }, 600);
    }, 600); // 与fadeOut动画时长一致
  }, 1000);
}

// 标记任务为未完成
function incompleteTask(task: TodoTask) {
  // 如果已经处于淡出过程中，清除定时器
  if (task.completionTimer) {
    clearTimeout(task.completionTimer);
    task.completionTimer = null;
    // 恢复到完成状态
    task.completed = false;
    return;
  }

  // 设置定时器
  task.completionTimer = setTimeout(() => {
    task.fadeOut = true;

    // 动画结束后将任务移动到未完成列表
    setTimeout(() => {
      task.fadeOut = false;
      task.completed = false;
      api.taskAPI.updateTask(task.id, {
        completed: false
      });
      task.fadeIn = true;
      task.completionTimer = null; // 清除定时器引用

      // 淡入动画结束后清除标记
      setTimeout(() => {
        task.fadeIn = false;
      }, 200);
    }, 400); // 与fadeOut动画时长一致
  }, 0);
}




// 新任务对象
const newTask = reactive({
  id: crypto.randomUUID(),
  title: "",
  date: new Date(),
  tag: "",
  priority: 0,
  completed: false,
  fadeOut: false,
  fadeIn: false,
  completionTimer: null,
  repeat: false,
  recurrence: null
});

function formatTimeTo24Hour(date: Date) {
  if (!(date instanceof Date)) {
    return '';
  }

  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

// 添加日期分组格式化函数
function formatDateHeader(date: Date) {
  const options: Intl.DateTimeFormatOptions = {
    month: 'long' as const,
    day: 'numeric' as const
  };
  return new Date(date).toLocaleDateString('zh-CN', options).replace('年', '月').replace('日', '日');
}


const groupedTasksByDate = computed(() => {
  const groups = new Map();

  [...useTodoList.incompleteTasks, ...useTodoList.completedTasks].forEach(task => {
    const taskDate = new Date(task.date);
    const dateKey = `${taskDate.getFullYear()}-${(taskDate.getMonth() + 1).toString().padStart(2, '0')}-${taskDate.getDate().toString().padStart(2, '0')}`;

    if (!groups.has(dateKey)) {
      groups.set(dateKey, {
        date: new Date(taskDate.getFullYear(), taskDate.getMonth(), taskDate.getDate()),
        incomplete: [],
        completed: []
      });
    }

    const group = groups.get(dateKey);
    task.completed ? group.completed.push(task) : group.incomplete.push(task);
  });

  return Array.from(groups.values()).sort((a, b) => b.date - a.date);
});

import { ProjectParams } from '../../stores/TodoList/ProjectParams';
const useProjectParams = ProjectParams();
onMounted(async () => {
  useProjectParams.activeProjectId = 'daily_todos';
})
</script>

<style scoped>
.todo-app {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  background: white;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  overflow: hidden;
}

/* 头部样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0px;
  margin-top: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.today-title {
  font-size: 32px;
  font-weight: 600;
  color: #222;
  user-select: none;
}

.view-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
}

.view-button:hover {
  background-color: #f7f7f7;
}

.icon {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  position: relative;
  left: 2px;
}

.hidden-icon {
  opacity: 0;
  transition: all 0.3s ease;
  border-radius: 6px;
  height: 28px;
  width: 28px;
  padding: 4px;
}

.task-item:hover .hidden-icon {
  opacity: 1;
}

.hidden-icon:hover {
  background-color: #e0e0e0;

}

/* 项目标题 */
.section-title {
  padding: 16px 24px 8px;
  font-size: 16px;
  font-weight: 600;
  color: #555;
  background-color: #f8f8f8;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.no-tasks-message {
  text-align: center;
  color: #aaa;
  font-style: italic;
  margin-top: 20px;
  user-select: none;
}

/* 任务列表 */
.tasks-list {
  height: calc(100vh - 120px);
  padding: 5px 0 10px;
}

.task-item {
  display: flex;
  padding: 2px 10px;
  border-radius: 8px;
  align-items: center;
  justify-content: baseline;
  cursor: pointer;
  transition: background 0.2s;
  min-height: 36px;
  /* 统一高度避免抖动 */
}

.task-item:last-child {
  border-bottom: none;
}

.task-item:hover {
  background-color: #f4f4f4c9;
}

/* 淡出动画 */
.fade-out {
  animation: fadeOut 0.3s ease-out forwards;
}

@keyframes fadeOut {
  from {
    opacity: 0.6;
  }

  to {
    opacity: 0;
  }
}

/* 淡入动画 */
.fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
    color: #BEBEBE;
  }

  to {
    transform: translateY(0);
    opacity: 0.6;
    color: #BEBEBE;
  }
}

.task-move {
  transition: transform 0.6s ease;
}

.task-enter-active {
  transition: all 0.3s ease;
}

.task-leave-active {
  transition: all 0.3s ease;
  position: absolute;
}

.task-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.task-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}


/* 复选框 */
.checkbox {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 6px;
  margin-top: 4px;
  flex-shrink: 0;
}

.checkmark {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #717171;
  display: none;
}

.completed .checkmark {
  display: block;
}

.completed-task-item .checkmark {
  display: block;
}

/* 任务内容 */
.task-content {
  flex-grow: 1;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
  /* 修改为 flex-start 以对齐顶部 */
}

.task-title {
  font-size: 17px;
  font-weight: 500;
  color: #333;
  margin: 8px 10px;
  /* 统一上下边距 */
  display: flex;
  align-items: center;
  gap: 8px;
  user-select: none;
}

.completed .task-title {
  text-decoration: line-through;
  color: #999;
}

.task-meta {
  display: flex;
  align-items: center;
  position: relative;
  top: 8px;
  gap: 12px;
}

.task-time {
  font-size: 14px;
  color: #9d9d9d;
  user-select: none;
}


.add-task-item {
  border-radius: 8px;
  border: none;
  background-color: transparent;
}

.add-task-item:hover {
  background-color: #f4f4f4c9;
}

.placeholder-checkbox {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px dashed #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 6px;
  margin-top: 4px;
  flex-shrink: 0;
}

.placeholder-title {
  font-size: 17px;
  color: #aaa;
  font-weight: 400;
  font-style: italic;
  transition: all 0.3s ease;
  margin: 8px 0;
  /* 与.task-title保持一致 */
}

.add-task-item:hover .placeholder-title {
  color: #cbcbcb;
}

.editing-task {
  padding: 6px 10px;
  align-items: center;
  min-height: 36px;
  /* 与.task-item保持一致避免抖动 */
}

.task-input {
  flex-grow: 1;
  border: none;
  font-size: 17px;
  font-weight: 400;
  /* 与.task-title的margin保持一致 */
  margin: 0px 10px;
  color: #000000;
  background: transparent;
}

.task-input:focus {
  outline: none;
}

.add-task-item:hover .placeholder-checkbox {
  border-color: #d7d7d7;
}

.completed-task-item {
  opacity: 0.6;
}

.completed-task-item .task-title {
  text-decoration: line-through;
  color: #999;
}

.date-title {
  font-size: 22px;
  font-weight: 600;
  color: #161616;
  padding: 12px 12px 0px 12px;
  margin: 0px 12px 12px 0px;
  user-select: none;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.scrollable {
  overflow-y: auto;
  max-height: calc(100vh - 180px);
  padding-bottom: 20px;
}

.task-tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 14px;
  color: #fff;
  display: inline-block;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.396), rgba(128, 128, 128, 0.046));
}

/* 暗色主题样式 */
[data-theme="dark"] .header{
  border-bottom: #484848;
}
[data-theme="dark"] .todo-app {
  background-color: #1e1e1e;
  color: #ffffff;
}

[data-theme="dark"] .header {
  background-color: #1E1E1E;
  color: #ffffff;
}

[data-theme="dark"] .today-title {
  color: #ffffff;
}

[data-theme="dark"] .tasks-list {
  background-color: #1e1e1e;
}

[data-theme="dark"] .task-item {
  background-color: #1d1d1d;
  color: #ffffff;
}

[data-theme="dark"] .task-item:hover {
  background-color: #333333;
}

[data-theme="dark"] .task-title {
  color: #ffffff;
}

[data-theme="dark"] .completed .task-title,
[data-theme="dark"] .completed-task-item .task-title {
  color: #aaaaaa;
}

[data-theme="dark"] .task-time {
  color: #aaaaaa;
}

[data-theme="dark"] .checkbox {
  border: 2px solid #666666;
}

[data-theme="dark"] .checkmark {
  background-color: #aaaaaa;
}

[data-theme="dark"] .add-task-item {
  background-color: transparent;
}

[data-theme="dark"] .add-task-item:hover {
  background-color: #333333;
}

[data-theme="dark"] .placeholder-checkbox {
  border: 2px dashed #666666;
}

[data-theme="dark"] .placeholder-title {
  color: #888888;
}

[data-theme="dark"] .add-task-item:hover .placeholder-title {
  color: #aaaaaa;
}

[data-theme="dark"] .task-input {
  color: #ffffff;
  background-color: transparent;
}

[data-theme="dark"] .date-title {
  color: #ffffff;
}

[data-theme="dark"] .no-tasks-message {
  color: #888888;
}

[data-theme="dark"] .empty-icon {
  color: #666666;
}

[data-theme="dark"] .hidden-icon:hover {
  background: #2D2D2D;
}
</style>