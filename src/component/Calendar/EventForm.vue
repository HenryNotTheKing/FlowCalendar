<template>
    <div class="event-form">
        <el-form :model="useEventData.currentEvent" label-width="auto" style="max-width: 300px">
            <el-form-item label="类别" label-position="top">
                <el-select 
                    v-model="useEventData.currentEvent.category" 
                    placeholder="请选择" 
                    class="custom-select"
                    id="category">
                    <el-option v-for="item in useScheduleStore.options" :key="item.value" :label="item.label" :value="item.value"
                        class="custom-option" />
                </el-select>
            </el-form-item>
            <el-form-item label="标题" label-position="top">
                <el-input 
                    v-model="useEventData.currentEvent.title"
                    id="title"
                />
            </el-form-item>
            <el-form-item label="时间" v-if="!useEventData.currentEvent.allDay">
                <el-col :span="10">
                    <el-time-picker v-model="useEventData.currentEvent.start" format="HH:mm" :show-seconds="false" placeholder="开始"
                        style="width: 100%; font-size: 13px" :clearable="false" :disabled-hours="disableStartHours" :disabled-minutes="disableStartMinutes" class="custom-time-picker"/>
                </el-col>
                <el-col :span="4" class="text-center">
                    <div style="display: flex; justify-content: center; color: #3d3d3d">-</div>
                </el-col>
                <el-col :span="10">
                    <el-time-picker v-model="useEventData.currentEvent.end" format="HH:mm" :show-seconds="false" placeholder="结束"
                        style="width: 100%; font-size: 13px" :clearable="false"  :disabled-hours="disableEndHours" :disabled-minutes="disableEndMinutes" class="custom-time-picker"/>
                </el-col>
                <el-col :span="24">
                    <el-form-item style="margin-left: 0">
                        <el-text type="info">
                            {{ durationText }}
                        </el-text>
                    </el-form-item>
                </el-col>
                <el-col :span="24">
                    <el-form-item style="margin-left: 0">
                        <el-text type="info" v-if="useEventData.currentEvent.start">
                            {{ dayjs(useEventData.currentEvent.start).format('YYYY年MM月DD日') }}
                        </el-text>
                    </el-form-item>
                </el-col>
            </el-form-item>
            <el-form-item>
                <el-col :span="10">
                    <el-form-item label="全天">
                        <el-switch 
                            @change="handleAllDayChange"
                            v-model="useEventData.currentEvent.allDay" 
                            id="allDay"
                        />
                    </el-form-item>
                </el-col>
                <el-col :span="8" v-if="!useEventData.currentEvent.repeat">
                    <el-form-item label="重复" >
                        <el-switch v-model="useEventData.currentEvent.repeat" @change="handleRepeatSwitch" :disabled="showRepeatDialog" />
                    </el-form-item>
                </el-col>
                <el-col :span="12" v-if="useEventData.currentEvent.repeat">
                    <el-form-item label=" ">
                        <div class="modify-btn" @click="handleModifyRepeat">修改重复</div>
                    </el-form-item>
                </el-col>
            </el-form-item>
            <el-form-item label="地点">
                <el-input v-model="useEventData.currentEvent.location" type="textarea"/>
            </el-form-item>
            <el-form-item label="描述">
                <el-input v-model="useEventData.currentEvent.description" type="textarea" :autosize="{ minRows: 2 }"/>
            </el-form-item>
        </el-form>

        <el-dialog v-model="showRepeatDialog" title="设置重复规则" width="600px" destroy-on-close :append-to-body="true"
            :modal-append-to-body="true" @close='cancel'>
            <el-form :model="dialogRecurrence" label-width="100px">
                <!-- 重复类型 -->
                <el-form-item label="重复类型">
                    <el-select v-model="dialogRecurrence.type" placeholder="请选择">
                        <el-option v-for="(item, index) in repeatTypes" :key="index" 
                         :label="item.label" :value="item.value"/>
                    </el-select>
                </el-form-item>

                <!-- 间隔周期 -->
                <el-form-item label="每">
                    <el-input-number v-model="dialogRecurrence.interval" :min="1" :max="365" />
                    <span :style="{ color: '#606266', marginLeft: '10px'}">
                        {{ dialogRecurrence.type === "yearly" ? '年' : ((dialogRecurrence.type ==="monthly") ? '月' : (dialogRecurrence.type === "weekly" ? '周' : '天')) }}
                    </span>

                </el-form-item>

                <!-- 结束条件 -->
                <el-form-item label="结束条件">
                    <el-radio-group v-model="dialogRecurrence.endCondition">
                        <el-radio value="never">永不</el-radio>
                        <el-radio value="occurrences">重复次数</el-radio>
                        <el-radio value="untilDate">结束日期</el-radio>
                    </el-radio-group>
                </el-form-item>

                <!-- 次数输入 -->
                <el-form-item v-if="dialogRecurrence.endCondition === 'occurrences'" label="重复次数">
                    <el-input-number v-model="dialogRecurrence.occurrences" :min="1" :max="999" />
                </el-form-item>

                <!-- 结束日期 -->
                <el-form-item v-if="dialogRecurrence.endCondition === 'untilDate'" label="结束日期">
                    <el-date-picker v-model="dialogRecurrence.endDate" placeholder="选择结束日期" 
                    :disabled-date="(date: Date) => {
                      const start = useEventData.currentEvent.start;
                     return start ? date < new Date(new Date(start).setHours(0,0,0,0)) : false;
                    }"/>
                </el-form-item>
            </el-form>

            <template #footer>
                <el-button @click="cancel">取消</el-button>
                <el-button type="primary" @click="confirmRepeat">确定</el-button>
            </template>
        </el-dialog> 
    </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import dayjs from 'dayjs'
import { ScheduleStore } from '../../stores/Calendar/ScheduleStore'
import { EventData } from '../../stores/Calendar/EventData';
import { cloneDeep } from 'lodash-es'
import type { RecurrenceRule } from '../../types/schedule';
const useEventData = EventData();
const useScheduleStore = ScheduleStore();

const isConfirmed = ref(false);

const dateToWeekDay = (date: Date) => {
    return dayjs(date).day();
}

const confirmRepeat = () => {
    Object.assign(useEventData.currentEvent.recurrence, {
        ...dialogRecurrence.value,
        interval: Number(dialogRecurrence.value.interval),
        endDate: dialogRecurrence.value.endDate ? dayjs(dialogRecurrence.value.endDate).add(1, 'day').toDate() : null,
        daysOfWeek: dialogRecurrence.value.type === 'weekly' ? [dateToWeekDay(useEventData.currentEvent.start)] : []
    });
    console.log(useEventData.currentEvent.recurrence.daysOfWeek)
    // 标记为确认状态
    isConfirmed.value = true;
    showRepeatDialog.value = false;
    readyToUpdate.value = true;
}

function cancel() {
    showRepeatDialog.value = false;
    
    // 仅在非确认状态下重置状态
    if (!isConfirmed.value) {
        useEventData.currentEvent.repeat = false;
        dialogRecurrence.value = useEventData.resetRecurrence();
        if (useEventData.currentEvent.originalEventId === '') {
            useEventData.currentEvent.repeat = false;
        }
    }
    
    // 重置确认标记
    isConfirmed.value = false;
}
// 专门用于对话框的重复规则缓存



const dialogRecurrence = ref<RecurrenceRule>(cloneDeep({...useEventData.currentEvent.recurrence, interval: 1,}));




const readyToUpdate = ref(false);

watch(() => useEventData.currentEvent, (newVal) => {
    if (useEventData.selectedRectIndex !== -1 && useEventData.currentWeekEvents.find((event) => event.id === useEventData.currentRects[useEventData.selectedRectIndex].id) && useScheduleStore.isOperatingForm) {
        newVal = {
            ...newVal,
            start: new Date(newVal.start),
            end: new Date(newVal.end),
        }
        if (newVal.title === '') {
            newVal = {
                ...newVal,
                title: '新事项',
            }
        }
        if ((newVal.repeat && readyToUpdate.value) || (newVal.repeat && !showRepeatDialog.value)) {
            useScheduleStore.updateRepeatEvent(newVal);
            readyToUpdate.value = false;
        }else if (!newVal.repeat) {
            useScheduleStore.updateRegularEvent(newVal);
        }
    }
}, { deep: true, immediate: true });
// 修复 1: 明确表单类型

const showRepeatDialog = ref(false)

// 可用选项
const repeatTypes = [
    { value: 'daily', label: '每天' },
    { value: 'weekly', label: '每周' },
    { value: 'monthly', label: '每月' },
    { value: 'yearly', label: '每年' }
]


import { getRectPositionFromTimeRange } from '../../utils/dataHelper';

const handleAllDayChange = (val: boolean) => {
    console.log(val);
    if (val) {
        // 当事件变成全天事件时，找到currentRects里id等于currentEvent.id的矩形，将其三个数值都改成0，id保持不变
        useEventData.currentRects = useEventData.currentRects.map((rect) => {
            if (rect.id === useEventData.currentEvent.id) {
                return {
                    ...rect,
                    column: -1,
                    startRow: 0,
                    rowCount: 0
                };
            }
            return rect;
        });
    } else {
        // 当事件从全天事件变为非全天事件时，更新对应的矩形
        const eventRect = getRectPositionFromTimeRange(useEventData.currentEvent);
        useEventData.currentRects = useEventData.currentRects.map((rect) => {
            if (rect.id === useEventData.currentEvent.id) {
                return {
                    ...rect,
                    column: eventRect.column,
                    startRow: eventRect.startRow,
                    rowCount: eventRect.rowCount
                };
            }
            return rect;
        });
    }
}

// 开关处理
const handleRepeatSwitch = async (val: boolean) => {
    if (val) {
        // 开启重复逻辑
        showRepeatDialog.value = true
    }
    // else{ ElMessageBox.confirm(
    //     '你确认要取消该重复事件吗：',
    //     {
    //       distinguishCancelAndClose: false,
    //       confirmButtonText: '确定',
    //       cancelButtonText: '取消',
    //       type: 'warning'
    //     }
    //   ).then(() => {
    //     useScheduleStore.deleteEvent(useEventData.currentEvent, true);
    //     useEventData.selectedRectIndex = -1;
    //   })
    // }
}
    



const handleModifyRepeat = () => {
    showRepeatDialog.value = true;
    // 加载当前重复规则到对话框
    dialogRecurrence.value = cloneDeep(useEventData.currentEvent.recurrence);
};

const durationText = computed(() => {
    if (!useEventData.currentEvent.start || !useEventData.currentEvent.end) return ' '
    const diffMinutes = dayjs(useEventData.currentEvent.end).diff(useEventData.currentEvent.start, 'minute')
    const hours = Math.floor(diffMinutes / 60)
    const minutes = diffMinutes % 60
    return `${hours}小时${minutes}分钟`
})
const disableStartHours = () => {
    if (!useEventData.currentEvent.end) return [];
    const endHour = dayjs(useEventData.currentEvent.end).hour();
    if(dayjs(useEventData.currentEvent.end).minute() < dayjs(useEventData.currentEvent.start).minute()) {
        return Array.from({length: 24}, (_, i) => i).filter(h => h > endHour)}
    else {
        return Array.from({length: 24}, (_, i) => i).filter(h => h > endHour);}
};

const disableStartMinutes = (selectedHour: number) => {
    if (!useEventData.currentEvent.end) return [];
    const end = dayjs(useEventData.currentEvent.end);
    if (selectedHour === end.hour()) {
        // 新增5分钟最小间隔限制
        const minAllowed = end.minute() - 15;
        return Array.from({length: 60}, (_, i) => i).filter(m => m >= minAllowed);
    }
    return [];
};

const disableEndHours = () => {
    if (!useEventData.currentEvent.start) return [];
    const startHour = dayjs(useEventData.currentEvent.start).hour();
    if(dayjs(useEventData.currentEvent.end).minute() > dayjs(useEventData.currentEvent.start).minute()) {
        return Array.from({length: 24}, (_, i) => i).filter(h => h < startHour)}
    else {
        return Array.from({length: 24}, (_, i) => i).filter(h => h < startHour);}
};

const disableEndMinutes = (selectedHour: number) => {
    if (!useEventData.currentEvent.start) return [];
    const start = dayjs(useEventData.currentEvent.start);
    if (selectedHour === start.hour()) {
        // 新增5分钟最小间隔限制
        const maxAllowed = start.minute() + 15;
        return Array.from({length: 60}, (_, i) => i).filter(m => m <= maxAllowed);
    }
    return [];
};
</script>


<style scoped>
* {
    user-select: none;
}

.event-form {
    display: flex;
    width: 90%;
    height: inherit;
    transform: translateY(50px);
}

.ml-2 {
    margin-left: 8px;
}

.custom-select :deep(.el-input__inner) {
    border-color: #000000;
    border-radius: 8px;
    background-color: #fff5f5;
}
.custom-select {
    width: 160px;
}
.custom-time-picker:deep(.el-input--prefix .el-input__prefix) {
    display: none !important;
}

.modify-btn {
  height: 32px;
  width: 66px;
  background-color: #FBFBFB;
  border-radius: 4px;
  margin-left: auto;
  cursor: pointer;
  border: #d4d4d4 1px solid;
  font-size: 14px;
  color: #000000;
  user-select: none;
  display: flex;
  color: #606266;
  justify-content: center;
  align-items: center;
  padding: 2px 0 4px 0;
  transition: background-color 0.2s ease;
  &:hover {
    background-color: #dbdbdb;
  }
}

/* 暗色主题样式 */
[data-theme="dark"] .custom-select :deep(.el-input__inner) {
  border-color: #444444;
  background-color: #2d2d2d;
  color: #ffffff;
}

[data-theme="dark"] .custom-time-picker :deep(.el-input__inner) {
  background-color: #2d2d2d;
  color: #ffffff;
  border-color: #444444;
}

[data-theme="dark"] .modify-btn {
  background-color: #2d2d2d;
  border: #444444 1px solid;
  color: #ffffff;
  &:hover {
    background-color: #3d3d3d;
  }
}

[data-theme="dark"] .el-dialog {
  background-color: #252526;
}

[data-theme="dark"] .el-dialog__header {
  color: #ffffff;
}

[data-theme="dark"] .el-form-item__label {
  color: #ffffff;
}

[data-theme="dark"] .el-input__inner {
  background-color: #2d2d2d;
  color: #ffffff;
  border-color: #444444;
}

[data-theme="dark"] .el-textarea__inner {
  background-color: #2d2d2d;
  color: #ffffff;
  border-color: #444444;
}
</style>