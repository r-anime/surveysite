<template>
  <h1 class="mb-4 mx-n2 p-3 shadow bg-primary bg-opacity-75 text-light" v-if="surveyName">{{ surveyName }}!</h1>

  <template v-if="data">
    <div class="row mb-5">
      <div class="col-12 col-md-4">
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


    <!-- Should only display anime series, special anime also need their own section -->
    <h3 class="mb-4 p-2 rounded shadow row justify-content-between align-items-center bg-primary bg-opacity-75 text-light">
      <div class="col-auto">Anime Series</div>
      <div class="col-auto" id="modal-button-container-series">
        <button variant="light" class="btn btn-light p-n2">Is an anime missing?</button> <!-- Doesn't do anything yet -->
      </div>
    </h3>

    
    <div class="row row-cols-1 row-cols-md-2">
      <div class="col mb-4" v-for="(animeData, animeIdx) in data.animeDataList" :key="animeIdx">
        
        <div class="card shadow-sm h-100">
          <div class="row">
            <!-- Card image -->
            <div class="col-lg-3 col-md-4 col-sm-3 col-4">
              <AnimeImages :animeImages="animeData.images"/> <!-- Should be rounded with 'rounded-start' -->
            </div>

            <!-- Card info -->
            <div class="col"><div class="card-body">
              <div class="card-title"> <!-- Could the AnimeNames component be used for this? -->
                <h5 class="mb-1">
                  {{ animeData.names[0].name }} <!-- Should be Japanese title (with shortened name small) -->
                </h5>
                <h6 style="color:#777777;" v-for="(nameData, nameIdx) in animeData.names.slice(1)" :key="nameIdx">
                  {{ nameData.name }} <!-- Should be English title -->
                </h6>
              </div>

              <div>Input</div>

              <!-- Watching checkbox -->

              <!-- If post-season && series: Underwatched checkbox -->

              <!-- Score input -->

              <!-- If post-season && series: Expectations selectbox -->
            </div></div>
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
import AnimeImages from '@/components/AnimeImages.vue';


interface ResponseData {
  age?: number;
  gender?: string;
}

interface AnimeResponseData {
  animeId: number;
  score: number;
  watching: boolean;
  underwatched?: boolean;
  expectations?: string;
}

interface SurveyFormData {
  survey: SurveyData;
  responseData: ResponseData;
  animeDataList: AnimeData[];
  animeResponseDataList: AnimeResponseData[];
}

@Options({
  components: {
    AnimeImages,
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
