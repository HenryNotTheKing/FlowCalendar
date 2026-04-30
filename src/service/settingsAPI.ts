import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

export interface ProviderConfig {
  base_url: string
  api_key_masked: string
  has_key: boolean
}

export interface LlmConfigResponse {
  deepseek: ProviderConfig
  dashscope: ProviderConfig
}

export async function fetchLlmConfig(): Promise<LlmConfigResponse> {
  const { data } = await apiClient.get<LlmConfigResponse>('/llm_config')
  return data
}

export interface ProviderUpdate {
  base_url: string
  /** 空字符串表示保留旧值 */
  api_key: string
}

export async function saveLlmConfig(payload: {
  deepseek: ProviderUpdate
  dashscope: ProviderUpdate
}): Promise<void> {
  await apiClient.post('/llm_config', payload)
}
