import { ScheduleEvent, Category } from '../../types/schedule';
import { defineStore } from 'pinia';
import { getWeekRange, getWeekKey, getRectPositionFromTimeRange, RecurrenceService } from '../../utils/dataHelper';
import axios from 'axios';
import { RRule } from 'rrule';
import { ref, computed } from 'vue';
import { EventData } from './EventData';
import { DateDisplay } from './DateDisplay';
import { ElMessageBox } from 'element-plus';
import dayjs from 'dayjs';


export const ScheduleStore = defineStore('schedule', () => {
  const useDateDisplay = DateDisplay();
  const isShowEventForm = ref(false);
  const isOperatingForm = ref(false);

  const weeklyCache = ref(new Map<string, ScheduleEvent[]>());
  const currentWeek = ref<ScheduleEvent[]>([]);//储存从后端获取的中间状态
  const useEventData = EventData();

  const repeatEvents = ref(<ScheduleEvent[]>[]);//储存重复事件

  const categories = ref<Category[]>([]);
  const options = computed(() =>
    categories.value.map(item => ({
      value: item.name,
      label: item.name
    }))
  )

  const hasCachedWeek = computed(() => (currentDate: Date) => {
    return weeklyCache.value.has(getWeekKey(currentDate));
  });

  async function fetchWeekEvents(currentDate: Date) {
    const [weekStart, weekEnd] = getWeekRange(currentDate);
    const cacheKey = getWeekKey(currentDate);

    if (!weeklyCache.value.has(cacheKey)) {
      try {
        const response = await axios.get('/api/events/week', {
          params: {
            start: weekStart.toISOString(),
            end: weekEnd.toISOString()
          }
        });

        const processedEvents = response.data.flatMap((event: ScheduleEvent) => {
          // 转换日期字段
          const baseEvent = {
            ...event,
            start: new Date(event.start),
            end: new Date(event.end),
            exceptions: (event.exceptions as Date[])?.map(d => new Date(d)) || []
          };
          if (event.repeat) {
            if (typeof (event.recurrence.endDate) === 'string') {
              event.recurrence.endDate = new Date(event.recurrence.endDate)
            }
            if (!repeatEvents.value.find(e => e.id === baseEvent.id)){
              repeatEvents.value.push(baseEvent) 
            }
            const maxEndDate = event.recurrence.endCondition === 'untilDate' && event.recurrence.endDate
              ? new Date(Math.min(weekEnd.getTime(), event.recurrence.endDate.getTime()))
              : new Date(weekEnd);
            return RecurrenceService.generateRecurrenceEvents(
              baseEvent,  // 使用转换后的对象
              new Date(weekStart),
              maxEndDate
            ).filter(Boolean);
          } else {
            return [baseEvent];
          }
        });

        weeklyCache.value.set(cacheKey, processedEvents);
      } catch (error) {
        console.error('获取周数据失败:', error);
      }
    }
    currentWeek.value = weeklyCache.value.get(cacheKey) || [];
    return currentWeek.value;
  }

  async function addEvent(newEvent: ScheduleEvent) {
    try {
      if (newEvent.repeat) {
        repeatEvents.value.push(newEvent);
        const recurrenceEvents = RecurrenceService.generateRecurrenceEvents(
          newEvent,
          newEvent.start,
          new Date(newEvent.start.getFullYear() + 1, newEvent.start.getMonth(), newEvent.start.getDate())
        );
        recurrenceEvents.forEach(event => {
          const weekKey = getWeekKey(event.start);
          weeklyCache.value.set(weekKey, [...(weeklyCache.value.get(weekKey) || []), event]);
        });
      } else {
        newEvent.start = new Date(newEvent.start);
        newEvent.end = new Date(newEvent.end);
        const weekKey = getWeekKey(newEvent.start);
        const weekEvents = weeklyCache.value.get(weekKey) || [];
        weeklyCache.value.set(weekKey, [...weekEvents, newEvent]);
      }
      fetchWeekEventsFromCache(useDateDisplay.selectedDate);
      const payload = {
        ...newEvent,
        start: newEvent.start.toISOString(),
        end: newEvent.end.toISOString(),
        exceptions: newEvent.exceptions?.map(d => d.toISOString()) || []
      };
      await axios.post('/api/events', payload);

    } catch (error) {
      console.error('创建事件失败:', error);
      throw error;
    }
  }

  async function addEventFromAi(newEvent: ScheduleEvent) {
    if(!categories.value.some(c => c.name === newEvent.category)){
      const newCategory = {
        name: newEvent.category,
        color: 'Blue'
      }
      createCategory(newCategory)
    }
    // 转换为 UTC+8 时区
    const start = new Date(newEvent.start);
    const end = new Date(newEvent.end);
    
    // 减去8小时以转换为utc标准时区
    start.setHours(start.getHours() - 8);
    end.setHours(end.getHours() - 8);
    
    const payload = {
      ...newEvent,
      id: crypto.randomUUID(),
      start: start,
      end: end,
      lastState: undefined,
      exceptions: newEvent.exceptions?.map(d => new Date(d)) || []
    }
    
    addEvent(payload);
  }


  async function updateRepeatEvent(newEvent: ScheduleEvent) {
    if (!newEvent.originalEventId) {
      const existingEvent = repeatEvents.value.find(e => e.id === newEvent.id);
      if (!existingEvent) {
        repeatEvents.value.push(newEvent);
        weeklyCache.value.forEach((events, weekKey) => {
          const filtered = events.filter(event => event.id !== newEvent.id);
          weeklyCache.value.set(weekKey, filtered);
        });
        // 保存到后端
        const payload = {
          ...newEvent,
          start: newEvent.start.toISOString(),
          end: newEvent.end.toISOString(),
        };
        axios.put(`/api/events/${newEvent.id}`, payload);
      }
      // 生成副本显示
      const recurrenceEvents = RecurrenceService.generateRecurrenceEvents(
        newEvent,
        newEvent.start,
        new Date(newEvent.start.getFullYear() + 1, newEvent.start.getMonth(), newEvent.start.getDate())
      );
      recurrenceEvents.forEach(event => {
        const weekKey = getWeekKey(event.start);
        weeklyCache.value.set(weekKey, [...(weeklyCache.value.get(weekKey) || []), event]);
      });
      fetchWeekEventsFromCache(useDateDisplay.selectedDate);
      return;
    }


    await ElMessageBox.confirm(
      '请选择操作方式:',
      '编辑重复事件',
      {
        distinguishCancelAndClose: true,
        confirmButtonText: '仅修改本次',
        cancelButtonText: '修改所有',
        type: 'warning'
      }
    ).then(async (result) => {
      if (result === 'confirm') {
        const originalEvent = repeatEvents.value.find(event => event.id === newEvent.originalEventId);
        if (!originalEvent) throw new Error('找不到原始事件');
        useEventData.selectedRectIndex = -1;

        // 添加例外日期
        const { updatedOriginal, independentEvent } = RecurrenceService.editOccurrence(
          originalEvent,
          newEvent,
        );

        const eventIndex = repeatEvents.value.findIndex(event => event.id === updatedOriginal.id);
        if (eventIndex !== -1) {
          repeatEvents.value[eventIndex] = { ...updatedOriginal };
        }

        // 更新缓存
        weeklyCache.value.forEach((events, weekKey) => {
          weeklyCache.value.set(weekKey, events.filter(e => (e.originalEventId !== originalEvent.id) || !e.repeat))
        });
        // 生成新重复事件
        const recurrenceEvents = RecurrenceService.generateRecurrenceEvents(
          updatedOriginal,
          updatedOriginal.start,
          new Date(updatedOriginal.start.getFullYear() + 1, updatedOriginal.start.getMonth(), updatedOriginal.start.getDate())
        ).filter(Boolean);

        // 更新缓存和后端
        recurrenceEvents.forEach(event => {
          const weekKey = getWeekKey(event.start);
          weeklyCache.value.set(weekKey, [...(weeklyCache.value.get(weekKey) || []), event]);
        });

        const payload = {
          ...updatedOriginal,
          start: updatedOriginal.start.toISOString(),
          end: updatedOriginal.end.toISOString(),
        };

        await addEvent(independentEvent); // 添加独立事件
        fetchWeekEventsFromCache(useDateDisplay.selectedDate);
        await axios.put(`/api/events/${originalEvent.id}`, payload);
        return;
      }
    }).catch((action: string) => {
      if (action === 'cancel') {

        const originalId = newEvent.originalEventId;
        if (!originalId) return;

        const originalEvent = repeatEvents.value.find(event => event.id === newEvent.originalEventId);
        if (!originalEvent) throw new Error('找不到关联的原始事件');

        if (!newEvent.lastState) {
          throw new Error('原始事件缺少 lastState');
        }
        const deltaTime = newEvent.start.getTime() - newEvent.lastState.start.getTime();
        // 应用时间差到原始事件
        const mergedEvent = {
          ...originalEvent,
          repeat: true,
          start: new Date(originalEvent.start.getTime() + deltaTime),
          end: new Date(originalEvent.end.getTime() + deltaTime),
          title: newEvent.title,
          description: newEvent.description,
          location: newEvent.location,
          category: newEvent.category,
          exceptions: originalEvent.exceptions?.map(d => new Date(d.getTime() + deltaTime)),
          recurrence:{
            ...originalEvent.recurrence,
            daysOfWeek: newEvent.recurrence.type === 'weekly' ? [dayjs(new Date(originalEvent.start.getTime() + deltaTime)).day()] : []

          }
        };


        weeklyCache.value.forEach((events, weekKey) => {
          weeklyCache.value.set(weekKey, events.filter(e => (e.originalEventId !== originalId) || !e.repeat))
        });

        // 生成新重复事件
        const recurrenceEvents = RecurrenceService.generateRecurrenceEvents(
          mergedEvent,
          mergedEvent.start,
          new Date(mergedEvent.start.getFullYear() + 1, mergedEvent.start.getMonth(), mergedEvent.start.getDate())
        ).filter(Boolean);

        // 更新缓存和后端
        const eventIndex = repeatEvents.value.findIndex(event => event.id === mergedEvent.id);
        if (eventIndex !== -1) {
          repeatEvents.value[eventIndex] = { ...mergedEvent };
        }
        recurrenceEvents.forEach(event => {
          const weekKey = getWeekKey(event.start);
          weeklyCache.value.set(weekKey, [...(weeklyCache.value.get(weekKey) || []), event]);
        });
        useEventData.selectedRectIndex = -1;

        fetchWeekEventsFromCache(useDateDisplay.selectedDate);
        // 更新后端
        const payload = {
          ...mergedEvent,
          start: mergedEvent.start.toISOString(),
          end: mergedEvent.end.toISOString(),
        };
        axios.put(`/api/events/${originalId}`, payload);
        return;
      } else if (action === 'close') {
        fetchWeekEventsFromCache(useDateDisplay.selectedDate);
      }
    }
    );
  }

  async function updateRegularEvent(newEvent: ScheduleEvent) {
    // 获取事件应该属于的周
    const eventWeeks = getEventWeeks(newEvent);
    
    // 只在事件实际所属的周中更新事件
    eventWeeks.forEach(weekKey => {
      const events = weeklyCache.value.get(weekKey) || [];
      const filtered = events.filter(e => e.id !== newEvent.id);
      if (!newEvent.repeat) {
        filtered.push(newEvent);
        useEventData.selectedRectIndex = filtered.length - 1;
      }
      weeklyCache.value.set(weekKey, filtered);
    });
    fetchWeekEventsFromCache(useDateDisplay.selectedDate);
    const payload_ = {
      ...newEvent,
      start: newEvent.start.toISOString(),
      end: newEvent.end.toISOString(),
    };
 
    await axios.put(`/api/events/${newEvent.id}`, payload_);
  };

  async function deleteEvent(deleteEvent: ScheduleEvent, isDeleteAll: boolean = false) {
    try {
      if (deleteEvent.repeat && !isDeleteAll) {
        
        const originalId = deleteEvent.originalEventId;
        const originalEvent = repeatEvents.value.find(event => event.id === originalId);
        if (!originalEvent) throw new Error('找不到原始事件');

        weeklyCache.value.forEach((events, weekKey) => {
          weeklyCache.value.set(weekKey, events.filter(e => (e.id !== deleteEvent.id)))
        });
        if (!originalEvent) {
          throw new Error('找不到关联的原始事件');
        }

        // 生成添加例外后的新原始事件
        const updatedOriginal = RecurrenceService.deleteOccurrence(
          originalEvent,
          deleteEvent.start
        );

        const eventIndex = repeatEvents.value.findIndex(event => event.id === updatedOriginal.id);
        if (eventIndex !== -1) {
          repeatEvents.value[eventIndex] = { ...updatedOriginal };
        }
        fetchWeekEventsFromCache(useDateDisplay.selectedDate);
        await axios.put(`/api/events/${originalEvent.id}`, updatedOriginal);
      }
      else {
        if (isDeleteAll) {
          weeklyCache.value.forEach((events, weekKey) => {
            const filtered = events.filter(event => (event.originalEventId !== deleteEvent.originalEventId) || !event.repeat);
            weeklyCache.value.set(weekKey, filtered);
          });
          fetchWeekEventsFromCache(useDateDisplay.selectedDate);
          await axios.delete(`/api/events/${deleteEvent.originalEventId}`);
        } else {
          weeklyCache.value.forEach((events, weekKey) => {
            const filtered = events.filter(event => event.id !== deleteEvent.id);
            weeklyCache.value.set(weekKey, filtered);
          });
          fetchWeekEventsFromCache(useDateDisplay.selectedDate);
          await axios.delete(`/api/events/${deleteEvent.id}`);
        }
      }
    } catch (error) {
      console.error('删除事件失败:', error);
      throw error;
    }
  }



  function getEventWeeks(event: ScheduleEvent): string[] {
    const weeks = new Set<string>();
    const [start, end] = [new Date(event.start), new Date(event.end)];

    //处理重复规则
    function generateRRuleOptions(recurrence: any, start: Date) {
      const options = {
         freq: RRule[recurrence.type.toUpperCase() as keyof typeof RRule],
        dtstart: start,
        interval: recurrence.interval,
        ...(recurrence.type === 'weekly' && recurrence.daysOfWeek && {
          byweekday: recurrence.daysOfWeek.map((day: number) => (day + 6) % 7)
        }),
      };

      switch (recurrence.endCondition) {
        case 'untilDate':
          if (!recurrence.endDate) throw new Error('endDate is required for "untilDate"');
          return { ...options, until: new Date(recurrence.endDate) };
        case 'occurrences':
          if (!recurrence.occurrences) throw new Error('occurrences is required for "occurrences"');
          return { ...options, count: recurrence.occurrences };
        case 'never':
          return options;
        default:
          throw new Error(`Invalid endCondition: ${recurrence.endCondition}`);
      }
    }

    if (event.repeat && event.recurrence) {
      const ruleOptions = generateRRuleOptions(event.recurrence, start);
      const rule = new RRule(ruleOptions);
      rule.all().forEach(occurrence => weeks.add(getWeekKey(occurrence)));
    } else {
      const currentDate = new Date(start);
      while (currentDate <= end) {
        weeks.add(getWeekKey(currentDate));
        currentDate.setDate(currentDate.getDate() + 1);
      }
    }

    return Array.from(weeks);
  }

  async function fetchWeekEventsFromBackend(currentDate: Date) {
    try {
      const currentWeekEvents = await fetchWeekEvents(currentDate);
      if (currentWeekEvents) {
        useEventData.currentWeekEvents = [...currentWeekEvents]; // 创建新数组
        useEventData.currentRects = currentWeekEvents.filter(Boolean).map(event =>
          getRectPositionFromTimeRange(event)
        );
      }
    } catch (error) {
      console.error('初始化周显示失败:', error);
    }
  }

  function fetchWeekEventsFromCache(currentDate: Date) {
    const weekKey = getWeekKey(currentDate);
    const cachedWeekEvents = weeklyCache.value.get(weekKey);
    if (!cachedWeekEvents) {
      return;
    }

    useEventData.currentWeekEvents = [...cachedWeekEvents];
    useEventData.currentRects = cachedWeekEvents
      ? cachedWeekEvents.map(getRectPositionFromTimeRange)
      : [];
  }

  async function updateWeekEvents(currentDate: Date) {
    try {
      const weekkey = getWeekKey(currentDate);
      if (weeklyCache.value.has(weekkey)) {
        fetchWeekEventsFromCache(currentDate);
      }
      else {
        fetchWeekEventsFromBackend(currentDate);
      }
    }
    catch (error) {
      console.error('更新周事件失败:', error);
      throw error;

    }
  }
  function clearWeekCache(event: ScheduleEvent) {
    const weeks = getEventWeeks(event);
    weeks.forEach(weekKey => {
      weeklyCache.value.delete(weekKey)
    })
    useEventData.currentWeekEvents = []       // 清空当前显示的事件
  }

  const fetchCategories = async () => {
    try {
      const response = await axios.get('/api/categories');
      // 添加数据校验
      if (!Array.isArray(response.data)) {
        throw new Error('无效的分类数据格式');
      }

      categories.value = response.data.map((c: any) => ({
        id: c.id,
        name: c.name || '新类别', // 防止空值
        color: c.color || 'Blue',  // 添加默认颜色
        displayName: c.displayName || '新类别' // 添加显示名称
      }));
      // 确保至少有一个默认分类

    } catch (error) {
      console.error('获取分类失败:', error);
      // 可以添加用户通知
    }
  };
  // 创建分类（带临时ID和回滚机制）
  const createCategory = async (payload: Omit<Category, 'id'>) => {
    const tempId = -Date.now(); // 生成临时ID
    const tempCategory = { ...payload, id: tempId };

    try {
      // 立即添加临时分类
      categories.value.push(tempCategory);

      // 发送请求
      const response = await axios.post('/api/categories', payload);
      const savedCategory = response.data;

      // 替换临时分类
      const index = categories.value.findIndex(c => c.id === tempId);
      if (index !== -1) {
        categories.value[index] = savedCategory;
      }

      return savedCategory;
    } catch (error) {
      // 回滚删除临时分类
      categories.value = categories.value.filter(c => c.id !== tempId);
      console.error('创建分类失败:', error);
      throw error;
    }
  };

  // 更新分类（带状态回滚）
  const updateCategory = async (id: number, updates: Partial<Category>) => {
    const original = categories.value.find(c => c.id === id);
    if (!original) return;

    try {
      // 立即应用更新
      const updated = { ...original, ...updates };
      const index = categories.value.findIndex(c => c.id === id);
      if (index !== -1) {
        categories.value[index] = updated;
      }

      await axios.put(`/api/categories/${id}`, updates);
    } catch (error) {
      // 恢复原始状态
      if (original) {
        const index = categories.value.findIndex(c => c.id === id);
        if (index !== -1) {
          categories.value[index] = original;
        }
      }
      console.error('更新分类失败:', error);
      throw error;
    }
  };

  // 删除分类（带恢复机制）
  const deleteCategory = async (id: number) => {
    const backup = categories.value.find(c => c.id === id);

    try {

      categories.value = categories.value.filter(c => c.id !== id);
      
      await axios.delete(`/api/categories/${id}`);
    } catch (error) {
      // 恢复数据
      if (backup) {
        categories.value.push(backup);
      }
      console.error('删除分类失败:', error);
      throw error;
    }
  };

  return {
    isShowEventForm,
    isOperatingForm,
    weeklyCache,
    hasCachedWeek,
    categories,
    options,
    repeatEvents,
    fetchWeekEvents,
    addEvent,
    getEventWeeks,
    updateRepeatEvent,
    updateRegularEvent,
    deleteEvent,
    updateWeekEvents,
    clearWeekCache,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    fetchWeekEventsFromBackend,
    addEventFromAi
  };
});