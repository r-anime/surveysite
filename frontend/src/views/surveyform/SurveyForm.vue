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


    <h3 class="mb-4 p-2 rounded shadow row justify-content-between align-items-center bg-primary bg-opacity-75 text-light">
      <div class="col-auto">Anime Series</div>
      <div class="col-auto" id="modal-button-container-series">
        <button variant="light" class="btn btn-light p-n2">Is an anime missing?</button> <!-- Doesn't do anything yet -->
      </div>
    </h3>

    
    <div class="row row-cols-1 row-cols-md-2">
      <div class="col mb-4" v-for="animeId in animeSeriesIds" :key="animeId">
        
        <div class="card shadow-sm h-100">
          <div class="row">
            <!-- Card image -->
            <div class="col-lg-3 col-md-4 col-sm-3 col-4">
              <AnimeImages :animeImages="getAnimeData(animeId).images"/> <!-- Should be rounded with 'rounded-start' -->
            </div>

            <!-- Card info -->
            <div class="col"><div class="card-body">
              <div class="card-title"> <!-- Could the AnimeNames component be used for this? -->
                <h5 class="mb-1">
                  {{ getJapaneseName(getAnimeData(animeId)) }}
                  <span style="font-size:60%;">({{ getShortName(getAnimeData(animeId)) }})</span>
                </h5>
                <h6 style="color:#777777;">
                  {{ getEnglishName(getAnimeData(animeId)) }}
                </h6>
              </div>

              <!-- Watching checkbox -->
              <div class="mb-3">
                <input type="checkbox" class="btn-check" :id="`input-anime-${animeId.toString()}-watching`" autocomplete="off" v-model="getAnimeResponseData(animeId).watching">
                <label class="btn btn-primary" :for="`input-anime-${animeId.toString()}-watching`">{{ getAnimeResponseData(animeId).watching }}</label>
              </div>

              <!-- If post-season && series: Underwatched checkbox -->
              <div class="mb-3"> <!-- v-if="!data.survey.isPreseason" -->
                <input type="checkbox" class="btn-check" :id="`input-anime-${animeId.toString()}-underwatched`" autocomplete="off" v-model="getAnimeResponseData(animeId).underwatched">
                <label class="btn btn-primary" :for="`input-anime-${animeId.toString()}-underwatched`">{{ getAnimeResponseData(animeId).underwatched }}</label>
              </div>

              <!-- Score input -->
              <div class="mb-3">
                <label class="form-label" :for="`input-anime-${animeId.toString()}-score`">How good do you expect this to be? {{ getAnimeResponseData(animeId).score }}-{{ typeof getAnimeResponseData(animeId).score }}</label>
                <select class="form-select" :id="`input-anime-${animeId.toString()}-score`" v-model="getAnimeResponseData(animeId).score">
                  <option :value="(null)">-----</option>
                  <option value="5">5/5 - Great</option>
                  <option value="4">4/5</option>
                  <option value="3">3/5 - Average</option>
                  <option value="2">2/5</option>
                  <option value="1">1/5 - Bad</option>
                </select>
              </div>

              <!-- If post-season && series: Expectations selectbox -->
              <div class="mb-3"> <!-- v-if="!data.survey.isPreseason" -->
                <label class="form-label" :for="`input-anime-${animeId.toString()}-expectations`">Was this a surprise or disappointment? {{ getAnimeResponseData(animeId).expectations }}-{{ typeof getAnimeResponseData(animeId).expectations }}</label>
                <select class="form-select" :id="`input-anime-${animeId.toString()}-expectations`" v-model="getAnimeResponseData(animeId).expectations">
                  <option :value="(null)">-----</option>
                  <option value="S">Surprise</option>
                  <option value="D">Disappointment</option>
                </select>
              </div>
            </div></div>
          </div>
        </div>

      </div>
    </div>

    
    <!-- Special anime also need their own section -->
  </template>
</template>

<script lang="ts">
import Ajax from '@/util/ajax';
import { AnimeData, AnimeNameType, AnimeType, SurveyData } from '@/util/data';
import { getSurveyName, isAnimeSeries } from '@/util/helpers';
import { Options, Vue } from 'vue-class-component';
import Cookie from 'js-cookie';
import AnimeImages from '@/components/AnimeImages.vue';
import { filter, map, orderBy } from 'lodash';


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
}

@Options({
  components: {
    AnimeImages,
  },
  data() {
    return {
      surveyName: '',
      surveyIsPreseason: true,
      csrfToken: Cookie.get('csrftoken') ?? '',
      data: null,
      animeSeriesIds: [],
      specialAnimeIds: [],
    }
  },
  methods: {
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

    getNameOfType(anime: AnimeData, animeNameType: AnimeNameType): string | null {
      const filtered = filter(anime.names, name => name.type == animeNameType);
      if (!filtered.length) return null;

      const ordered = orderBy(filtered, ['isOfficial', 'name'], ['desc', 'asc']);
      return ordered[0].name;
    },
    getJapaneseName(anime: AnimeData): string {
      return this.getNameOfType(anime, AnimeNameType.JAPANESE_NAME);
    },
    getEnglishName(anime: AnimeData): string {
      return this.getNameOfType(anime, AnimeNameType.ENGLISH_NAME);
    },
    getShortName(anime: AnimeData): string {
      return this.getNameOfType(anime, AnimeNameType.SHORT_NAME);
    },
  },
  async mounted() {
    const year = this.$route.params.year as number;
    const season = this.$route.params.season as number;
    const preOrPostSeason = this.$route.params.preOrPost as string;

    const surveyFormData = await Ajax.get<SurveyFormData>(`api/survey/${year}/${season}/${preOrPostSeason}/`);
    if (surveyFormData === null) return;

    console.log(surveyFormData);
    this.data = surveyFormData;
    this.surveyIsPreseason = surveyFormData.survey.isPreseason;
    this.surveyName = getSurveyName(surveyFormData.survey);

    const animeSeries = filter(surveyFormData.animeDataDict, anime => isAnimeSeries(anime));
    const specialAnime = filter(surveyFormData.animeDataDict, anime => !isAnimeSeries(anime));
    this.animeSeriesIds = map(orderBy(animeSeries, [anime => this.getJapaneseName(anime)], ['asc']), anime => anime.id);
    this.specialAnime = map(orderBy(specialAnime, [anime => this.getJapaneseName(anime)], ['asc']), anime => anime.id);
  }
})
export default class Survey extends Vue {}
</script>
