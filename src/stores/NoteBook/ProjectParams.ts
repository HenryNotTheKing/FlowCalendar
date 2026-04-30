import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { DocProject, Document } from '../../types/document';
import { DocStore } from './DocumentStore';
const API_BASE_URL = 'http://localhost:5000/api'
export const ProjectParams= defineStore('project', () => {
  const projects = ref([] as DocProject[]);
  const activeProjectId = ref(null as string | null);

  // 从后端获取所有项目
  const fetchProjects = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/projects`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const projectData = await response.json()
      projects.value = projectData
    } catch (error) {
      console.error('获取项目失败:', error)
      throw error
    }
  }

  // 创建新项目
  const createProject = async (name: string) => {
    try {

      const payload: DocProject = {
        id:crypto.randomUUID(),
        name,
        projects: [],
        documents: []
      }

      const response = await fetch(`${API_BASE_URL}/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const newProject = await response.json()
      projects.value.push(newProject)
      return newProject
    } catch (error) {
      console.error('创建项目失败:', error)
      throw error
    }
  }

  // 更新项目名称
  const updateProjectName = async (id: string, newName: string) => {
    try {
      const project = projects.value.find(project => project.id === id)
      if (!project) {
        throw new Error('项目不存在')
      }
      project.name = newName
      const response = await fetch(`${API_BASE_URL}/projects/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(project)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const updatedProject = await response.json()
      const index = projects.value.findIndex(project => project.id === id)
      if (index !== -1) {
        projects.value[index] = updatedProject
      }
      return updatedProject
    } catch (error) {
      console.error('更新项目失败:', error)
      throw error
    }
  }

  // 删除项目
  const deleteProject = async (id: string) => {
    // 阻止删除默认项目
    if (id === 'rcwd') {
      throw new Error('不能删除默认项目');
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/projects/${id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const index = projects.value.findIndex(project => project.id === id)
      if (index !== -1) {
        projects.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除项目失败:', error)
      throw error
    }
  }
  
  // 向项目添加文档
  const addDocumentToProject = async (projectId: string, newDoc: Document) => {
    try {
      console.log('向项目添加文档:', projectId, newDoc)
      // 更新项目中的文档列表
      const project = projects.value.find(p => p.id === projectId)
      if (project) {
        // 检查文档是否已存在于项目中
        const exists = project.documents.some(id => id === newDoc.id)
        if (!exists) {
          project.documents.push(newDoc.id)
          console.log('添加文档到项目:', project)
          const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {

            method: 'PUT',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(project)
          })
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
        }
        return newDoc
      }
    } catch (error) {
      console.error('向项目添加文档失败:', error)
      throw error
    }
  }

  // 从项目中移除文档
  const removeDocumentFromProject = async (projectId: string, docId: string) => {
    try {
      // 更新项目中的文档列表
      const project = projects.value.find(p => p.id === projectId)
      if (project) {
        // 从项目文档列表中移除文档ID
        const docIndex = project.documents.indexOf(docId);
        if (docIndex > -1) {
          project.documents.splice(docIndex, 1);
          
          const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(project)
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        }
        return project;
      }
    } catch (error) {
      console.error('从项目中移除文档失败:', error);
      throw error;
    }
  }

  const addProjectToProject = async (projectId: string, newProject: DocProject) => {
    try {
      // 更新项目中的文档列表
      const project = projects.value.find(p => p.id === projectId)
      if (project) {
        // 检查文档是否已存在于项目中
        const exists = project.projects.some(id => id === newProject.id)
        if (!exists) {
          project.projects.push(newProject.id)
          const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(project)
          })
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
        }
        return newProject
      }
    } catch (error) {
      console.error('向项目添加项目失:', error)
      throw error
    }
  }


  // 获取项目中的文档
  const getProjectDocuments = (projectId: string) => {
    const project = projects.value.find(p => p.id === projectId);
    if (!project) return [];
    
    // 获取文档存储实例
    const docStore = DocStore();
    
    // 根据文档ID从文档存储中获取完整文档对象
    return project.documents.map(id => {
      const doc = docStore.documents.find(d => d.id === id);
      return doc || { id } as Document;
    });
  };

  const activeProject = computed(() => {
    return projects.value.find(project => project.id === activeProjectId.value) || null;
  });

  // 获取子项目
  const getSubProjects = (projectId: string) => {
    const project = projects.value.find(p => p.id === projectId);
    if (!project) return [];
    return project.projects.map(id => projects.value.find(p => p.id === id)).filter(Boolean) as DocProject[];
  };

  return {
    projects,
    activeProjectId,
    activeProject,
    addProjectToProject,
    fetchProjects,
    createProject,
    updateProjectName,
    deleteProject,
    addDocumentToProject,
    removeDocumentFromProject,
    getSubProjects,
    getProjectDocuments,
  }
});