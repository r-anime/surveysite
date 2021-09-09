<template>
  <h1 class="mb-4 mx-n2 p-3 shadow bg-primary bg-opacity-75 text-light">{{ surveyName }}</h1>

  <template v-if="data">
    <div class="row mb-4">
      <div class="col-12 col-sm-4">
        <div class="row">
          <div class="col-12 mb-3">
            <label class="form-label" for="input-age">How old are you?</label>
            <input class="form-control" id="input-age" v-model="data.responseData.age" min="10" max="80" type="number" placeholder="Enter your age">
          </div>
          <div class="col-12 mb-3">
            <label class="form-label" for="input-gender">Which gender do you identify as?</label>
            <select class="form-control" id="input-gender" v-model="data.responseData.gender">
              <option :value="null" disabled>Select a gender</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </template>
</template>

<script lang="ts">
import Ajax from '@/util/ajax';
import { AnimeData, SurveyData } from '@/util/data';
import { getSurveyName } from '@/util/helpers';
import { Options, Vue } from 'vue-class-component';
import Cookie from 'js-cookie';


interface ResponseData {
  age?: number
  gender?: string
}

interface AnimeResponseData {
  animeId: number
  score: number
  watching: boolean
  underwatched?: boolean
  expectations?: string
}

interface SurveyFormData {
  survey: SurveyData
  responseData: ResponseData
  animeDataList: AnimeData[]
  animeResponseDataList: AnimeResponseData[]
}

@Options({
  components: {
  },
  data() {
    return {
      surveyName: '',
      csrfToken: Cookie.get('csrftoken') ?? '',
      data: null,
    }
  },
  async mounted() {
    const year = this.$route.params.year as number;
    const season = this.$route.params.season as number;
    const preOrPostSeason = this.$route.params.preOrPost as string;

    const surveyFormData = await Ajax.get<SurveyFormData>(`api/survey/${year}/${season}/${preOrPostSeason}/`);
    if (surveyFormData === null) return;

    console.log(surveyFormData);
    this.data = surveyFormData;
    this.surveyName = getSurveyName(surveyFormData.survey);
  }
})
export default class Survey extends Vue {}
</script>
