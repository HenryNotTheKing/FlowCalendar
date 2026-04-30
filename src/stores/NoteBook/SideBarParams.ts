import { defineStore } from "pinia";
import { ref } from 'vue';
 
export const SideBarParams = defineStore("SideBarParams", () => {
    const isShowPage = ref(false);
    const showDocumentList = ref(true);
    const isShowRecycleBin = ref(false);
    const isShowSearchBox = ref(false);
    const isShowProjectCatalog = ref(false); // 新增：显示项目目录
    const currentProjectId = ref(null as string | null); // 新增：当前项目ID
    const isRightPanelVisible = ref(true);

    // 新增状态重置方法
    function resetViews() {
        isShowPage.value = false;
        isShowRecycleBin.value = false;
        showDocumentList.value = false;
        isShowSearchBox.value = false;
        isShowProjectCatalog.value = false; // 重置项目目录显示状态
        currentProjectId.value = null; // 重置当前项目ID
    }


    return {
        isShowPage,
        showDocumentList,
        isShowRecycleBin,
        isShowSearchBox,
        isShowProjectCatalog, // 导出新属性
        currentProjectId, // 导出新属性
        isRightPanelVisible,
        resetViews,
    }
})