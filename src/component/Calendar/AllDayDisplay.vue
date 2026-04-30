<template>
<div class="all-day-display">
    <div class="allday-tag"> 全天 </div>
    <div class="day-block" v-for="(item, index) in allDayEventsByDay" :key="index">
        <div v-for="event in item" :key="event.id" 
             class="allday-event" 
             :style="getEventStyle(event)"
             @click="selectEvent(event)">
            <div class="event-indicator" :style="getIndicatorStyle(event)"></div>
            <div class="event-title">
                {{ event.title }}
            </div>
        </div>
    </div>
</div>

</template>

<script setup lang="ts">
import { computed} from 'vue'
import { EventData } from '../../stores/Calendar/EventData';
import { ScheduleStore } from '../../stores/Calendar/ScheduleStore';
const useScheduleStore = ScheduleStore();
const useEventData = EventData();

import { ScheduleEvent } from '../../types/schedule';


const allDayEventsByDay = computed(() => {
  const events: ScheduleEvent[][] = [[], [], [], [], [], [], []];
  useEventData.currentWeekEvents.forEach(event => {
    if (event.allDay) {
      const dayIndex = event.start.getDay(); // 0 is Sunday, 1 is Monday, ..., 6 is Saturday
      // Adjust index to make Monday = 0, Sunday = 6
      const adjustedIndex = dayIndex === 0 ? 6 : dayIndex - 1;
      events[adjustedIndex].push(event);
    }
  });
  
  return events;
});
import { ThemeStore } from '../../stores/ThemeStore';
const themeStore = ThemeStore();
const getEventStyle = (event: ScheduleEvent) => {
    if (themeStore.theme === 'dark') {
        const category = useEventData.darkColorMap[useScheduleStore.categories.find((item) => item.name === event.category)?.color || ''];
        if (event.id !== useEventData.currentEvent.id) {
            return {
                backgroundColor: category?.['--shallow'] || '#409EFF',
                color: 'white'
            }
        } else {
            return {
                backgroundColor: category?.['--deep'] || '#409EFF',
                color: 'white'
            }
        }
    } else {
        const category = useEventData.colorMap[useScheduleStore.categories.find((item) => item.name === event.category)?.color || ''];
        if (event.id !== useEventData.currentEvent.id) {
            return {
                backgroundColor: category?.['--shallow'] || '#409EFF',
                color: category?.['--text'] || 'white'
            }
        } else {
            return {
                backgroundColor: category?.['--deep'] || '#409EFF',
                color: 'white'
            }
        }
    }
};

const getIndicatorStyle = (event: ScheduleEvent) => {
    const category = useEventData.colorMap[useScheduleStore.categories.find((item) => item.name === event.category)?.color || ''];
    return {
        backgroundColor: category?.['--deep'] || '#409EFF',
    }
}
const selectEvent = (event: ScheduleEvent) => {
  useScheduleStore.isOperatingForm = false;
  useEventData.currentEvent = event;
  useEventData.selectedRectIndex = useEventData.currentRects.findIndex(e => e.id === event.id);
  useScheduleStore.isShowEventForm = true;
};


</script>
<style scoped>
.all-day-display {
    position: relative;
    display: flex;
    flex-direction: row;
    top: 0;
    left: 0px;
    height: auto;
    min-height: 26px;
    width: 100%;
    padding: 0 0px;
    background: #FFFFFF;
    z-index: 90;
}

[data-theme="dark"] .all-day-display {
    background: #1e1e1e;
}

.allday-tag {
    user-select: none;
    flex-direction: column;
    position: relative;
    text-align: center;
    font-size: 12px;
    color: #999999;
    width: 36px;
    height: auto;
    justify-content: center;
    align-items: center;
    border-bottom: 1px solid #DDDDDD;
    border-left: 1.5px solid #F0F0F0;
}

[data-theme="dark"] .allday-tag {
    color: #666666;
    border-bottom: 1px solid #444444;
    border-left: 1.5px solid #2d2d2d;
}
.day-block {
    display: flex;
    flex-direction: column;
    border-top: none;
    border-right: 1px solid #DDDDDD;
    border-bottom: 1px solid #DDDDDD;
    border-left: 1px solid #DDDDDD;
    flex: 1;
    height: auto;
}

[data-theme="dark"] .day-block {
    border-top: none;
    border-right: 1px solid #444444;
    border-bottom: 1px solid #444444;
    border-left: 1px solid #444444;
}

.allday-event {
    display: flex;
    padding: 2px 4px;
    margin: 2px;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    min-width: 60px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

[data-theme="dark"] .allday-event {
    color: #ffffff;
}

.event-title {
    flex: 1;
}

.event-indicator {
  position: relative;
  width: 3px;
  height: 90%;
  transform: translateY(10%);
  border-radius: 3px;
}

[data-theme="dark"] .event-indicator {
  opacity: 0.8;
}
</style>