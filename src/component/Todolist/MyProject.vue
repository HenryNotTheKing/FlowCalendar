<template>
  <div class="project-view">
    <div v-if="activeProject" class="header">
      <input v-if="isEditingTitle" v-model="editableTitle" @blur="saveTitle" @keyup.enter="saveTitle"
        class="title-input" ref="titleInput" />
      <div v-else class="project-title" @click="startEditingTitle">
        {{ activeProject.name }}
      </div>
    </div>
    <div v-else class="no-project-selected">
      <p>请在侧边栏选择一个项目</p>
    </div>

    <div class="tasks-list scrollable">
      <div v-for="(group, index) in groupedTasksByDate" :key="index" class="date-group">
        <!-- 当项目没有任务时不显示日期标题 -->
        <h2 class="date-title"
          v-if="!(groupedTasksByDate.length === 1 && group.incomplete.length === 0 && group.completed.length === 0)">{{
            formatDateHeader(group.date) }}</h2>
        <!-- 当项目没有任务时显示的添加入口 -->
        <div v-if="group.incomplete.length === 0 && group.completed.length === 0">
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

          <!-- 编辑状态 -->
          <div class="task-item editing-task" v-if="useEditParams.isAdding">
            <div class="checkbox">
              <div class="checkmark"></div>
            </div>
            <input :ref="el => { if (el) inputRefForAdd = el as HTMLInputElement }" v-model="newTodoTitle"
              class="task-input" @blur="finishAdding" @keyup.enter="finishAddingRestart">
            <div class="edit" @mousedown.prevent="openProjectEditModal">
              <Settings2 :size="20" color="gray" strokeWidth="1.5" class="hidden-icon" />
            </div>
          </div>
        </div>

        <!-- 当项目有任务时，在上一次添加任务的日期下方显示添加入口 -->
        <div v-else>
          <!-- 新增添加入口 -->
          <div class="task-item add-task-item"
            @click="() => { useEditParams.lastAddedDate = group.date; startAdding(); }"
            v-if="!useEditParams.isAdding && index === lastAddedDateGroupIndex">
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
          <div class="task-item editing-task" v-if="useEditParams.isAdding && index === lastAddedDateGroupIndex">

            <div class="checkbox">
              <div class="checkmark"></div>
            </div>
            <input :ref="el => { if (el) inputRefForGroup = el as HTMLInputElement }" v-model="newTodoTitle"
              class="task-input" @blur="finishAdding" @keyup.enter="finishAddingRestart">
            <div class="edit" @mousedown.prevent="openProjectEditModal">
              <Settings2 :size="20" color="gray" strokeWidth="1.5" class="hidden-icon" />
            </div>
          </div>
        </div>

        <!-- 未完成任务 -->
        <transition-group name="task" tag="div" :css="useTodoSideBarParams.isDisableTransition ? false : true">
          <div v-for="task in group.incomplete" :key="'incomplete-' + task.id" class="task-item"
            :class="{ 'completed': task.completionTimer, 'fade-out': task.fadeOut, 'fade-in': task.fadeIn }">
            <div class="checkbox" @click="toggleTodoStatus(task.id, task.completed)"
              :style="{ borderColor: getPriorityColor(task.priority) }">
              <div class="checkmark" @click="toggleTodoStatus(task.id, task.completed)"
                :style="{ 'background-color': getPriorityColor(task.priority) }"></div>
            </div>
            <div class="task-content" @click="toggleTodoStatus(task.id, task.completed)">
              <div class="task-title">
                {{ task.title }}
              </div>
              <div class="task-meta">
                <div class="icon">
                  <SquarePen :size="20" color="gray" strokeWidth="1.5" class="hidden-icon"
                    @mousedown.prevent="useEditParams.openEditModal(task)" />
                  <Trash2 :size="20" color="gray" strokeWidth="1.5" @mousedown.prevent="removeTodo(task.id)"
                    class="hidden-icon" />
                </div>

                <div v-if="task.date" class="task-time">{{ formatTimeTo24Hour(task.date) }}</div>
                <div v-if="task.tag" class="task-tag"
                  :style="{ backgroundColor: useProjectStore.activeProject?.tags.find(t => t.name === task.tag)?.color || '#e0e0e0' }">
                  {{ "#" + task.tag }}
                </div>
              </div>
            </div>
          </div>
        </transition-group>

        <!-- 已完成任务 -->
        <transition-group name="task" tag="div" :css="useTodoSideBarParams.isDisableTransition ? false : true">
          <div v-for="task in group.completed" :key="'completed-' + task.id" class="task-item completed-task-item"
            :class="{ 'completed': task.completionTimer, 'fade-out': task.fadeOut, 'fade-in': task.fadeIn }">
            <div class="checkbox" @click="toggleTodoStatus(task.id, task.completed)"
              :style="{ borderColor: getPriorityColor(task.priority) }">
              <div class="checkmark" @click="toggleTodoStatus(task.id, task.completed)"
                :style="{ 'background-color': getPriorityColor(task.priority) }"></div>
            </div>
            <div class="task-content" @click="toggleTodoStatus(task.id, task.completed)">
              <div class="task-title">
                {{ task.title }}
              </div>
              <div class="task-meta">
                <div class="icon">
                  <SquarePen :size="20" color="gray" strokeWidth="1.5" class="hidden-icon"
                    @mousedown.prevent="useEditParams.openEditModal(task)" />
                  <Trash2 :size="20" color="gray" strokeWidth="1.5" @mousedown.prevent="removeTodo(task.id)"
                    class="hidden-icon" />
                </div>

                <div v-if="task.date" class="task-time">{{ formatTimeTo24Hour(task.date) }}</div>
                <div v-if="task.tag" class="task-tag"
                  :style="{ backgroundColor: useProjectStore.activeProject?.tags.find(t => t.name === task.tag)?.color || '#e0e0e0' }">
                  {{ "#" + task.tag }}
                  {{ "#" + task.tag }}
                </div>
              </div>
            </div>
          </div>
        </transition-group>
      </div>
    </div>
    <EditPanel v-if="useEditParams.isEditModalOpen" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue';
import { ProjectParams } from '../../stores/TodoList/ProjectParams.ts';
import { Trash2, SquarePen, Settings2 } from 'lucide-vue-next';
import { EditParams } from '../../stores/TodoList/EditParams.ts';
// import { TodoList } from '../../stores/TodoList/TodoList.ts';
import { TodoSideBarParams } from '../../stores/TodoList/TodoSideBarParams.ts';
import EditPanel from './EditPanel.vue';
import { TodoTask } from '../../types/todolist.ts';
const useProjectStore = ProjectParams();
const useEditParams = EditParams();
// const useTodoList = TodoList();
const useTodoSideBarParams = TodoSideBarParams();

const isEditingTitle = ref(false);
const editableTitle = ref('');
const newTodoTitle = ref('');
const inputRefForAdd = ref<HTMLInputElement | null>(null);
const inputRefForGroup = ref<HTMLInputElement | null>(null);
const titleInput = ref<HTMLInputElement | null>(null);

const activeProject = computed(() => useProjectStore.activeProject);

// 初始化useEditParams.lastAddedDate
watch(activeProject, (newProject) => {
  if (newProject && newProject.todos.length > 0) {
    // 找到最新的任务日期
    const latestTask = newProject.todos.reduce((latest, current) => {
      return new Date(current.date) > new Date(latest.date) ? current : latest;
    });
    useEditParams.lastAddedDate = new Date(latestTask.date);
  }
}, { immediate: true });

// 当项目没有任务时，将useEditParams.lastAddedDate设置为今天
watch(activeProject, (newProject) => {
  if (newProject && newProject.todos.length === 0) {
    useEditParams.lastAddedDate = new Date();
  }
}, { immediate: true });

// 按日期分组任务
const groupedTasksByDate = computed(() => {
  if (!activeProject.value) return [];

  const groups = new Map();

  activeProject.value.todos.forEach(task => {
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

  // 如果没有任务，添加一个今天的空组
  if (activeProject.value.todos.length === 0) {
    const today = new Date();
    const todayKey = `${today.getFullYear()}-${(today.getMonth() + 1).toString().padStart(2, '0')}-${today.getDate().toString().padStart(2, '0')}`;
    groups.set(todayKey, {
      date: new Date(today.getFullYear(), today.getMonth(), today.getDate()),
      incomplete: [],
      completed: []
    });
  }

  return Array.from(groups.values()).sort((a, b) => b.date - a.date);
});
// 格式化日期标题
function formatDateHeader(date: Date) {
  const options: Intl.DateTimeFormatOptions = {
    month: 'long' as const,
    day: 'numeric' as const
  };
  return new Date(date).toLocaleDateString('zh-CN', options).replace('年', '月').replace('日', '日');
}


// 格式化时间
function formatTimeTo24Hour(date: Date) {
  if (!(date instanceof Date)) {
    return '';
  }

  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}


// 获取上次添加任务的日期组索引
const lastAddedDateGroupIndex = computed(() => {
  if (!useEditParams.lastAddedDate || !groupedTasksByDate.value) return -1;

  const lastAddedDateObj = new Date(useEditParams.lastAddedDate);

  for (let i = 0; i < groupedTasksByDate.value.length; i++) {
    const group = groupedTasksByDate.value[i];
    if (group.date.toDateString() === lastAddedDateObj.toDateString()) {
      return i;
    }
  }

  // 如果找不到对应的日期组，返回最后一个日期组的索引
  return groupedTasksByDate.value.length > 0 ? groupedTasksByDate.value.length - 1 : -1;
});

// 获取优先级颜色
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

// 标题编辑功能
const startEditingTitle = () => {
  isEditingTitle.value = true;
  editableTitle.value = activeProject.value?.name ?? '';

  nextTick(() => {
    if (titleInput.value) {
      titleInput.value.focus();
    }
  });
};

const saveTitle = () => {
  if (editableTitle.value.trim() && activeProject.value) {
    useProjectStore.updateProject(activeProject.value.id, { name: editableTitle.value.trim() });
  }
  isEditingTitle.value = false;
};

// 待办事项添加功能
const startAdding = () => {
  useEditParams.isAdding = true;
  newTodoTitle.value = "";
  nextTick(() => {
    // 添加延时确保DOM更新完成
    setTimeout(() => {
      if (inputRefForAdd.value) {
        console.log("add input", inputRefForAdd.value);
        inputRefForAdd.value.focus();
        inputRefForAdd.value = null; // 清除引用，避免重复引用
      } else if (inputRefForGroup.value) {
        console.log("group input", inputRefForGroup.value);
        inputRefForGroup.value.focus();
        inputRefForGroup.value = null; // 清除引用，避免重复引用
      } else {
        console.warn('No input element found to focus');
      }
    }, 50);
  });
};
import { TodoApi } from '../../stores/TodoList/TodoAPI.ts';
const api = TodoApi();

const finishAdding = () => {
  // 即使在编辑模态框打开的情况下，也需要确保添加状态被重置
  if (!useEditParams.isAdding || useEditParams.isEditModalOpen) return;

  if (newTodoTitle.value.trim() && activeProject.value) {
    // 使用上次添加的日期，如果没有则使用今天
    const targetDate = useEditParams.lastAddedDate || new Date();
    useProjectStore.addTodoToProject(activeProject.value.id, newTodoTitle.value.trim(), targetDate);
    // 更新上次添加日期
    useEditParams.lastAddedDate = targetDate;
  }
  useEditParams.isAdding = false;
};

const finishAddingRestart = () => {
  finishAdding();
  startAdding();
};
const removeTodo = (todoId: string) => {
  if (activeProject.value) {
    useProjectStore.removeTodoFromProject(activeProject.value.id, todoId);
  }
};

const toggleTodoStatus = (todoId: string, completed: boolean) => {
  if (!activeProject.value) return;

  // 找到对应的task
  const task = activeProject.value.todos.find(t => t.id === todoId);
  if (!task) return;

  // 如果已经处于淡出过程中，清除定时器
  if (task.completionTimer) {
    clearTimeout(task.completionTimer);
    task.completionTimer = null;
    // 恢复到未完成状态
    task.completed = false;
    useProjectStore.updateTodoStatus(activeProject.value.id, todoId, false);
    return;
  }

  // 设置定时器
  if (!completed) {
    // 标记为完成
    task.completionTimer = setTimeout(() => {
      task.fadeOut = true;

      // 动画结束后更新状态
      setTimeout(() => {
        task.fadeOut = false;
        task.completed = true;
        api.taskAPI.updateTask(todoId, { completed: true });
        task.fadeIn = true;
        task.completionTimer = null; // 清除定时器引用
        useProjectStore.updateTodoStatus(activeProject.value?.id ?? '', todoId, true);

        // 淡入动画结束后清除标记
        setTimeout(() => {
          task.fadeIn = false;
        }, 600);
      }, 600); // 与fadeOut动画时长一致
    }, 1000);
  } else {
    // 标记为未完成
    task.completionTimer = setTimeout(() => {
      task.fadeOut = true;

      // 动画结束后更新状态
      setTimeout(() => {
        task.fadeOut = false;
        task.completed = false;
        api.taskAPI.updateTask(todoId, { completed: false });
        task.fadeIn = true;
        task.completionTimer = null; // 清除定时器引用
        useProjectStore.updateTodoStatus(activeProject.value?.id ?? '', todoId, false);

        // 淡入动画结束后清除标记
        setTimeout(() => {
          task.fadeIn = false;
        }, 200);
      }, 400); // 与fadeOut动画时长一致
    }, 0);
  }
};

// 项目编辑模态框
const openProjectEditModal = () => {
  // 创建一个临时任务对象，包含项目ID
  const tempTask = {
    id: crypto.randomUUID(),
    title: newTodoTitle.value,
    date: new Date(),
    completed: false,
    priority: 0,
    tag: '',
    projectId: activeProject.value?.id ?? ''
  };
  useEditParams.openEditModal(tempTask as TodoTask);
};
</script>

<style scoped>
.project-view {
  width: 100%;
  margin: 0 auto;
  background: white;
  font-family: -apple-system, 'Segoe UI', sans-serif;
  overflow: hidden;
  padding: 20px;
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

.project-title {
  font-size: 32px;
  font-weight: 600;
  color: #222;
  user-select: none;
  cursor: pointer;
}

.title-input {
  font-size: 32px;
  font-weight: 600;
  color: #222;
  border: none;
  outline: none;
  background: transparent;
  width: 100%;
}

.no-project-selected {
  text-align: center;
  color: #666;
  margin-top: 50px;
}

.todo-section {
  margin-top: 20px;
}

/* 任务列表 */
.todo-list {
  list-style: none;
  padding: 0;
  height: calc(100vh - 120px);
  padding: 5px 0 10px;
}

.task-meta {
  display: flex;
  align-items: center;
  position: relative;
  top: 8px;
  gap: 12px;
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

.date-title {
  font-size: 22px;
  font-weight: 600;
  color: #161616;
  padding: 12px 12px 0px 12px;
  user-select: none;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.task-item:last-child {
  border-bottom: none;
}

.task-item:hover {
  background-color: #f4f4f4c9;
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

.completed-task-item .task-title {
  text-decoration: line-through;
  color: #999;
  opacity: 0.6;
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

.scrollable {
  overflow-y: auto;
  max-height: calc(100vh - 180px);
  padding-bottom: 20px;
}

.placeholder-title {
  font-size: 17px;
  color: #aaa;
  font-weight: 400;
  font-style: italic;
  transition: all 0.3s ease;
  margin: 8px 10px;
  /* 与.task-title保持一致 */
}

.add-task-item:hover .placeholder-title {
  color: #cbcbcb;
}

.editing-task {
  padding: 6px 10px;
  min-height: 36px;
  /* 与.task-item保持一致避免抖动 */
}

.task-input {
  flex-grow: 1;
  border: none;
  font-size: 17px;
  font-weight: 400;
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

.tasks-list,
.completed-tasks-section>div:not(.header) {
  position: relative;
  height: calc(100vh - 120px);
  padding: 5px 0 10px;
}

.task-tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 14px;
  color: #fff;
  display: inline-block;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.802));
}

.task-time {
  font-size: 14px;
  color: #9d9d9d;
  user-select: none;
}

/* 暗色主题样式 */
[data-theme="dark"] .project-view {
  background-color: #1e1e1e;
  color: #ffffff;
}

[data-theme="dark"] .header {
  background-color: #1E1E1E;
  color: #ffffff;
}

[data-theme="dark"] .project-title {
  color: #ffffff;
}

[data-theme="dark"] .todo-list {
  background-color: #1e1e1e;
}

[data-theme="dark"] .task-item {
  background-color: #2d2d2d;
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

[data-theme="dark"] .hidden-icon:hover {
  background-color: #444444;
}

[data-theme="dark"] .task-time {
  color: #aaaaaa;
}

[data-theme="dark"] .task-tag {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.3));
}
</style>