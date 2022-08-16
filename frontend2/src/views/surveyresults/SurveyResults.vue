<template>
  <h1 class="page-title">{{ pageTitle }}</h1>

  <Spinner v-if="!surveyResultsData" center/>

  <router-view v-else/>
</template>

<script lang="ts">
import Spinner from '@/components/Spinner.vue';
import { getSurveyApiUrl, getSurveyNameFromRoute } from '@/util/helpers';
import HttpService from '@/util/http-service';
import NotificationService from '@/util/notification-service';
import { computed } from 'vue';
import { Vue, Options } from 'vue-class-component';
import type { SurveyResultsData } from './data/survey-results-data';

@Options({
  components: {
    Spinner,
  },
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
    this.pageTitle = getSurveyNameFromRoute(this.$route) + ' Results!';

    await HttpService.get<SurveyResultsData>(getSurveyApiUrl(this.$route) + 'results/', surveyResultsData => {
      this.surveyResultsData = surveyResultsData;
    }, failureResponse => {
      NotificationService.pushMsgList(failureResponse.errors?.global ?? (failureResponse.status === 404 ? ['Survey not found!'] : ['An unknown error occurred']), 'danger');
      this.$router.push({name: 'Index'});
    });
  }
}
</script>