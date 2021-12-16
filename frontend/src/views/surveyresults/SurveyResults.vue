<template>
  <template v-if="surveyResultsData">
    <h1 class="page-title">{{ pageTitle }}</h1>
    <router-view/>
  </template>
</template>

<script lang="ts">
import Ajax, { Response } from '@/util/ajax';
import { getSurveyApiUrl, getSurveyName } from '@/util/helpers';
import NotificationService from '@/util/notification-service';
import { computed } from '@vue/runtime-core';
import { Vue, Options } from 'vue-class-component';
import { SurveyResultsData } from './data/survey-results-data';

@Options({
  provide() {
    return {
      surveyResultsDataRef: computed(() => this.surveyResultsData),
    };
  },
})
export default class SurveyResults extends Vue {
  surveyResultsData: SurveyResultsData|null = null;
  pageTitle?: string;

  async created(): Promise<void> {
    const response = await Ajax.get<SurveyResultsData>(getSurveyApiUrl(this.$route) + 'results/');
    if (Response.isErrorData(response.data)) {
      NotificationService.pushMsgList(response.getGlobalErrors(), 'danger');

      this.$router.push({name: 'Index'});
      return;
    }

    this.surveyResultsData = response.data;
    this.pageTitle = getSurveyName(this.surveyResultsData.survey) + ' Results!';
  }
}
</script>