export interface Document {
  id: string
  title: string
  eventId?: string
  projectId?: string // 新增：关联项目ID
  eventName: string
  createdAt: string
  updatedAt?: string
  deletedAt?: string // 添加删除时间戳字段
}

export interface DocProject {
  id: string//uuid
  name: string
  projects: string[]//储存其子项目的id
  documents: string[]//储存其子文档的id
}

export interface Content {
  id: string
  content: string
}