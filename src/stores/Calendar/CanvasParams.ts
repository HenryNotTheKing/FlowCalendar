import { ref } from 'vue'
import { defineStore } from 'pinia'

export const CanvasParams = defineStore('CanvasParams', () => {
  // 定义行高
  const rowHeight = ref(0)
  // 定义列宽
  const colWidth = ref(0)
  // 定义画布宽度
  const canvasWidth = ref(0)
  // 定义画布高度
  const canvasHeight = ref(0)
  // 定义滚动条位置
  const scrollTop = ref(0)
  // 定义当前时间坐标
  const currentTimeCoord = ref(0)
  return {rowHeight, colWidth, scrollTop, currentTimeCoord, canvasWidth, canvasHeight}
})
