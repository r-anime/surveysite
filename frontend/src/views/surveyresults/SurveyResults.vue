<template>
  <h1 class="page-title">{{ pageTitle }}</h1>

  <Spinner v-if="!surveyResultsData" center/>

  <router-view v-else/>
</template>

<script setup lang="ts">
import Spinner from '@/components/Spinner.vue';
import { getSurveyApiUrl, getSurveyNameFromRoute } from '@/util/helpers';
import HttpService from '@/util/http-service';
import NotificationService from '@/util/notification-service';
import { provide, ref } from 'vue';
import { useRouter } from 'vue-router';
import type { SurveyResultsData } from './data/survey-results-data';

const router = useRouter();
const route = router.currentRoute;

const surveyResultsData = ref<SurveyResultsData | null>(null);
const pageTitle = getSurveyNameFromRoute(route.value) + ' Results!';


provide('surveyResultsData', surveyResultsData);


HttpService.get<SurveyResultsData>(getSurveyApiUrl(route.value) + 'results/', data => {
  surveyResultsData.value = data;
}, failureResponse => {
  NotificationService.pushMsgList(failureResponse.errors?.global ?? (failureResponse.status === 404 ? ['Survey not found!'] : ['An unknown error occurred']), 'danger');
  router.push({name: 'Index'});
});
</script>