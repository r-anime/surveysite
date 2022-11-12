import { createRouter, createWebHistory } from 'vue-router';
import type { NavigationGuard, RouteLocationRaw, RouteParams, RouteRecordRaw } from 'vue-router';
import IndexPage from '@/views/index/IndexPage.vue';
import NotFoundPage from '@/views/NotFoundPage.vue';
import { getSurveyName } from '@/util/helpers';
import { isInteger } from 'lodash-es';
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
};

type SurveyRouteMeta = {
  subtitleFn?: (params: RouteParams) => string;
};

const routes: Array<RouteRecordRaw & { meta?: SurveyRouteMeta }> = [
  {
    path: '/',
    name: 'Index',
    component: IndexPage,
  }, {
    path: '/survey/:year/:season/:preOrPost/',
    name: 'SurveyForm',
    component: () => import('../views/surveyform/SurveyFormPage.vue'),
    beforeEnter: confirmValidSurveyRouteParams,
    meta: {
      subtitleFn: (params: RouteParams) => getSurveyName({
        isPreseason: params.preOrPost !== 'post',
        season: Number(params.season),
        year: Number(params.year),
      }),
    },
  }, {
    path: '/survey/:year/:season/:preOrPost/',
    name: 'SurveyResults',
    component: () => import(/* webpackChunkName: "group-surveyresults" */ '../views/surveyresults/SurveyResultsPage.vue'),
    beforeEnter: confirmValidSurveyRouteParams,
    meta: {
      subtitleFn: (params: RouteParams) => getSurveyName({
        isPreseason: params.preOrPost !== 'post',
        season: Number(params.season),
        year: Number(params.year),
      }) + ' Results',
    },
    children: [{
      path: 'results/',
      name: 'SurveyResultsSummary',
      component: () => import(/* webpackChunkName: "group-surveyresults" */ '../views/surveyresults/SurveyResultsSummaryPage.vue'),
    }, {
      path: 'fullresults/',
      name: 'SurveyResultsFull',
      component: () => import(/* webpackChunkName: "group-surveyresults" */ '../views/surveyresults/SurveyResultsFullPage.vue'),
    }],
  }, {
    path: '/:paramMatch(.*)*',
    name: 'NotFound',
    component: NotFoundPage,
  },
];

// Remove 'static/' (or 'static') from the base URL so that we get 'example.com/' instead of 'example.com/static/' as base
const defaultBaseUrl = import.meta.env.BASE_URL;
const baseUrl = defaultBaseUrl.substring(0, defaultBaseUrl.lastIndexOf('static'));

const router = createRouter({
  history: createWebHistory(baseUrl),
  routes: routes,
  scrollBehavior: (to, from, savedPosition) => {
    // Don't scroll when we're still in the same view, and the hash is either identical or removed
    if (to.name === from.name && (to.hash === from.hash || !to.hash)) {
      return;
    }

    if (to.hash) {
      return new Promise(resolve => setTimeout(() => resolve({ el: to.hash }), 700));
    } else if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

router.beforeResolve(to => {
  let title = '/r/anime Surveys';
  const routeMeta = to.meta as SurveyRouteMeta;

  if (routeMeta.subtitleFn != null) {
    title += ' - ' + routeMeta.subtitleFn(to.params);
  }
  document.title = title;
});

export default router;
