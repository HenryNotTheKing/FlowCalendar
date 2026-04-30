import { RecurrenceRule } from "./schedule";

export interface TodoTask {
  id: string;
  originalTaskId?: string;
  projectId?: string; // 新增：关联项目ID
  title: string;
  date: Date;
  tag: string;
  priority: number;
  completed: boolean;
  fadeOut: boolean;
  fadeIn: boolean;
  completionTimer: number | null | ReturnType<typeof setTimeout>;
  repeat: boolean;
  recurrence: RecurrenceRule | null; 
}

export interface Project {
  id: string;
  name: string; // 新增：项目名称
  tags: {
    name: string;
    color: string;
  }[];
  todos: TodoTask[];
}