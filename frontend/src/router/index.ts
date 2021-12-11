import { createRouter, createWebHistory, NavigationGuard, RouteParams, RouteRecordRaw } from 'vue-router';
import Index from '@/views/index/Index.vue';
import NotFound from '@/views/NotFound.vue';
import { getSurveyName } from '@/util/helpers';
import { isInteger } from 'lodash';
import NotificationService from '@/util/notification-service';

function notifyRouteError(relativeUrl: string): void {
  NotificationService.push({
    message: `"${relativeUrl}" was not found`,
    color: 'danger',
  });
}

const confirmValidSurveyRouteParams: NavigationGuard = (to, _from, next) => {
  const year = Number(to.params.year);
  const season = Number(to.params.season);
  const preOrPost = to.params.preOrPost;

  const isValid = isInteger(year) && isInteger(season)
    && season >= 0 && season <= 3
    && (preOrPost === 'pre' || preOrPost === 'post');

  if (isValid) next();
  else {
    next({ name: 'NotFound', replace: false });
    notifyRouteError(`/survey/${year}/${season}/${preOrPost}/`);
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
    component: () => import('../views/surveyform/SurveyForm.vue'), // Lazy-load complex components
    meta: {
      subtitleFn: (params: RouteParams) => getSurveyName({
        isPreseason: params.preOrPost !== 'post',
        season: Number(params.season),
        year: Number(params.year),
      }),
    },
    beforeEnter: confirmValidSurveyRouteParams,
  }, {
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
    beforeEnter: confirmValidSurveyRouteParams,
  }, {
    path: '/:paramMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    beforeEnter: to => to.params.paramMatch ? notifyRouteError(to.params.paramMatch.toString()) : undefined,
  }
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
