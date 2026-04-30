<template>
<div class="picker">
    <!-- 新增分类项容器 -->
    <div class="category-container">
        <div 
            class="category-item"
            v-for="(category) in useScheduleStore.categories"
            :key="category.id"
        >
            <div
                class="color-display"
                :style="{backgroundColor: useEventData.colorOptions.find(c => Object.keys(c)[0] === category.color)?.[category.color]}"
                @click="toggleColorPicker(category.id, $event)"
            ></div>
            <input
                class="text-display"
                type="text" 
                v-model="category.name"
                @blur="handleNameUpdate(category)"
            >
            <div class="delete-icon" @click="deleteCategory(category.id)">
                <img src="../../assets/Icons/delete.svg" alt="delete" class="delete-icon" />
        </div>
        </div>
        
    </div>

    <!-- 新增分类按钮 -->
    <div class="add-catagory" @click="addCategory()">
        <div class="add" >
            <img src="../../assets/Icons/Plus.svg" alt="ADD" class="add-icon" />
        </div>
        <div class="text-add">添加分类</div>
    </div>

    <!-- 颜色选择器菜单（保持在底部） -->
    <div v-show="activeColorIndex !== null" class="color-picker-menu" :style="menuPosition">
    <div 
        v-for="(color, cIndex) in useEventData.colorOptions" 
        :key="cIndex"
        class="color-option"
        :style="{backgroundColor: Object.values(color)[0]}"
        @click.stop="selectColor(cIndex, activeColorIndex)" 
    ></div>
</div>
</div>
</template>

<script lang='ts' setup>


import { ref } from 'vue';
import { ScheduleStore } from '../../stores/Calendar/ScheduleStore';
import { EventData } from '../../stores/Calendar/EventData';
const useEventData = EventData();
const useScheduleStore = ScheduleStore();
const activeColorIndex = ref<number | null>(null);
import { ElMessage } from 'element-plus'

const menuPosition = ref({
    left: '0px',
    top: '0px'
})

const toggleColorPicker = (index: number, event: MouseEvent) => {
    activeColorIndex.value = activeColorIndex.value === index ? null : index;
    
    const target = event.currentTarget as HTMLElement;
    const rect = target.getBoundingClientRect();
    const parentRect = target.offsetParent?.getBoundingClientRect() || { top: 0, left: 0 };
    
    // 计算相对父容器的垂直位置（居中显示）
    menuPosition.value = {
        left: `${rect.left + rect.width + 8 - (parentRect?.left || 0)}px`,
        top: `${rect.top + rect.height/2 - (parentRect?.top || 0) - 20}px` // 调整垂直居中
    }
}
const selectColor = (colorIndex: number, targetIndex: number | null) => {
    if (targetIndex !== null) {
        const selectedColor = Object.keys(useEventData.colorOptions[colorIndex])[0];
        useScheduleStore.updateCategory(targetIndex, { 
            color: selectedColor 
        });
    }
    activeColorIndex.value = null;  // 关闭颜色选择器
}

const deleteCategory = (index: number) => {
    if ((deleteCategory as any).timer) clearTimeout((deleteCategory as any).timer);
        
        if (useScheduleStore.categories.length === 1) {
            ElMessage.error('至少保留一个分类');
            return;
        }else{
            useScheduleStore.deleteCategory(index);
        }
};

const addCategory = () => {
  // 生成临时名称时先检查是否重复
  const baseName = `新分类-${useScheduleStore.categories.length + 1}`;
  let newName = baseName;
  let counter = 1;
  
  // 检查是否存在同名分类
  while (useScheduleStore.categories.some(c => c.name === newName)) {
    newName = `${baseName} (${counter})`;
    counter++;
  }

  try {
    useScheduleStore.createCategory({
      name: newName,
      color: 'Blue'
    });
  } catch (error) {
    console.error('创建分类失败:', error);
  }
};

const handleNameUpdate = (category: any) => {
  const isDuplicate = useScheduleStore.categories
    .filter(c => c.id !== category.id)
    .some(c => c.name === category.name);
  
  if (isDuplicate) {
    ElMessage.error('分类名称已存在');
    category.name = `${category.name}(2)`; // 恢复原名称
    return;
  }
  useScheduleStore.updateCategory(category.id, { name: category.name });
};
</script>

<style scoped>
.category-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 80%;
    margin-bottom: 12px;
}

.category-item {
    display: flex;
    align-items: center;
    width: 100%;
    height: 30px;
}

.color-picker-menu {
    position: absolute;
    left: 0;
    top: 0;
    transform: translateY(-50%);
    background: #F7F7F7;
    padding: 8px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    display: flex;
    gap: 6px;
    z-index: 1000;
    transform: translateY(12%);
}

.color-option {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    border-radius: 4px;
    cursor: pointer;
    transition: transform 0.2s;
}

.color-option:hover {
    transform: scale(1.1);
}

.picker{
    position: relative;
    top:10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
}
.category-container{
    display: flex;
    flex-direction: column;
    width:80%;
}
.catagory-display{
    width: 80%;
    height: 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    border-radius: 6px;
}

.add-catagory{
    width: 85%;
    height: 30px;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    border-radius: 6px;
}
.color-display{
   height: 14px;
   width: 14px;
   border-radius: 4px;
   background-color: #000000;
   margin-left: 4px;
   flex-shrink: 0;
   cursor: pointer;
}
.text-display{
    font-size: 14px;
    color: #868686;
    user-select: none;
    width: 90%;
    height: 28px;
    border-radius: 4px;
    text-align: left;
    padding: 0 8px;
    border: none;
    outline: none;
    background: none;
    box-shadow: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
}
.delete-icon{
    display: flex;
    align-items: center;
    justify-content: center;
    height: 22px;
    width: 22px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
}
.delete-icon:hover{
    background-color: #efefef;
    transition: all 0.2s ease-in-out;
}
.text-display:focus {
    background-color: #efefef;
}
.text-display:hover{
    background-color: #efefef;
}

.add-icon{
    margin-left: 10px;
    transform: translateY(-1px);
}
.text-add{
    color: #868686;
    margin-left: 11px;
    user-select: none;
    width: 90%;
    height: 24px;
    border-radius: 4px;
    font-size: 13px;
}
.add-catagory:hover{
    background-color: #efefef;
}
[data-theme="dark"] .color-picker-menu {
    background-color: #3D3D3D;
}
[data-theme="dark"] .text-display {
    color: #B0B0B0;
    background: none;
}
[data-theme="dark"] .text-display:focus {
    background-color: #2D2D2D;
}
[data-theme="dark"] .text-display:hover {
    background-color: #2D2D2D;
}
[data-theme="dark"] .delete-icon:hover {
    background-color: #2D2D2D;
}
[data-theme="dark"] .add-catagory:hover {
    background-color: #2D2D2D;
}
[data-theme="dark"] .text-add {
    color: #B0B0B0;
}
</style>