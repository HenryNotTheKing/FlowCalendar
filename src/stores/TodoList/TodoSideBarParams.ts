import { defineStore } from "pinia";
import { ref } from 'vue';
 
export const TodoSideBarParams = defineStore("TodoSideBarParams", () => {
    const isShowToday = ref(true);
    const isShowCompleted = ref(false);
    const isShowAll = ref(false);
    const isShowMyProject = ref(false); // 新增：控制是否显示MyProject组件
    const isDisableTransition = ref(false); // 控制是否禁用过渡动画
    
    // 新增状态重置方法
    function resetViews() {
        isShowToday.value = false;
        isShowCompleted.value = false;
        isShowAll.value = false;
        isShowMyProject.value = false; // 重置MyProject显示状态
    }

    return {
        isShowToday,
        isShowCompleted,
        isShowAll,
        isShowMyProject, // 导出新变量
        isDisableTransition, // 导出新变量
        resetViews
    }
})