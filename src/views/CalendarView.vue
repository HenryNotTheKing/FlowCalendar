<template>
  <div class="sub-left-panel">
    <Calendar />
    <catagoryPicker />
  </div>
  <div class="divideline_left"></div>
  <div class="sub-center-panel">
    <div class="date-title">
      <div class="month-title">{{ formatMonth(useDateDisplay.selectedDate) }}</div>
      <div class="year-title">{{ useDateDisplay.selectedDate.getFullYear() }}</div>
      <div class="to-today" @click="useDateDisplay.toToday()">今天</div>
      <div class="arrow-container">
        <div class="arrow-container-left" @click="useDateDisplay.toLastWeek()">
          <img v-if = "useThemeStore.theme === 'light'" src="../assets/Icons/chevron-left.svg" alt="arrow-left" class="icon" />
          <img v-else src="../assets/Icons/chevron-left-dark.svg" alt="arrow-left" class="icon" />
        </div>
        <div class="arrow-container-right" @click="useDateDisplay.toNextWeek()">
          <img v-if = "useThemeStore.theme === 'light'" src="../assets/Icons/chevron-right.svg" alt="arrow-right" class="icon" />
          <img v-else src="../assets/Icons/chevron-right-dark.svg" alt="arrow-right" class="icon" />
        </div>
      </div>
    </div>
    <DayAxis :timeAxisWidth="timeAxisWidth" />
    <AllDayDisplay />
    <div class="canvas-container-with-axis">
      <div class="time-axis" ref="timeAxisRef">
        <TimeAxis />
      </div>
      <div class="CalendarDisplay" ref="parentRef">
        <CalendarDisplay />
      </div>
    </div>
  </div>
  <div class="sub-right-panel" >
    <div class="divideline_right"></div>
    <EventForm v-if="useScheduleStore.isShowEventForm"/>
    <EventList v-else/>

  </div>
</template>

<script lang='ts' setup>
import CalendarDisplay from '../component/Calendar/CalendarDisplay.vue';
import DayAxis from '../component/Calendar/DayAxis.vue';
import TimeAxis from '../component/Calendar/TimeAxis.vue';
import Calendar from '../component/Calendar/Calendar.vue';
import EventForm from '../component/Calendar/EventForm.vue';
import catagoryPicker from '../component/Calendar/CatagoryPicker.vue';
import AllDayDisplay from '../component/Calendar/AllDayDisplay.vue';
import EventList from '../component/Todolist/EventList.vue';
import { ref, onMounted} from 'vue';
import { DateDisplay } from '../stores/Calendar/DateDisplay';
import { ScheduleStore } from '../stores/Calendar/ScheduleStore';
import { CanvasParams } from '../stores/Calendar/CanvasParams.ts';
import { ThemeStore } from '../stores/ThemeStore';
import { ProjectParams } from '../stores/TodoList/ProjectParams';
import { DocStore } from '../stores/NoteBook/DocumentStore';
const useThemeStore = ThemeStore();
const useProjectParams = ProjectParams();
const docStore = DocStore();
const useScheduleStore = ScheduleStore();
const useDateDisplay = DateDisplay();
const useCanvasParams = CanvasParams();
function formatMonth(date: { getMonth: () => any; }){
  const month = date.getMonth(); // 月份从0开始，所以需要加1
  const Months = [
    '一月', '二月', '三月', '四月', '五月', '六月',
    '七月', '八月', '九月', '十月', '十一月', '十二月'
  ];
  return Months[month];
}
const parentRef = ref(null);
const timeAxisRef = ref(null);

const timeAxisWidth = ref(0);

async function init() {
  // 先初始化项目参数和文档存储

  
  // 然后继续原有的初始化逻辑
  await useScheduleStore.fetchCategories().then(async () => {
    // 获取当前日期前后两周
    const baseDate = new Date(useDateDisplay.selectedDate);
    const datesToLoad = [
      new Date(baseDate.setDate(baseDate.getDate() - 7)), // 前一周
      useDateDisplay.selectedDate,                        // 当前周
      new Date(baseDate.setDate(baseDate.getDate() + 14))  // 后一周
    ];
    
    await Promise.all(datesToLoad.map(date => 
      useScheduleStore.fetchWeekEvents(new Date(date))
    ));
  });
  
  if (useScheduleStore.categories.length === 0) {
    useScheduleStore.createCategory({name: '日程', color: 'Blue'});
  }
  await useProjectParams.init();
  await docStore.initializeDocuments();
}

 onMounted(() => {
  init();

  const resizeObserver = new ResizeObserver((entries) => {
    for (const entry of entries) {
      useCanvasParams.canvasWidth = entry.contentRect.width;
    }
  });
  if (parentRef.value) {
    resizeObserver.observe(parentRef.value);
  }

  const timeAxisObserver = new ResizeObserver((entries) => {
    for (const entry of entries) {
      timeAxisWidth.value = entry.contentRect.width;
    }
  });
  if (timeAxisRef.value) {
    timeAxisObserver.observe(timeAxisRef.value);
  }

  // 在组件卸载时停止监听
  return () => {
    if (parentRef.value) {
      resizeObserver.unobserve(parentRef.value);
    }
  };
});

</script>

<style scoped>
.date-title {
  display: flex; 
  align-items: baseline;
  margin-bottom: 1%;
}
.to-today {
  height: 28px;
  width: 48px;
  background-color: #FBFBFB;
  border-radius: 4px;
  margin-left: auto;
  cursor: pointer;
  border: #d4d4d4 1px solid;
  font-size: 14px;
  color: #000000;
  user-select: none;
  box-shadow: 0px 2px 2px rgba(100, 100, 100, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2px 0 4px 0;
  transition: background-color 0.2s ease;
  transform: translateY(10px);
  &:hover {
    background-color: #dbdbdb;
  }
}

.arrow-container {
  display: flex;
  align-items: center;
  margin-left: 5px;
  margin-right: 10px;
  gap: 6px;
  transform: translateY(13px);
}
.arrow-container-left,.arrow-container-right {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  &:hover {
    background-color: #efefef;
  }
}

.month-title {
 font-size: 30px;
 font-weight: 600;
 margin-left:3%;
 user-select: none;
 margin-right: 5px;
 border-right: 5px;
 align-self: flex-end;
}
.year-title {
  font-size: 24px;
  font-weight: 500;
  user-select: none;
  align-self: flex-end;
}
.canvas-container {
 display: flex; 
}
.canvas-container-with-axis {
  height: 100%;
  width: 100%;
  display: flex;
}
.time-axis {
  width: 36px;
}
.CalendarDisplay {
  width: calc(100% - 36px);
}
.day-axis {
  display: block
}
.icon {
  width: 16px;
  height: 16px;
}

/* 暗色主题样式 */
[data-theme="dark"] .to-today {
  background-color: #2d2d2d;
  border: #444444 1px solid;
  color: #ffffff;
  box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.3);
  &:hover {
    background-color: #3d3d3d;
  }
}

[data-theme="dark"] .arrow-container-left,
[data-theme="dark"] .arrow-container-right {
  &:hover {
    background-color: #3d3d3d;
  }
}

</style>