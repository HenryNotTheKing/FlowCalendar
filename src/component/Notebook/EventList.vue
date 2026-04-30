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
      <!-- 每天日程区块 -->
      <div v-if="scheduleDays.length > 0">
        <div v-for="day in scheduleDays" :key="day.id" class="day-schedule" :data-month="getMonthKey(day.id)">
          <!-- 日期标题区 -->
          <div class="day-header">
            <span class="date-label">{{ day.dateLabel }}</span>
            <span v-if="day.isToday" class="today-label">今天</span>
            <span v-if="day.isTomorrow" class="tomorrow-label">明天</span>
            <span class="day-name">{{ day.dayName }}</span>
          </div>

          <!-- 日程项目列表 -->
          <div v-for="event in day.events" :key="event.id" class="event-item" @click="handleEventClick(event.id, event.title, event.date)" >
            <!-- 左侧时间标示线 -->
            <div class="event-indicator" :style="{
              backgroundColor: event.category
                ? getCategoryColor(event.category)
                : '#0a84ff'
            }"></div>
            <!-- 时间信息 -->
            <div class="event-time">
              <template v-if="event.isAllDay">
                全天
              </template>
              <template v-else>
                <div class="start-time">{{ event.startTime }}</div>
                <div v-if="event.endTime" class="end-time">{{ event.endTime }}</div>
              </template>
            </div>

            <!-- 日程内容 -->
            <div class="event-title">{{ event.title }}</div>
          </div>
        </div>
      </div>
      <!-- 空提示 -->
      <div v-else class="empty-prompt">
        暂无日程安排
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick} from 'vue';
import { ScheduleStore } from '../../stores/Calendar/ScheduleStore';
import { EventData } from '../../stores/Calendar/EventData';
import { DateDisplay } from '../../stores/Calendar/DateDisplay';
import { getWeekKey } from '../../utils/dataHelper';
const useScheduleStore = ScheduleStore();
const useEventData = EventData();
const useDateDisplay = DateDisplay();


import { DocStore } from '../../stores/NoteBook/DocumentStore'
import { SideBarParams } from '../../stores/NoteBook/SideBarParams'
const docStore = DocStore()
const useSideBarParams = SideBarParams()

const createDocumentFromEvent = (eventId, eventName = '未命名事件', eventStart) => {

  docStore.createDocumentFromEvent(eventId, eventName, eventStart)
  useSideBarParams.isShowTodo = false
  useSideBarParams.isShowRecycleBin = false;
  useSideBarParams.showDocumentList = false;
  useSideBarParams.isShowPage = true
}

const handleEventClick = (eventId, eventName = '未命名事件', eventStart) => {
  // 检查文档是否已存在
  const existingDoc = docStore.findDocByEventId(eventId);
  
  if (existingDoc) {
    // 如果文档已存在，打开它
    docStore.currentDocId = existingDoc.id;
    docStore.docChanged = !docStore.docChanged
    useSideBarParams.resetViews()
    useSideBarParams.isShowPage = true;
  } else {
    // 如果文档不存在，创建新文档
    docStore.createDocumentFromEvent(eventId, eventName, eventStart);
  }
}

const getCategoryColor = (categoryName) => {
  const category = useScheduleStore.categories.find(c => c.name === categoryName);
  if (!category) return '#0a84ff';
  
  const color = useEventData.colorOptions.find(c => Object.keys(c)[0] === category.color);
  
  // 3. 返回颜色值或默认值
  return color ? Object.values(color)[0] : '#0a84ff';
};

// 从weeklyCache生成日程数据
const scheduleDays = computed(() => {
  const daysMap = new Map();
  
  useScheduleStore.weeklyCache.forEach((weekEvents) => {
    weekEvents.forEach(event => {
      // 修复：使用本地时区生成日期
    const eventDate = new Date(event.start);
    const dateKey = `${eventDate.getFullYear()}-${(eventDate.getMonth()+1).toString().padStart(2,'0')}-${eventDate.getDate().toString().padStart(2,'0')}`;
      
      if (!daysMap.has(dateKey)) {
        daysMap.set(dateKey, createDayData(eventDate));
      }
      
      const dayData = daysMap.get(dateKey);
      dayData.events.push(createEventData(event));
    });
  });

  // 修复：使用数值比较代替Date对象比较
  return Array.from(daysMap.values())
    .sort((a, b) => {
      const aDate = a.id.split('-').map(Number);
      const bDate = b.id.split('-').map(Number);
      return aDate[0] - bDate[0] || aDate[1] - bDate[1] || aDate[2] - bDate[2];
    })
    .map(day => ({
      ...day,
      events: day.events.sort((a, b) => {
        // 全天事件排在最前面
        if (a.isAllDay && !b.isAllDay) return -1;
        if (!a.isAllDay && b.isAllDay) return 1;
        
        // 比较时间戳（将时间转换为分钟数进行排序）
        const getMinutes = (time) => {
          if (!time) return 0;
          const [hours, minutes] = time.split(':').map(Number);
          return hours * 60 + minutes;
        };
        
        return getMinutes(a.startTime) - getMinutes(b.startTime);
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
    events: []
  };
}

// 创建事件数据
function createEventData(event) {
  return {
    id: event.id,
    title: event.title,
    date: event.start,
    isAllDay: isAllDayEvent(event),
    startTime: formatTime(event.start),
    category: event.category || '',
    endTime: event.end ? formatTime(event.end) : ''
  };
}

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

const isAllDayEvent = (event) => {
  const start = event.start;
  const end = event.end;
  return start.getHours() === 0 && start.getMinutes() === 0 &&
         (!end || (end.getHours() === 0 && end.getMinutes() === 0));
};

const formatTime = (date) => 
  date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });

  // 新增响应式变量
const scrollContainer = ref(null)
const currentMonth = ref('')
const prevMonthKey = ref('')
const monthTransition = ref('slide-up')

// 获取月份唯一标识
const getMonthKey = (dateString) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}-${date.getMonth()}`
}

// 处理滚动事件（添加节流）
let scrollTimer = null
let scrollCheckTimer = null;
const handleScroll = () => {
  clearTimeout(scrollCheckTimer);
  scrollCheckTimer = setTimeout(() => {
    const container = scrollContainer.value;
    if (container) {
      // 3. 动态调整缓冲区间
      const dynamicBuffer = Math.max(50, container.clientHeight * 0.4);
      const { scrollTop, scrollHeight, clientHeight } = container;
      
      if (scrollTop < dynamicBuffer) {
        loadPreviousWeeks(4);
      }
      
      if (scrollHeight - (scrollTop + clientHeight) < dynamicBuffer) {
        loadNextWeeks(4);
      }
    }
    updateMonthHeader();
  }, 50);
};


// 更新月份标题
const updateMonthHeader = () => {
  const days = [...scrollContainer.value.querySelectorAll('.day-schedule')]
  const visibleDays = days.filter(el => {
    const rect = el.getBoundingClientRect()
    return rect.top >= 40 && rect.bottom <= window.innerHeight
  })

  if (visibleDays.length > 0) {
    const currentDay = visibleDays[0]
    const newMonthKey = currentDay.dataset.month
    const [year, month] = newMonthKey.split('-')
    const newMonth = `${year}年${parseInt(month) + 1}月`

    if (newMonthKey !== prevMonthKey.value) {
      // 判断滚动方向
      const oldDate = prevMonthKey.value ? new Date(prevMonthKey.value.replace('-', '/')) : null
      const newDate = new Date(newMonthKey.replace('-', '/'))
      
      monthTransition.value = newDate > oldDate ? 'slide-up' : 'slide-down'
      prevMonthKey.value = newMonthKey
      currentMonth.value = newMonth
    }
  }
}

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

const loadedWeeks = ref(new Set()); // 跟踪已加载周
const isLoading = ref(false);
const bufferPx = 50;

// 新的加载检测逻辑
const checkLoadMore = () => {
  const container = scrollContainer.value;
  if (!container) return;

  const { scrollTop, scrollHeight, clientHeight } = container;
  
  // 顶部加载
  if (scrollTop < bufferPx) {
    loadPreviousWeeks(3); // 加载前2周
  }
  
  // 底部加载
  if (scrollHeight - (scrollTop + clientHeight) < bufferPx) {
    loadNextWeeks(3); // 加载后6周
  }
};

const scrollPosition = ref(0);
const containerHeight = ref(0);

// 加载前序周（复用现有方法）
const loadPreviousWeeks = async (weeks = 3) => {
  if (isLoading.value) return;
  
  const container = scrollContainer.value;
  if (container) {
    scrollPosition.value = container.scrollTop;
    containerHeight.value = container.scrollHeight;
  }


  isLoading.value = true;
  try {
    let loadCount = 0;
    const datesToLoad = [];
    
    // 生成需要加载的日期
    Array.from({ length: weeks }).forEach((_, i) => {
      const date = new Date(useDateDisplay.selectedDate);
      date.setDate(date.getDate() - 7 * (i + 1));
      datesToLoad.push(date);
    });

    // 并行加载周数据
    await Promise.all(datesToLoad.map(async date => {
      if (!loadedWeeks.value.has(getWeekKey(date))) {
        await useScheduleStore.fetchWeekEvents(date);
        loadedWeeks.value.add(getWeekKey(date));
        loadCount++;
      }
    }));

    // 如果全部周都已缓存，停止加载
    if (loadCount === 1) return;
    
  } finally {
    isLoading.value = false;
    nextTick(() => {
      // 2. 计算高度差并补偿滚动位置
      if (container) {
        const newHeight = container.scrollHeight;
        container.scrollTop = scrollPosition.value + (newHeight - containerHeight.value);
      }
    });
  }
};

// 加载后续周（复用现有方法）
const loadNextWeeks = async (weeks = 3) => {
  if (isLoading.value) return;

  const container = scrollContainer.value;
  if (container) {
    scrollPosition.value = container.scrollTop;
    containerHeight.value = container.scrollHeight;
  }
  isLoading.value = true;
  try {
    let loadCount = 0;
    
    for (let i = 1; i <= weeks; i++) {
      const date = new Date(useDateDisplay.selectedDate);
      date.setDate(date.getDate() + 7 * i);
      
      if (!loadedWeeks.value.has(getWeekKey(date))) {
        await useScheduleStore.fetchWeekEvents(date);
        loadedWeeks.value.add(getWeekKey(date));
        loadCount++;
        
        // 如果连续两周无新数据，停止加载
        if (loadCount === 1) break;
      }
    }
    
  } finally {
    isLoading.value = false;
    nextTick(() => {
      // 2. 计算高度差并补偿滚动位置
      if (container) {
        const newHeight = container.scrollHeight;
        container.scrollTop = scrollPosition.value + (newHeight - containerHeight.value);
      }
    });
  }
};
watch(scheduleDays, () => {
  nextTick(updateMonthHeader) // DOM更新后立即检测月份
})

onMounted(() => {
  nextTick(scrollToToday())
  nextTick(updateMonthHeader) // 替换原有的setTimeout
})
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
}
.event-item:hover  {
  box-shadow: 0.5px 1.5px 5px rgba(0, 0, 0, 0.105);
  transform: translateY(-3px);
}
.event-item:active {
  transform: translateY(-2px);
  box-shadow: 0px 0px 2px rgba(0, 0, 0, 0.105);
}
.event-indicator {
  position: absolute;
  width: 3px;
  height: 70%;
  border-radius: 3px;
}

.event-time {
  min-width: 50px;
  color: #999;
  font-size: 0.8rem;
  margin-left: 15px;
}

.start-time, .end-time {
  line-height: 1.4;
}

.event-title {
  flex: 1;
  padding-left: 12px;
  font-size: 13px;
  color: #333;
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
  background-color: #1e1e1e;
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

[data-theme="dark"] .event-time {
  color: #aaaaaa;
}

[data-theme="dark"] .month-header {
  color: #ffffff;
  background: #1e1e1e;
}

[data-theme="dark"] .month-header-container {
  background: #1e1e1e;
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