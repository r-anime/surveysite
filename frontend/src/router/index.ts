import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Index from '@/views/Index.vue';
import NotFound from '@/views/NotFound.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    //name: 'Home',
    //component: Home
    name: 'Index',
    component: Index
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  },
  {
    path: '/survey/:year/:season/:preOrPost/',
    name: 'Survey',
    component: () => import('../views/Survey.vue')
  },
  {
    path: '/:_(.*)',
    name: 'NotFound',
    component: NotFound,
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
