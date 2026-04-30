import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchLlmConfig, saveLlmConfig } from '../service/settingsAPI'

export interface ProviderState {
  baseUrl: string
  apiKey: string // 用户新输入的 key（空字符串表示保留旧值）
  apiKeyMasked: string
  hasKey: boolean
}

function emptyProvider(): ProviderState {
  return { baseUrl: '', apiKey: '', apiKeyMasked: '', hasKey: false }
}

export const SettingsStore = defineStore('settings', () => {
  const deepseek = ref<ProviderState>(emptyProvider())
  const dashscope = ref<ProviderState>(emptyProvider())
  const loading = ref(false)
  const saving = ref(false)
  const lastError = ref<string>('')

  async function fetchConfig() {
    loading.value = true
    lastError.value = ''
    try {
      const data = await fetchLlmConfig()
      deepseek.value = {
        baseUrl: data.deepseek.base_url || '',
        apiKey: '',
        apiKeyMasked: data.deepseek.api_key_masked || '',
        hasKey: data.deepseek.has_key,
      }
      dashscope.value = {
        baseUrl: data.dashscope.base_url || '',
        apiKey: '',
        apiKeyMasked: data.dashscope.api_key_masked || '',
        hasKey: data.dashscope.has_key,
      }
    } catch (e: any) {
      lastError.value = e?.message || '加载配置失败'
    } finally {
      loading.value = false
    }
  }

  async function saveConfig(): Promise<boolean> {
    saving.value = true
    lastError.value = ''
    try {
      await saveLlmConfig({
        deepseek: {
          base_url: deepseek.value.baseUrl.trim(),
          api_key: deepseek.value.apiKey, // 空字符串 → 后端保留旧值
        },
        dashscope: {
          base_url: dashscope.value.baseUrl.trim(),
          api_key: dashscope.value.apiKey,
        },
      })
      // 保存成功后刷新一次获取最新掩码
      await fetchConfig()
      return true
    } catch (e: any) {
      lastError.value = e?.message || '保存失败'
      return false
    } finally {
      saving.value = false
    }
  }

  return { deepseek, dashscope, loading, saving, lastError, fetchConfig, saveConfig }
})
