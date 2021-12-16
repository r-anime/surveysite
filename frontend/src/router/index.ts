import { createRouter, createWebHistory, NavigationGuard, RouteLocationRaw, RouteParams, RouteRecordRaw } from 'vue-router';
import Index from '@/views/index/Index.vue';
import NotFound from '@/views/NotFound.vue';
import { getSurveyName } from '@/util/helpers';
import { isInteger } from 'lodash';
import NotificationService from '@/util/notification-service';

const confirmValidSurveyRouteParams: NavigationGuard = to => {
  const year = Number(to.params.year);
  const season = Number(to.params.season);
  const preOrPost = to.params.preOrPost;

  const isValid = isInteger(year) && isInteger(season)
    && season >= 0 && season <= 3
    && (preOrPost === 'pre' || preOrPost === 'post');

  if (!isValid) {
    NotificationService.push({
      message: `"/survey/${to.params.year}/${to.params.season}/${to.params.preOrPost}/" is not a valid survey URL`,
      color: 'danger',
    });
    return {
      name: 'NotFound',
      replace: true,
    } as RouteLocationRaw;
  }
}

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Index',
    component: Index,
  }, {
    path: '/survey/:year/:season/:preOrPost/',
    name: 'SurveyForm',
    component: () => import('../views/surveyform/SurveyForm.vue'),
    beforeEnter: confirmValidSurveyRouteParams,
    meta: {
      subtitleFn: (params: RouteParams) => getSurveyName({
        isPreseason: params.preOrPost !== 'post',
        season: Number(params.season),
        year: Number(params.year),
      }),
    },
  }, {
    path: '/survey/:year/:season/:preOrPost/results/',
    name: 'SurveyResults',
    component: () => import(/* webpackChunkName: "group-surveyresults" */ '../views/surveyresults/SurveyResults.vue'),
    beforeEnter: confirmValidSurveyRouteParams,
    meta: {
      subtitleFn: (params: RouteParams) => getSurveyName({
        isPreseason: params.preOrPost !== 'post',
        season: Number(params.season),
        year: Number(params.year),
      }) + ' Results',
    },
    children: [{
      path: '',
      name: 'SurveyResultsSummary',
      component: () => import(/* webpackChunkName: "group-surveyresults" */ '../views/surveyresults/SurveyResultsSummary.vue'),
    }, {
      path: 'full/',
      name: 'SurveyResultsFull',
      component: () => import(/* webpackChunkName: "group-surveyresults" */ '../views/surveyresults/SurveyResultsFull.vue'),
    }],
  }, {
    path: '/:paramMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes: routes,
});

router.beforeResolve(to => {
  let title = '/r/anime Surveys';

  const subtitleFn = to.meta.subtitleFn as ((params: RouteParams) => string) | undefined;
  if (subtitleFn != null) {
    title += ' - ' + subtitleFn(to.params);
  }
  document.title = title;
});

export default router;
