import { createRouter, createWebHistory, RouteParams, RouteRecordRaw } from 'vue-router';
import Index from '@/views/index/Index.vue';
import NotFound from '@/views/NotFound.vue';
import { getSurveyName } from '@/util/helpers';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Index',
    component: Index,
  },
  {
    path: '/survey/:year/:season/:preOrPost/',
    name: 'SurveyForm',
    component: () => import('../views/surveyform/SurveyForm.vue'), // Lazy-load complex components
    meta: {
      subtitleFn: (params: RouteParams) => getSurveyName({
        isPreseason: params.preOrPost !== 'post',
        season: Number(params.season),
        year: Number(params.year),
      }),
    },
  },
  {
    path: '/survey/:year/:season/:preOrPost/results/',
    name: 'SurveyResults',
    component: () => import('../views/surveyresults/SurveyResults.vue'),
    meta: {
      subtitleFn: (params: RouteParams) => getSurveyName({
        isPreseason: params.preOrPost !== 'post',
        season: Number(params.season),
        year: Number(params.year),
      }) + ' Results',
    },
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

router.beforeEach(route => {
  const subtitleFn = route.meta.subtitleFn as ((params: RouteParams) => string) | undefined;
  let title = '/r/anime Surveys';
  if (subtitleFn != null) {
    try {
      title += ' - ' + subtitleFn(route.params);
    } catch (e) {
      // Log error, and don't append a subtitle
      console.log(e);
    }
  }
  document.title = title;
})

export default router;
