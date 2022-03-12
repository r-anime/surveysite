<template>
  <template v-if="surveyResultsData">
    <h1 class="page-title">{{ pageTitle }}</h1>
    <router-view/>
  </template>
</template>

<script lang="ts">
import { getSurveyApiUrl, getSurveyName } from '@/util/helpers';
import HttpService from '@/util/http-service';
import NotificationService from '@/util/notification-service';
import { computed } from '@vue/runtime-core';
import { Vue, Options } from 'vue-class-component';
import { SurveyResultsData } from './data/survey-results-data';

@Options({
  provide() {
    return {
      surveyResultsData: computed(() => this.surveyResultsData),
    };
  },
})
export default class SurveyResults extends Vue {
  surveyResultsData: SurveyResultsData|null = null;
  pageTitle?: string;

  async created(): Promise<void> {
    await HttpService.get<SurveyResultsData>(getSurveyApiUrl(this.$route) + 'results/', surveyResultsData => {
      this.surveyResultsData = surveyResultsData;
      this.pageTitle = getSurveyName(surveyResultsData.survey) + ' Results!';
    }, failureResponse => {
      NotificationService.pushMsgList(failureResponse.errors?.global ?? (failureResponse.status === 404 ? ['Survey not found!'] : ['An unknown error occurred']), 'danger');
      this.$router.push({name: 'Index'});
    });
  }
}
</script>