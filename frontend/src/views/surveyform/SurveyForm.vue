<template>
  <h1 class="mb-4 mx-n2 p-3 shadow bg-primary bg-opacity-75 text-light" v-if="surveyName">{{ surveyName }}!</h1>

  <template v-if="data">
    <div class="row mb-5">
      <div class="col-12 col-md-4">
        <div class="row">
          <div class="col-12 mb-3">
            <label class="form-label" for="input-age">How old are you?</label>
            <input class="form-control" id="input-age" v-model="getResponseData().age" min="10" max="80" type="number" placeholder="Enter your age">
          </div>
          <div class="col-12 mb-3">
            <label class="form-label" for="input-gender">Which gender do you identify as?</label>
            <select class="form-select" id="input-gender" v-model="getResponseData().gender">
              <option :value="(null)">-----</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <template v-if="animeSeriesIds && animeSeriesIds.length">
      <h3 class="mb-4 p-2 rounded shadow row justify-content-between align-items-center bg-primary bg-opacity-75 text-light">
        <div class="col-auto">Anime Series</div>
        <div class="col-auto" id="modal-button-container-series">
          <button variant="light" class="btn btn-light p-n2">Is an anime missing?</button> <!-- Doesn't do anything yet -->
        </div>
      </h3>

      <div class="row row-cols-1 row-cols-md-2">
        <div class="col mb-4" v-for="animeId in animeSeriesIds" :key="animeId">
          <SurveyFormAnime :animeData="getAnimeData(animeId)" :animeResponseData="getAnimeResponseData(animeId)" :isSurveyPreseason="isSurveyPreseason" :isAnimeNew="isAnimeNew(animeId)"/>
        </div>
      </div>
    </template>

    <template v-if="specialAnimeIds && specialAnimeIds.length">
      <h3 class="mb-4 p-2 rounded shadow row justify-content-between align-items-center bg-primary bg-opacity-75 text-light">
        <div class="col-auto">Anime Movies/ONAs/OVAs/Specials</div>
        <div class="col-auto" id="modal-button-container-series">
          <button variant="light" class="btn btn-light p-n2">Is an anime missing?</button> <!-- Doesn't do anything yet -->
        </div>
      </h3>

      <div class="row row-cols-1 row-cols-md-2">
        <div class="col mb-4" v-for="animeId in specialAnimeIds" :key="animeId">
          <SurveyFormAnime :animeData="getAnimeData(animeId)" :animeResponseData="getAnimeResponseData(animeId)" :isSurveyPreseason="isSurveyPreseason" :isAnimeNew="isAnimeNew(animeId)"/>
        </div>
      </div>
    </template>

    <button class="btn btn-primary" @click="submit()">Submit</button>
  </template>
</template>

<script lang="ts">
import Ajax from '@/util/ajax';
import { AnimeData, AnimeNameType, SurveyData } from '@/util/data';
import { getAnimeName, getSurveyName, isAnimeSeries } from '@/util/helpers';
import { Options, Vue } from 'vue-class-component';
import SurveyFormAnime from './components/SurveyFormAnime.vue';
import { groupBy, map, orderBy } from 'lodash';


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
  animeDataDict: Record<number, AnimeData>;
  animeResponseDataDict: Record<number, AnimeResponseData>;
  isAnimeNewDict: Record<number, boolean>;
}

@Options({
  components: {
    SurveyFormAnime,
  },
  data() {
    return {
      surveyName: '',
      isSurveyPreseason: true,
      data: null,
      animeSeriesIds: [],
      specialAnimeIds: [],
    };
  },
  methods: {
    getApiUrl(): string {
      const year = this.$route.params.year as number;
      const season = this.$route.params.season as number;
      const preOrPostSeason = this.$route.params.preOrPost as string;
      
      return `api/survey/${year}/${season}/${preOrPostSeason}/`;
    },

    getResponseData(): ResponseData {
      const data = this.data as SurveyFormData;
      return data.responseData;
    },
    getAnimeData(id: number): AnimeData {
      const data = this.data as SurveyFormData;
      return data.animeDataDict[id];
    },
    getAnimeResponseData(id: number): AnimeResponseData {
      const data = this.data as SurveyFormData;
      return data.animeResponseDataDict[id];
    },
    isAnimeNew(id: number): boolean {
      const data = this.data as SurveyFormData;
      return data.isAnimeNewDict[id];
    },

    async submit() {
      await Ajax.post(this.getApiUrl(), this.data);
    },
  },
  async mounted() {
    const surveyFormData = await Ajax.get<SurveyFormData>(this.getApiUrl());
    if (surveyFormData === null) return;

    console.log(surveyFormData);
    this.data = surveyFormData;
    this.isSurveyPreseason = surveyFormData.survey.isPreseason;
    this.surveyName = getSurveyName(surveyFormData.survey);

    const groupedAnime = groupBy(surveyFormData.animeDataDict, isAnimeSeries);
    const animeSeries = groupedAnime.true;
    this.animeSeriesIds = map(orderBy(animeSeries, [anime => getAnimeName(anime, AnimeNameType.JAPANESE_NAME)], ['asc']), anime => anime.id);
    const specialAnime = groupedAnime.false;
    this.specialAnimeIds = map(orderBy(specialAnime, [anime => getAnimeName(anime, AnimeNameType.JAPANESE_NAME)], ['asc']), anime => anime.id);
  },
})
export default class SurveyForm extends Vue {}
</script>
