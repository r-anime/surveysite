<template>
  <h1 class="mb-4 mx-n2 shadow">{{ surveyName }}</h1>
  <p>{{ survey }}</p>
  <p>{{ animeList }}</p>
</template>

<script lang="ts">
import Ajax from '@/util/ajax';
import { AnimeData, SurveyData } from '@/util/data';
import { getSurveyName } from '@/util/helpers';
import { Options, Vue } from 'vue-class-component';

interface SurveyFormData {
  survey: SurveyData;
  animeList: AnimeData[];
}

@Options({
  components: {
  },
  data() {
    return {
      survey: {} as SurveyData,
      animeList: [] as AnimeData[],
      surveyName: '',
    }
  },
  async mounted() {
    const year = this.$route.params.year as number;
    const season = this.$route.params.season as number;
    const preOrPostSeason = this.$route.params.preOrPost as string;

    const surveyFormData = await Ajax.get<SurveyFormData>(`api/survey/${year}/${season}/${preOrPostSeason}/`);
    this.survey = surveyFormData?.survey;
    this.animeList = surveyFormData?.animeList;
    this.surveyName = getSurveyName(this.survey);
  }
})
export default class Survey extends Vue {}
</script>
