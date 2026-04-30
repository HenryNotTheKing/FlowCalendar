import { defineStore } from "pinia";
import { computed} from 'vue';
import { TodoTask } from "../../types/todolist";
import { ProjectParams } from "./ProjectParams";
import { TodoSideBarParams } from "./TodoSideBarParams";

export const TodoList = defineStore("TodoList", () => {
  //const RepeatTasks = ref<TodoTask[]>([]);
  const useProjectParams = ProjectParams();
  const tasks = computed<TodoTask[]>(() => {
    return useProjectParams.projects.filter(project => project.id === 'daily_todos').flatMap(project => project.todos);
  });


  const TodayIncompletedTasks = computed(() => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return tasks.value.filter(task => {
            const taskDate = new Date(task.date);
            taskDate.setHours(0, 0, 0, 0);
            return taskDate.getTime() === today.getTime() && !task.completed;
        });
    })

    const incompleteTasks = computed(() => {
        return tasks.value.filter(task => !task.completed);
    });

    const TodayCompletedTasks = computed(() => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return tasks.value.filter(task => {
            const taskDate = new Date(task.date);
            taskDate.setHours(0, 0, 0, 0);
            return taskDate.getTime() === today.getTime() && task.completed;
        });
    })
    
    const completedTasks = computed(() => {
        return tasks.value.filter(task => task.completed);
    });

    function deleteTask(id: string) {
        const useTodoSideBarParams = TodoSideBarParams();
        useTodoSideBarParams.isDisableTransition = true
        const index = tasks.value.findIndex(task => task.id === id);
        if (index !== -1) {
            const task = tasks.value[index];
            
            // 如果已经处于淡出过程中，直接删除
            if (task.completionTimer) {
                clearTimeout(task.completionTimer);
                task.completionTimer = null;
                tasks.value.splice(index, 1);
                return;
            }

            // 设置定时器
            task.completionTimer = setTimeout(() => {
                task.fadeOut = true;

                // 动画结束后删除任务
                setTimeout(() => {
                    const current = tasks.value.find(t => t.id === id);
                    if (current?.projectId) {
                    useProjectParams.removeTodoFromProject(current.projectId, id);
                    console.log(useTodoSideBarParams.isDisableTransition);
                    useTodoSideBarParams.isDisableTransition = false;
                    }
                }, 300); // 与fadeOut动画时长一致
            }, 0);
        }        
    }

    function getCompletedTagColor(color:string){
        return (color + "80")
    }

  return {
    tasks,
    TodayIncompletedTasks,
    TodayCompletedTasks,
    incompleteTasks,
    completedTasks,
    getCompletedTagColor,
    deleteTask,
  }
})