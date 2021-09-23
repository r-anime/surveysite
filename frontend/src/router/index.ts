import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Index from '@/views/index/Index.vue';
import NotFound from '@/views/NotFound.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Index',
    component: Index
  },
  {
    path: '/survey/:year/:season/:preOrPost/',
    name: 'Survey',
    component: () => import('../views/surveyform/SurveyForm.vue'), // Lazy-load complex components
  },
  {
    path: '/:_(.*)',
    name: 'NotFound',
    component: NotFound,
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes: routes,
});

export default router;
