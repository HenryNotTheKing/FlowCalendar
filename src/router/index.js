import { createRouter, createWebHistory } from 'vue-router';
import Calendar from '../views/CalendarView.vue';
import TodoList from '../views/TodoView.vue'; 
import Notebook from '../views/NotebookView.vue';

const routes = [
  {
    path: '/',
    name: 'Calendar',
    component: Calendar
  },
  {
    path: '/TodoList',
    name: 'TodoList',
    component: TodoList
  },
  {
    path: '/Notebook',
    name: 'Notebook',
    component: Notebook
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;