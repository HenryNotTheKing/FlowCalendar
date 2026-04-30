<template>
  <div class="schedule-sidebar">
    <div class="month-header-container">
        <div v-if="currentMonth" key="month" class="month-header">
          {{ currentMonth }}
        </div>
    </div>
    <div 
      class="schedule-list"
      ref="scrollContainer"
      @scroll.passive="handleScroll"
    >
      <!-- 每天待办事项区块 -->
      <div v-if="todoDays.length > 0">
        <div v-for="day in todoDays" :key="day.id" class="day-schedule" :data-month="getMonthKey(day.id)">
          <!-- 日期标题区 -->
          <div class="day-header">
            <span class="date-label">{{ day.dateLabel }}</span>
            <span v-if="day.isToday" class="today-label">今天</span>
            <span v-if="day.isTomorrow" class="tomorrow-label">明天</span>
            <span class="day-name">{{ day.dayName }}</span>
          </div>

          <!-- 待办事项列表 -->
          <div v-for="task in day.tasks" :key="task.id" class="event-item" @click="handleTaskClick(task)" :class="{ 'fade-out': task.fadeOut, 'fade-in': task.fadeIn }">
            <!-- Checkmark 按钮 -->
            <div class="checkmark-container" >
              <div 
                class="checkmark" 
                :class="{ completed: task.completionTimer}"
                :style="{ 'borderColor': getPriorityColor(task.priority), '--priority-color': getPriorityColor(task.priority) }"
              >
                <svg v-if="task.completed" class="checkmark-svg" viewBox="0 0 12 12">
                  <path d="M1 6l3.5 3.5L11 2"></path>
                </svg>
              </div>
            </div>
            
            <!-- 时间信息 -->
            <div class="event-time">
              <div class="start-time">{{ formatTime(new Date(task.date)) }}</div>
            </div>

            <!-- 任务标题 -->
            <div 
              class="event-title" 
              :class="{ 'completed': task.completionTimer}"
            >
              {{ task.title }}
            </div>
          </div>
        </div>
      </div>
      <!-- 空提示 -->
      <div v-else class="empty-prompt">
        暂无待办事项
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { TodoList } from '../../stores/TodoList/TodoList';
import { DateDisplay } from '../../stores/Calendar/DateDisplay';

const useTodoList = TodoList();
const useDateDisplay = DateDisplay();

// 辅助函数
const isSameDay = (d1, d2) => 
  d1.getFullYear() === d2.getFullYear() &&
  d1.getMonth() === d2.getMonth() &&
  d1.getDate() === d2.getDate();

const isSameMonth = (d1, d2) =>
  d1.getFullYear() === d2.getFullYear() &&
  d1.getMonth() === d2.getMonth();

const getDayName = (dayIndex) => 
  ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dayIndex];

const formatTime = (date) => 
  date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });

// 获取优先级颜色
const getPriorityColor = (priority) => {
  const colors = ['grey', 'green', 'orange', 'red'];
  return colors[priority] || '#9E9E9E';
};

// 新增响应式变量
const scrollContainer = ref(null);
const currentMonth = ref('');
const prevMonthKey = ref('');
const monthTransition = ref('slide-up');

// 获取月份唯一标识
const getMonthKey = (dateString) => {
  const date = new Date(dateString);
  return `${date.getFullYear()}-${date.getMonth()}`;
};
 
let scrollCheckTimer = null;
const handleScroll = () => {
  clearTimeout(scrollCheckTimer);
  scrollCheckTimer = setTimeout(() => {
    const container = scrollContainer.value;
    if (container) {
      // 动态调整缓冲区间
      const dynamicBuffer = Math.max(50, container.clientHeight * 0.4);
      const { scrollTop, scrollHeight, clientHeight } = container;
      
      if (scrollTop < dynamicBuffer) {
        // 加载更多逻辑可以在这里添加
      }
      
      if (scrollHeight - (scrollTop + clientHeight) < dynamicBuffer) {
        // 加载更多逻辑可以在这里添加
      }
    }
    updateMonthHeader();
  }, 50);
};

// 更新月份标题
const updateMonthHeader = () => {
  const days = [...scrollContainer.value.querySelectorAll('.day-schedule')];
  const visibleDays = days.filter(el => {
    const rect = el.getBoundingClientRect();
    return rect.top >= 40 && rect.bottom <= window.innerHeight;
  });

  if (visibleDays.length > 0) {
    const currentDay = visibleDays[0];
    const newMonthKey = currentDay.dataset.month;
    const [year, month] = newMonthKey.split('-');
    const newMonth = `${year}年${parseInt(month) + 1}月`;

    if (newMonthKey !== prevMonthKey.value) {
      // 判断滚动方向
      const oldDate = prevMonthKey.value ? new Date(prevMonthKey.value.replace('-', '/')) : null;
      const newDate = new Date(newMonthKey.replace('-', '/'));
      
      monthTransition.value = newDate > oldDate ? 'slide-up' : 'slide-down';
      prevMonthKey.value = newMonthKey;
      currentMonth.value = newMonth;
    }
  }
};

const scrollToToday = () => {
  nextTick(() => {
    const currentDate = new Date().getDate().toString();
    const days = [...scrollContainer.value.querySelectorAll('.day-schedule')];
    const todayElement = days.find(el => {
      const dateLabel = el.querySelector('.date-label')?.textContent?.trim();
      return dateLabel === currentDate && el.querySelector('.today-label');
    });

    if (todayElement && scrollContainer.value) {
      // 计算相对滚动容器的位置
      const containerTop = scrollContainer.value.getBoundingClientRect().top;
      const elementTop = todayElement.getBoundingClientRect().top;
      scrollContainer.value.scrollTop = elementTop - containerTop;
      updateMonthHeader();
    }
  });
};

// 生成待办事项数据
const todoDays = computed(() => {
  const daysMap = new Map();
  
  // 合并未完成和已完成的任务
  const allTasks = [...useTodoList.incompleteTasks];
  
  allTasks.forEach(task => {
    const taskDate = new Date(task.date);
    const dateKey = `${taskDate.getFullYear()}-${(taskDate.getMonth()+1).toString().padStart(2,'0')}-${taskDate.getDate().toString().padStart(2,'0')}`;
      
    if (!daysMap.has(dateKey)) {
      daysMap.set(dateKey, createDayData(taskDate));
    }
      
    const dayData = daysMap.get(dateKey);
    dayData.tasks.push(task);
  });

  return Array.from(daysMap.values())
    .sort((a, b) => {
      const aDate = a.id.split('-').map(Number);
      const bDate = b.id.split('-').map(Number);
      return aDate[0] - bDate[0] || aDate[1] - bDate[1] || aDate[2] - bDate[2];
    })
    .map(day => ({
      ...day,
      tasks: day.tasks.sort((a, b) => {
        // 未完成的任务排在前面
        if (!a.completed && b.completed) return -1;
        if (a.completed && !b.completed) return 1;
        
        // 按时间排序
        return new Date(a.date).getTime() - new Date(b.date).getTime();
      })
    }));
});

// 创建每日数据
function createDayData(date) {
  return {
    id: `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2,'0')}-${date.getDate().toString().padStart(2,'0')}`,
    dateLabel: date.getDate().toString(),
    dayName: getDayName(date.getDay()),
    isToday: isSameDay(date, new Date()),
    isTomorrow: isSameDay(date, new Date(Date.now() + 86400000)),
    month: isSameMonth(date, new Date()) ? null : `${date.getMonth() + 1}月`,
    tasks: []
  };
}

import { TodoApi } from '../../stores/TodoList/TodoAPI.ts';
const api = TodoApi();
// 处理任务点击
const handleTaskClick = (task) => {
  // 如果completionTimer不为零，表示任务已完成
  if (task.completionTimer) {
    // 保持完成状态
    task.completed = true;
    return;
  }

  // 如果completionTimer为零，设置任务为完成状态
  
  
  // 设置定时器以处理动画效果
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
};

watch(todoDays, () => {
  nextTick(updateMonthHeader); // DOM更新后立即检测月份
});

onMounted(() => {
  nextTick(scrollToToday());
  nextTick(updateMonthHeader); // 替换原有的setTimeout
});
</script>

<style scoped>
* {
  user-select: none;
}
.schedule-sidebar {
  width: 100%;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  height: 80vh; /* 固定高度 */
  display: flex; /* 新增 */
  flex-direction: column; /* 新增 */
}

.month-header {
  padding: 10px;
  position: relative;
  left: 10px;
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}

.schedule-list {
  max-height: 80vh;
  overflow-y: auto;
  flex: 1;
  padding: 10px;
}

.day-schedule {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.089);
  margin-bottom: 15px;
  padding: 15px;
  position: relative;
}
.day-header {
  display: flex;
  align-items: center;
  padding-bottom: 10px;
  margin-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.date-label {
  font-size: 1.2rem;
  font-weight: bold;
  margin-right: 8px;
  color: #333;
}

.today-label {
  background-color: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
  font-size: 0.85rem;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 8px;
}

.tomorrow-label {
  background-color: rgba(10, 132, 255, 0.1);
  color: #0a84ff;
  font-size: 0.85rem;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 8px;
}

.day-name {
  color: #888;
  font-size: 0.9rem;
}

.event-item {
  display: flex;
  padding: 8px 0;
  align-items: center;
  border-radius: 6px;
  position: relative;
  transition: all 0.2s ease;
  cursor: pointer;
}
.event-item:hover  {
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.105);
}
.event-item:active {
  box-shadow: 0px 0px 2px rgba(0, 0, 0, 0.105);
}

.checkmark-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 10px;
  cursor: pointer;
}

.checkmark {
  width: 14px;
  height: 14px;
  border: 1.4px solid #ccc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  --priority-color: #0a84ff; /* 默认优先级颜色 */
}

.checkmark.completed {
  background-color: transparent;
  border-color: var(--priority-color);
}

.checkmark.completed::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 8px;
  height: 8px;
  background-color: var(--priority-color);
  border-radius: 50%;
  transform: translate(-55%, -55%);
}

/* 淡出动画 */
.fade-out {
  animation: fadeOut 0.3s ease-out forwards;
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

/* 淡入动画 */
.fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.checkmark-svg {
  width: 12px;
  height: 12px;
  fill: none;
  stroke: white;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.event-time {
  min-width: 50px;
  color: #999;
  font-size: 0.8rem;
  margin-right: 10px;
}

.start-time, .end-time {
  line-height: 1.4;
}

.event-title {
  flex: 1;
  font-size: 13px;
  color: #333;
}

.event-title.completed {
  text-decoration: line-through;
  color: #999;
}

.today {
  border: 1px solid #0a84ff;
  box-shadow: 0 0 0 1px rgba(10, 132, 255, 0.2);
}

.month-header-container {
  position: sticky;
  top: 10px;
  margin-bottom: 20px;
  z-index: 100;
  height: 40px;
  background: white;
  overflow: hidden;
}


/* 滚动条样式 */
.schedule-list::-webkit-scrollbar {
  width: 6px;
}

.schedule-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.schedule-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.schedule-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.empty-prompt {
  text-align: center;
  color: #999;
  font-style: italic;
  padding: 20px;
  font-size: 14px;
}

/* 暗色主题样式 */
[data-theme="dark"] .schedule-sidebar {
  background-color: #1E1E1E;
  color: #ffffff;
}

[data-theme="dark"] .day-schedule {
  background: #2d2d2d;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

[data-theme="dark"] .day-header {
  border-bottom: 1px solid #484848;
}

[data-theme="dark"] .date-label,
[data-theme="dark"] .day-name,
[data-theme="dark"] .event-title {
  color: #ffffff;
}

[data-theme="dark"] .event-title.completed {
  color: #aaaaaa;
}

[data-theme="dark"] .event-time {
  color: #aaaaaa;
}

[data-theme="dark"] .month-header {
  color: #ffffff;
  background: #1E1E1E;
}

[data-theme="dark"] .month-header-container {
  background: #1E1E1E;
}

[data-theme="dark"] .checkmark {
  border: 1.4px solid #666666;
}

[data-theme="dark"] .schedule-list::-webkit-scrollbar-track {
  background: #2d2d2d;
}

[data-theme="dark"] .schedule-list::-webkit-scrollbar-thumb {
  background: #555555;
}

[data-theme="dark"] .schedule-list::-webkit-scrollbar-thumb:hover {
  background: #777777;
}

[data-theme="dark"] .empty-prompt {
  color: #aaaaaa;
}
</style>