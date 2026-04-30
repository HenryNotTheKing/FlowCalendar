import { defineStore } from "pinia";
import { reactive, ref } from 'vue';
import { TodoTask } from "../../types/todolist";
import { ProjectParams } from "./ProjectParams";

// import { TodoList } from "./TodoList";

export const EditParams = defineStore("EditParams", () => {
    const lastAddedDate = ref<Date>(new Date());

    const isAdding = ref(false);
    type RecurrenceType = "daily" | "weekly" | "monthly" | "yearly";
    type EndConditionType = "never" | "untilDate" | "occurrences";
    // const useTodoList = TodoList();
    const editForm = reactive({
        title: '',
        date: new Date(),
        projectId: '',
        time: '',
        priority: 0,
        tag: '',
        repeat: false,
        recurrence: {
            type: 'daily' as RecurrenceType,
            interval: 1,
            endCondition: 'never' as EndConditionType,
            endDate: undefined as Date | undefined,
            occurrences: undefined as number | undefined
        }
    });

    // 编辑任务相关
    const editingTask = ref<TodoTask | null>(null);
    const isEditModalOpen = ref(false);


    // 标签删除图标显示状态
    const showDeleteIcon = ref<boolean[]>([]);

    function openEditModal(task: TodoTask) {
        const useProjectParams = ProjectParams();
        editingTask.value = task;
        isEditModalOpen.value = true;

        // 初始化编辑表单数据
        editForm.title = task.title;
        editForm.date = task.date;
        editForm.projectId = task.projectId || useProjectParams.activeProjectId || '';
        editForm.time = task.date instanceof Date ? formatTimeTo24Hour(task.date) : '';
        editForm.priority = task.priority;
        editForm.repeat = task.repeat;
        editForm.tag = task.tag;

        // // 初始化标签删除图标显示状态
        // showDeleteIcon.value = Array(useTodoList.tags.length).fill(false);

        if (task.recurrence) {
            editForm.recurrence = {
                type: task.recurrence.type as RecurrenceType,
                interval: task.recurrence.interval,
                endCondition: task.recurrence.endCondition as EndConditionType,
                endDate: task.recurrence.endDate !== undefined ? task.recurrence.endDate : undefined,
                occurrences: task.recurrence.occurrences !== undefined ? task.recurrence.occurrences : undefined
            };
        } else {
            editForm.recurrence = {
                type: 'daily' as RecurrenceType,
                interval: 1,
                endCondition: 'never' as EndConditionType,
                endDate: undefined,
                occurrences: undefined
            };
        }
    };

    function formatTimeTo24Hour(date: Date) {
        if (!(date instanceof Date)) {
            return '';
        }

        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    return {
        editingTask,
        editForm,
        isEditModalOpen,
        showDeleteIcon,
        isAdding,
        lastAddedDate,
        openEditModal
    }
})