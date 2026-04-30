import { defineStore } from "pinia";
import axios from 'axios';
import { Project, TodoTask } from '../../types/todolist';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api/todo', // 后端API的基础路径
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const TodoApi = defineStore("todoapi", () => {
  // 项目相关的API方法
  const projectAPI = {
    // 获取所有项目
    getAllProjects: async (): Promise<Project[]> => {
      try {
        const response = await api.get('/projects');
        return response.data;
      } catch (error) {
        console.error('获取项目列表失败:', error);
        throw error;
      }
    },

    // 创建项目
    createProject: async (name: string): Promise<Project> => {
      try {
        const response = await api.post('/projects', { name });
        return response.data;
      } catch (error) {
        console.error('创建项目失败:', error);
        throw error;
      }
    },

    // 更新项目
    updateProject: async (id: string, name: string): Promise<Project> => {
      try {
        const response = await api.put(`/projects/${id}`, { name });
        return response.data;
      } catch (error) {
        console.error('更新项目失败:', error);
        throw error;
      }
    },

    // 删除项目
    deleteProject: async (id: string): Promise<void> => {
      try {
        await api.delete(`/projects/${id}`);
      } catch (error) {
        console.error('删除项目失败:', error);
        throw error;
      }
    },
  };

  // 项目标签相关的API方法
  const projectTagAPI = {
    // 为项目添加标签
    addTagToProject: async (projectId: string, tagName: string, color: string): Promise<any> => {
      try {
        const response = await api.post(`/projects/${projectId}/tags`, { name: tagName, color: color });

        return response.data;
      } catch (error) {
        console.error('为项目添加标签失败:', error);
        throw error;
      }
    },

    // 更新项目标签
    updateProjectTag: async (projectId: string, tagName: string, newName: string, newColor: string): Promise<any> => {
      try {
        const response = await api.put(`/projects/${projectId}/tags/${tagName}`, { 
          name: newName, 
          color: newColor 
        });
        return response.data;
      } catch (error) {
        console.error('更新项目标签失败:', error);
        throw error;
      }
    },

    // 从项目删除标签
    deleteProjectTag: async (projectId: string, tagName: string): Promise<void> => {
      try {
        await api.delete(`/projects/${projectId}/tags/${tagName}`);
      } catch (error) {
        console.error('从项目删除标签失败:', error);
        throw error;
      }
    },
  };

  // 任务相关的API方法
  const taskAPI = {
    // 获取所有任务
    getAllTasks: async (): Promise<TodoTask[]> => {
      try {
        const response = await api.get('/tasks');
        return response.data;
      } catch (error) {
        console.error('获取任务列表失败:', error);
        throw error;
      }
    },

    // 创建任务
    createTask: async (task: TodoTask): Promise<TodoTask> => {

      try {
        const response = await api.post('/tasks', task);
        return response.data;
      } catch (error) {
        console.error('创建任务失败:', error);
        throw error;
      }
    },

    // 更新任务
    updateTask: async (id: string, updates: Partial<TodoTask>): Promise<TodoTask> => {
      try {
        const response = await api.put(`/tasks/${id}`, updates);
        return response.data;
      } catch (error) {
        console.error('更新任务失败:', error);
        throw error;
      }
    },

    // 删除任务
    deleteTask: async (id: string): Promise<void> => {
      try {
        await api.delete(`/tasks/${id}`);
      } catch (error) {
        console.error('删除任务失败:', error);
        throw error;
      }
    },
  };

  return {
    projectAPI,
    projectTagAPI,
    taskAPI
  };
});