import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { TodoTask } from '../../types/todolist';
import { Project } from '../../types/todolist';
import { TodoApi } from './TodoAPI';


export const ProjectParams = defineStore('projectParams', () => {
  const api = TodoApi();
  const projects = ref([] as Project[])
  const activeProjectId = ref(null as string | null)

  const init = async () => {
    projects.value = await api.projectAPI.getAllProjects();
  }

  function addProject(name: string) {
    const newProject: Project = {
      id: crypto.randomUUID(), // 简单的ID生成方式
      name,
      tags: [],
      todos: [],
    };
    projects.value.push(newProject);
    activeProjectId.value = newProject.id;
  }
  
  function removeProject(id: string) {
    // 防止删除默认项目
    if (id === 'rcwd') {
      throw new Error('默认项目不能被删除');
    }
    projects.value = projects.value.filter(project => project.id !== id);
      if (activeProjectId.value === id) {
        activeProjectId.value = projects.value.length > 0 ? projects.value[0].id : null;
      }
    }
    
    function updateProjectName(id: string, name: string) {
      // 防止修改默认项目名称
      if (id === 'rcwd') {
        throw new Error('默认项目名称不能被修改');
      }
      const project = projects.value.find(project => project.id === id);
      if (project) {
        project.name = name;
      }
    }
    
    function updateProject(id: string, updates: Partial<Project>) {
      // 防止修改默认项目
      if (id === 'rcwd') {
        throw new Error('默认项目不能被修改');
      }
      const project = projects.value.find(project => project.id === id);
      if (project) {
        Object.assign(project, updates);
      }
    }
    
    function addTodoToProject(projectId: string, title: string, date?: Date) {
      const project = projects.value.find(project => project.id === projectId);
      if (project) {
        const newTodo: TodoTask = {
          id: crypto.randomUUID(),
          projectId: projectId,
          title,
          date: date || new Date(),
          tag: "",
          priority: 0,
          completed: false,
          fadeOut: false,
          fadeIn: false,
          completionTimer: null,
          repeat: false,
          recurrence: null,
        };
        project.todos.push(newTodo);
        api.taskAPI.createTask(newTodo)
      }
    }
    function updateProjectTodo(projectId: string, todoId: string, updates: Partial<TodoTask>) {
      const project = projects.value.find(project => project.id === projectId);
      if (project) {
        const todo = project.todos.find(todo => todo.id === todoId);
        if (todo) {
          Object.assign(todo, updates);
          api.taskAPI.updateTask(todoId, updates);
        }else{
          project.todos.push(updates as TodoTask); // 如果找不到任务，则添加新任务
          api.taskAPI.createTask(updates as TodoTask);
        }
      }
    }


    function removeTodoFromProject(projectId: string, todoId: string) {
      const project = projects.value.find(project => project.id === projectId);
      if (project) {
        project.todos = project.todos.filter(todo => todo.id !== todoId);
        api.taskAPI.deleteTask(todoId);
      }
    }
    
    function updateTodoStatus(projectId: string, todoId: string, completed: boolean) {
      const project = projects.value.find(project => project.id === projectId);
      if (project) {
        const todo = project.todos.find(todo => todo.id === todoId);
        if (todo) {
          todo.completed = completed;
        }
      }
    }

    const activeProject = computed(() => {
      return projects.value.find(project => project.id === activeProjectId.value) || null;
    })

    return {
        projects,
        activeProjectId,
        addProject,
        removeProject,
        updateProjectName,
        updateProject,
        addTodoToProject,
        removeTodoFromProject,
        updateTodoStatus,
        updateProjectTodo,
        init,
        activeProject,
    }
});