<template>
    <div class="edit-modal-overlay" @click="closeEditModal">
      <div class="edit-modal" @click.stop>

        <div class="edit-modal-body">
          <div class="form-group first-group">
            <div class="edit-task-title">
              <input v-model="editForm.title" class="form-input" placeholder="输入任务名称" />
            </div>
            <el-date-picker v-model="editForm.date" type="date" placeholder="选择日期" format="MM-DD"
              class="form-input"   />
            <el-time-picker v-model="editForm.time" format="HH:mm" value-format="HH:mm" placeholder="选择时间"
              class="form-input" />
          </div>


          <div class="form-group">
            <div class="priority-buttons">
              <button :class="['priority-btn', { active: editForm.priority === 0 }]" @click="editForm.priority = 0">
                无
              </button>
              <button :class="['priority-btn', { active: editForm.priority === 1 }]" @click="editForm.priority = 1">
                低
              </button>
              <button :class="['priority-btn', { active: editForm.priority === 2 }]" @click="editForm.priority = 2">
                中
              </button>
              <button :class="['priority-btn', { active: editForm.priority === 3 }]" @click="editForm.priority = 3">
                高
              </button>
            </div>
          </div>

          <div class="form-group">
            <div class="tags-container">
              <!-- 已添加的标签 -->
              <div v-for="(tag, index) in useProjectParams.activeProject?.tags" :key="index" class="tag-item"
                :class="{ selected: editForm.tag === tag.name }"
                :style="{ 
                  borderColor: editForm.tag === tag.name ? 'transparent' : (isTaskCompleted ? (useTodoList.getCompletedTagColor(tag.name) || '#cccccc80') : (tag.color || '#e0e0e0')),
                  color: editForm.tag === tag.name ? 'white' : (isTaskCompleted ? (useTodoList.getCompletedTagColor(tag.name) || '#cccccc80') : (tag.color || '#e0e0e0')),
                  background: editForm.tag === tag.name ? 
                    `linear-gradient(135deg, ${getTransparentColor(tag.color, 0.5)}, ${tag.color})` : 
                    'rgba(255, 255, 255, 0.3)'
                }" 
                @click="editForm.tag = tag.name"
                @mouseenter="useEditParams.showDeleteIcon[index] = true" @mouseleave="useEditParams.showDeleteIcon[index] = false">
                {{  "#" + tag.name }}
                <X v-if="useEditParams.showDeleteIcon[index]" :size="14" 
                  :color="editForm.tag === tag.name ? 'white' : (isTaskCompleted ? (useTodoList.getCompletedTagColor(tag.name) || '#cccccc80') : (tag.color || '#e0e0e0'))" 
                  strokeWidth="2.5" class="delete-icon"
                  @click="removeTagFromTask(index)" />
              </div>

              <!-- 添加新标签的输入框 -->
              <div v-if="showNewTagInput" class="new-tag-input-container">
                <input ref="newTagInputRef" v-model="newTag.name" class="new-tag-input" placeholder="输入标签名称"
                  @keyup.enter="addTagToTask" />
                <div class="tag-colors">
                  <div v-for="color in tagColors" :key="color" class="color-option" :style="{ backgroundColor: getTransparentColor(color, 0.8) }"

                    @click="newTag.color = color" :class="{ selected: newTag.color === color }"></div>
                </div>
                <button class="confirm-tag-btn" @click="addTagToTask">确定</button>
              </div>

              <!-- 添加标签按钮 -->
              <div v-else class="add-tag-btn" @click="showAddTagInput">
                + 添加标签
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editForm.repeat" class="form-checkbox" />
              重复任务
            </label>
          </div>

          <div v-if="editForm.repeat" class="recurrence-settings">
            <div class="form-row">
              <div class="form-group">
                <label>重复类型</label>
                <select v-model="editForm.recurrence.type" class="form-select">
                  <option :value="'daily'">每日</option>
                  <option :value="'weekly'">每周</option>
                  <option :value="'monthly'">每月</option>
                  <option :value="'yearly'">每年</option>
                </select>
              </div>

              <div class="form-group">
                <label>间隔</label>
                <el-input-number v-model="editForm.recurrence.interval" :min="1" :max="365" controls-position="right"
                  class="number-input" />
              </div>
            </div>

            <div class="form-group">
              <label>结束条件</label>
              <select v-model="editForm.recurrence.endCondition" class="form-select">
                <option :value="'never'">从不</option>
                <option :value="'untilDate'">直到日期</option>
                <option :value="'occurrences'">重复次数</option>
              </select>
            </div>

            <div v-if="editForm.recurrence.endCondition === 'untilDate'" class="form-group">
              <label>结束日期</label>
              <el-date-picker v-model="editForm.recurrence.endDate" type="date" placeholder="选择结束日期" format="YYYY-MM-DD"
                value-format="YYYY-MM-DD" class="form-input" />
            </div>

            <div v-if="editForm.recurrence.endCondition === 'occurrences'" class="form-group">
              <label>重复次数</label>
              <el-input-number v-model="editForm.recurrence.occurrences" :min="1" :max="999" controls-position="right"
                class="number-input" />
            </div>
          </div>
        </div>
        <div class="edit-modal-footer">
          <button class="cancel-button" @click="closeEditModal">取消</button>
          <button class="save-button" @click="saveEdit">保存</button>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, computed } from 'vue';
import { ElDatePicker, ElTimePicker, ElInputNumber, ElMessage } from 'element-plus';
import { X } from 'lucide-vue-next';
import { EditParams } from '../../stores/TodoList/EditParams';
import { TodoList } from '../../stores/TodoList/TodoList';
import { TodoTask } from '../../types/todolist';
import { ProjectParams } from '../../stores/TodoList/ProjectParams';
import { TodoApi } from '../../stores/TodoList/TodoAPI.ts';
const api = TodoApi();
const useProjectParams = ProjectParams();
const useTodoList = TodoList();
const useEditParams = EditParams();
const editForm = useEditParams.editForm;

// 计算任务是否已完成
const isTaskCompleted = computed(() => {
  if (useEditParams.editingTask) {
    return useEditParams.editingTask.completed;
  }
  return false;
});

const showNewTagInput = ref(false);
const newTagInputRef = ref<HTMLInputElement | null>(null);
const newTag = reactive({
  name: '',
  color: '#409eff'
});

// 预定义的标签颜色
const tagColors = [
'#409EFF','#67C23A','#E6A23C','#E91E63','#9C27B0'
];


function closeEditModal() {
  useEditParams.isEditModalOpen = false;
  useEditParams.editingTask = null;
}

// 保存编辑
function saveEdit() {
  // 检查标题是否为空
  
  if (!editForm.title || editForm.title.trim() === '') {
    ElMessage.warning('任务标题不能为空');
    return;
  }
  
  if (useEditParams.editingTask) {
    // 准备更新数据
    const updates: Partial<TodoTask> = {
      title: editForm.title,
      date: new Date(editForm.date),
      priority: editForm.priority,
      projectId: editForm.projectId, 
      tag: editForm.tag,
      repeat: editForm.repeat,
      recurrence: editForm.recurrence
    };
    console.log(updates);
    useProjectParams.updateProjectTodo(editForm.projectId, useEditParams.editingTask.id, updates);
  }
  closeEditModal();
  useEditParams.isAdding = false;
  useEditParams.lastAddedDate = new Date(editForm.date);
}

// 显示添加标签输入框
const showAddTagInput = () => {
  showNewTagInput.value = true;
  newTag.name = '';
  newTag.color = '#409eff';

  // 在DOM更新后聚焦到输入框
  nextTick(() => {
    if (newTagInputRef.value) {
      newTagInputRef.value.focus();
    }
  });
};



// 添加标签到任务
const addTagToTask = () => {
  // 检查标签名是否为空
  if (!newTag.name.trim()) {
    ElMessage.warning('标签名称不能为空');
    return;
  }
  
  // 检查是否已存在同名标签
  const isDuplicate = useProjectParams.activeProject?.tags?.some(tag => tag.name === newTag.name);
  if (isDuplicate) {
    ElMessage.warning('已存在同名标签');
    return;
  }
  
  api.projectTagAPI.addTagToProject(useProjectParams.activeProject?.id ?? '', newTag.name, newTag.color);
  useProjectParams.activeProject?.tags?.push({name: newTag.name, color: newTag.color});
  useEditParams.editForm.tag = newTag.name;

  showNewTagInput.value = false;
  newTag.name = '';
};

// 从任务中移除标签
const removeTagFromTask = (index: number) => {
  const tagName = useProjectParams.activeProject?.tags?.[index]?.name ?? '';
  api.projectTagAPI.deleteProjectTag(useProjectParams.activeProject?.id ?? '', tagName);
  useProjectParams.activeProject?.tags?.splice(index, 1);
};

// 将颜色转换为透明颜色
const getTransparentColor = (color: string, alpha: number) => {
  if (color.startsWith('#')) {
    const r = parseInt(color.slice(1, 3), 16);
    const g = parseInt(color.slice(3, 5), 16);
    const b = parseInt(color.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }
  return color;
};

</script>

<style scoped>
.edit-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.edit-modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.edit-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 0px 24px;

}

.edit-modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: #333;
}

.edit-modal-body {
  padding: 20px 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-input,
.form-select {
  width: 100%;
  border: none;
  padding: 2px 0px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.edit-task-title {
  width: 100%;
  border-bottom: #cdcdcd 2px solid;
}

.edit-task-title .form-input {
  width: 140px;
  border: none;
  font-size: 18px;
  transform: translateY(2px);
  font-weight: 500;
  color: #333;
  background-color: transparent;
}

.form-input:focus,
.form-select:focus {
  outline: none;
}

.form-group.first-group {
  position: relative;
  top: 8px;
  display: flex;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
  margin-bottom: 0;
}

.priority-buttons {
  display: flex;
  gap: 8px;
}

.priority-btn {
  flex: 1;
  padding: 8px 0;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #333;
  position: relative;
  overflow: hidden;
}

.priority-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0));
  z-index: 1;
}

.priority-btn span {
  position: relative;
  z-index: 2;
}

.priority-btn:hover {
  transform: translateY(-2px);
}

.priority-btn.active {
  color: white;
}

/* 无优先级 - 灰色 */
.priority-btn:nth-child(1) {
  color: rgb(153, 153, 153);
  background: transparent;
  border: 1px solid rgba(201, 201, 201, 0.7);
}

.priority-btn:nth-child(1).active {
  background: linear-gradient(135deg, rgba(179, 179, 179, 0.9), rgba(143, 143, 143, 0.9));
  color: white;
}

/* 低优先级 - 绿色 */
.priority-btn:nth-child(2) {
  background: transparent;
  border: 1px solid rgba(102, 187, 106, 0.7);
  color: rgb(102, 187, 106);
}

.priority-btn:nth-child(2).active {
  background: linear-gradient(135deg, rgba(102, 187, 106, 0.9), rgba(56, 142, 60, 0.9));
  color: white;
}

/* 中优先级 - 橙色 */
.priority-btn:nth-child(3) {
  background: transparent;
  border: 1px solid rgba(255, 156, 56, 0.7);
  color: rgb(255, 156, 56);
}

.priority-btn:nth-child(3).active {
  background: linear-gradient(135deg, rgba(238, 196, 134, 0.9), rgba(255, 156, 56, 0.9));
  color: white;
}

/* 高优先级 - 红色 */
.priority-btn:nth-child(4) {
  background: transparent;
  border: 1px solid rgb(236, 133, 133);
  color: rgb(245, 93, 93);
}

.priority-btn:nth-child(4).active {
  background: linear-gradient(135deg, rgba(245, 141, 139, 0.9), rgba(234, 71, 71, 0.9));
  color: white;
}

.tag-input {
  position: relative;
  display: flex;

}

/* 标签样式 */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 32px;
}

.tag-item {
  display: flex;
  align-items: center;
  padding: 4px 10px;
  margin-right: 2px;
  border-radius: 12px;
  font-size: 12px;
  user-select: none;
  position: relative;
  transition: all 0.3s ease;
  border: 1px solid;
  background: transparent;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.3);
}

.tag-item:hover {
  padding-right: 20px;
  transform: translateY(-2px);
}

.tag-item.selected {
  color: white;
  border: none;
}

.delete-icon {
  position: absolute;
  right: 4px;
  cursor: pointer;
  color: inherit;
}

.add-tag-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border: 1px dashed #ccc;
  border-radius: 12px;
  font-size: 12px;
  color: #999;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.add-tag-btn:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.new-tag-input-container {
  display: flex;
  width: 100%;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.new-tag-input {
  padding: 6px;
  outline: none;
  border-top: none;
  border-left: none;
  border-right: none;
  border-bottom: 1px solid #e8e8e8;
  font-size: 14px;
}

.tag-colors {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  width: 100%;
}

.color-option {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  filter: saturate(1.5) brightness(0.9);
}

.color-option.selected {
  border-color:#6ebbff;
  transform: scale(1.1);
}

.confirm-tag-btn {
  align-self: flex-end;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: #409eff;
  color: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.confirm-tag-btn:hover {
  background: #337ecc;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-checkbox {
  margin-right: 8px;
  width: 16px;
  height: 16px;
}

.recurrence-settings {
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 6px;
  margin-top: 8px;
}

.number-input {
  width: 100%;
}

.edit-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

.cancel-button,
.save-button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-button {
  background-color: #f5f5f5;
  border: none;
  color: #666;
}

.cancel-button:hover {
  background-color: #eeeeee;
}

.save-button {
  background-color: #409eff;
  border: none;
  color: white;
}

.save-button:hover {
  background-color: #337ecc;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-date-editor.el-input),
:deep(.el-date-editor.el-input__wrapper) {
  border: none;
  background-color: #f5f5f5;
  border-radius: 6px;
  padding: 0;
}

:deep(.el-date-editor.el-input__inner) {
  border: none;
  background-color: transparent;
  padding: 10px 12px;
}

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-input-number .el-input) {
  background-color: #f5f5f5;
  border-radius: 6px;
}

:deep(.el-input-number .el-input__inner) {
  background-color: transparent;
  border: none;
  padding: 10px 12px;
}

:deep(.el-input-number .el-input__wrapper) {
  background-color: transparent;
  box-shadow: none;
}

:deep(.el-time-panel) {
  border-radius: 8px;
}

/* 暗色主题样式 */
[data-theme="dark"] .edit-modal-overlay {
  background-color: rgba(0, 0, 0, 0.7);
}

[data-theme="dark"] .edit-modal {
  background: #2d2d2d;
  color: #ffffff;
}

[data-theme="dark"] .form-input,
[data-theme="dark"] .form-select {
  background-color: #3c3c3c;
  color: #ffffff;
}

[data-theme="dark"] .edit-task-title {
  border-bottom: #555555 2px solid;
}

[data-theme="dark"] .edit-task-title .form-input {
  color: #ffffff;
  background-color: transparent;
}

[data-theme="dark"] .form-group label {
  color: #ffffff;
}

[data-theme="dark"] .priority-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #cccccc;
}

[data-theme="dark"] .priority-btn:nth-child(1) {
  border: 1px solid rgba(153, 153, 153, 0.7);
  color: #999999;
}

[data-theme="dark"] .priority-btn:nth-child(2) {
  border: 1px solid rgba(102, 187, 106, 0.7);
  color: #66bb6a;
}

[data-theme="dark"] .priority-btn:nth-child(3) {
  border: 1px solid rgba(255, 156, 56, 0.7);
  color: #ff9c38;
}

[data-theme="dark"] .priority-btn:nth-child(4) {
  border: 1px solid rgba(245, 93, 93, 0.7);
  color: #f55d5d;
}

[data-theme="dark"] .tag-item {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid #666666;
  color: #ffffff;
}

[data-theme="dark"] .add-tag-btn {
  border: 1px dashed #666666;
  color: #aaaaaa;
  background: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .new-tag-input-container {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid #555555;
}

[data-theme="dark"] .new-tag-input {
  background-color: transparent;
  color: #ffffff;
  border-bottom: 1px solid #555555;
}

[data-theme="dark"] .checkbox-label {
  color: #ffffff;
}

[data-theme="dark"] .recurrence-settings {
  background-color: #3c3c3c;
}

[data-theme="dark"] .edit-modal-footer {
  border-top: 1px solid #444444;
}

[data-theme="dark"] .cancel-button {
  background-color: #3c3c3c;
  color: #cccccc;
}

[data-theme="dark"] .cancel-button:hover {
  background-color: #444444;
}

[data-theme="dark"] .save-button {
  background-color: #0a84ff;
}

[data-theme="dark"] .save-button:hover {
  background-color: #0071e3;
}

/* Element Plus 组件暗色主题 */
[data-theme="dark"] :deep(.el-date-editor.el-input),
[data-theme="dark"] :deep(.el-date-editor.el-input__wrapper) {
  background-color: #3c3c3c;
}

[data-theme="dark"] :deep(.el-date-editor.el-input__inner) {
  color: #ffffff;
}

[data-theme="dark"] :deep(.el-input-number .el-input) {
  background-color: #3c3c3c;
}

[data-theme="dark"] :deep(.el-input-number .el-input__inner) {
  color: #ffffff;
}

[data-theme="dark"] :deep(.el-picker-panel) {
  background-color: #2d2d2d;
  border: 1px solid #444444;
  color: #ffffff;
}

[data-theme="dark"] :deep(.el-picker-panel__header) {
  background-color: #2d2d2d;
  border-bottom: 1px solid #444444;
}

[data-theme="dark"] :deep(.el-picker-panel__footer) {
  background-color: #2d2d2d;
  border-top: 1px solid #444444;
}

[data-theme="dark"] :deep(.el-time-panel) {
  background-color: #2d2d2d;
  border: 1px solid #444444;
  color: #ffffff;
}
</style>