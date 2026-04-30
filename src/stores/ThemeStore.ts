import { ref, watch } from 'vue'
import { defineStore } from 'pinia'

export const ThemeStore = defineStore('theme', () => {
  // 主题状态：'light' 或 'dark'
  const theme = ref<'light' | 'dark'>('light')

  // 切换主题
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    // 保存到 localStorage
    if (window.ipcRenderer) {
      window.ipcRenderer.send('set-theme', theme.value);
    }
    localStorage.setItem('theme', theme.value)
    // 应用主题到 document
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  // 初始化主题
  function initTheme() {
    // 从 localStorage 获取主题设置，如果没有则默认为 light
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null
    if (savedTheme) {
      theme.value = savedTheme
      if (window.ipcRenderer) {
        window.ipcRenderer.send('set-theme', theme.value);
      }
    } else {
      // 检查系统主题偏好
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      theme.value = prefersDark ? 'dark' : 'light'
    }
    // 应用主题到 document
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  // 监听系统主题偏好变化
  watch(theme, () => {
    document.documentElement.setAttribute('data-theme', theme.value)
  })

  return { theme, toggleTheme, initTheme }
})