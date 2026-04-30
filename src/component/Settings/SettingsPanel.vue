<template>
  <div v-if="visible" class="settings-overlay" @click.self="close">
    <div class="settings-modal">
      <div class="settings-header">
        <h3>设置</h3>
        <button class="close-button" @click="close" aria-label="关闭">×</button>
      </div>

      <div class="settings-body">
        <!-- 外观 -->
        <section class="settings-section">
          <div class="section-title">外观</div>
          <div class="theme-toggle">
            <button
              class="theme-option"
              :class="{ active: themeStore.theme === 'light' }"
              @click="setTheme('light')"
            >
              <Sun :size="16" stroke-width="1.6" />
              <span>明亮</span>
            </button>
            <button
              class="theme-option"
              :class="{ active: themeStore.theme === 'dark' }"
              @click="setTheme('dark')"
            >
              <Moon :size="16" stroke-width="1.6" />
              <span>暗色</span>
            </button>
          </div>
        </section>

        <!-- DeepSeek -->
        <section class="settings-section">
          <div class="section-title">DeepSeek</div>
          <div class="form-group">
            <label class="form-label">Base URL</label>
            <input
              v-model="settings.deepseek.baseUrl"
              type="text"
              class="form-input"
              placeholder="https://api.deepseek.com"
            />
          </div>
          <div class="form-group">
            <label class="form-label">API Key</label>
            <input
              v-model="settings.deepseek.apiKey"
              type="password"
              class="form-input"
              :class="{ 'has-mask': settings.deepseek.hasKey && !settings.deepseek.apiKey }"
              :placeholder="settings.deepseek.hasKey ? DOT_MASK : '请输入 sk-... （必填）'"
              autocomplete="off"
            />
            <div v-if="settings.deepseek.hasKey" class="hint-text">已配置，留空保留原 Key</div>
          </div>
        </section>

        <!-- DashScope -->
        <section class="settings-section">
          <div class="section-title">通义 DashScope</div>
          <div class="form-group">
            <label class="form-label">Base URL</label>
            <input
              v-model="settings.dashscope.baseUrl"
              type="text"
              class="form-input"
              placeholder="https://dashscope.aliyuncs.com/api/v1"
            />
          </div>
          <div class="form-group">
            <label class="form-label">API Key</label>
            <input
              v-model="settings.dashscope.apiKey"
              type="password"
              class="form-input"
              :class="{ 'has-mask': settings.dashscope.hasKey && !settings.dashscope.apiKey }"
              :placeholder="settings.dashscope.hasKey ? DOT_MASK : '请输入 sk-... （必填）'"
              autocomplete="off"
            />
            <div v-if="settings.dashscope.hasKey" class="hint-text">已配置，留空保留原 Key</div>
          </div>
        </section>

        <div v-if="settings.lastError" class="error-msg">{{ settings.lastError }}</div>
        <div v-if="toastMsg" class="toast-msg">{{ toastMsg }}</div>
      </div>

      <div class="settings-footer">
        <button class="btn btn-default" @click="close" :disabled="settings.saving">取消</button>
        <button class="btn btn-primary" @click="onSave" :disabled="settings.saving">
          {{ settings.saving ? '保存中…' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Sun, Moon } from 'lucide-vue-next'
import { SettingsStore } from '../../stores/SettingsStore'
import { ThemeStore } from '../../stores/ThemeStore'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void }>()

const settings = SettingsStore()
const themeStore = ThemeStore()
const toastMsg = ref('')
const DOT_MASK = '●'.repeat(16)

watch(
  () => props.visible,
  (v) => {
    if (v) {
      settings.fetchConfig()
      toastMsg.value = ''
    }
  },
)

function close() {
  emit('update:visible', false)
}

function setTheme(target: 'light' | 'dark') {
  if (themeStore.theme !== target) themeStore.toggleTheme()
}

async function onSave() {
  const ok = await settings.saveConfig()
  if (ok) {
    toastMsg.value = '配置已保存，重启后端后生效'
    setTimeout(() => {
      toastMsg.value = ''
      close()
    }, 1500)
  }
}
</script>

<style scoped>
.settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  -webkit-app-region: no-drag;
}

.settings-modal {
  background: var(--panel-bg, #ffffff);
  color: var(--text-color, #000000);
  border-radius: 10px;
  box-shadow: 0 8px 24px var(--shadow-color, rgba(0, 0, 0, 0.15));
  width: 92%;
  max-width: 520px;
  max-height: 88vh;
  overflow-y: auto;
  border: 1px solid var(--border-color, #d4d4d4);
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px 6px 24px;
}

.settings-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  color: #999;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
}

.close-button:hover {
  background: var(--hover-bg, #efefef);
  color: var(--text-color, #333);
}

.settings-body {
  padding: 8px 24px 4px 24px;
}

.settings-section {
  margin-bottom: 18px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #888;
  margin-bottom: 10px;
  letter-spacing: 0.5px;
}

[data-theme="dark"] .section-title {
  color: #aaa;
}

.theme-toggle {
  display: flex;
  gap: 8px;
}

.theme-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 0;
  border-radius: 6px;
  border: 1px solid var(--border-color, #d4d4d4);
  background: transparent;
  color: var(--text-color, #000);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.theme-option:hover {
  background: var(--hover-bg, #efefef);
}

.theme-option.active {
  background: var(--hover-bg, #efefef);
  border-color: #409eff;
  color: #409eff;
}

.form-group {
  margin-bottom: 12px;
}

.form-label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}

[data-theme="dark"] .form-label {
  color: #bbb;
}

.form-input {
  width: 100%;
  box-sizing: border-box;
  padding: 8px 10px;
  border: 1px solid var(--border-color, #d4d4d4);
  border-radius: 6px;
  background: var(--bg-color, #ffffff);
  color: var(--text-color, #000000);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;
}

.form-input:focus {
  border-color: #409eff;
}

.form-input.has-mask::placeholder {
  color: var(--text-color, #000);
  opacity: 0.85;
  letter-spacing: 1px;
}

.hint-text {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

[data-theme="dark"] .hint-text {
  color: #888;
}

.error-msg {
  color: #f56c6c;
  font-size: 13px;
  margin: 6px 0;
}

.toast-msg {
  color: #67c23a;
  font-size: 13px;
  margin: 6px 0;
}

.settings-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 24px 18px 24px;
  border-top: 1px solid var(--border-color, #eee);
}

.btn {
  padding: 7px 18px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid var(--border-color, #d4d4d4);
  background: transparent;
  color: var(--text-color, #000);
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-default:hover:not(:disabled) {
  background: var(--hover-bg, #efefef);
}

.btn-primary {
  background: #409eff;
  border-color: #409eff;
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
  border-color: #66b1ff;
}
</style>
