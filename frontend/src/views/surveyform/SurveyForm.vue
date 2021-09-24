<template>
  <h1 class="mb-4 mx-n2 p-3 shadow bg-primary bg-opacity-75 text-light" v-if="surveyName">{{ surveyName }}!</h1>

  <template v-if="data">
    <div class="row mb-5">
      <div class="col-12 col-md-4">
        <div class="row">
          <div class="col-12 mb-3">
            <label class="form-label" for="input-age">How old are you?</label>
            <input class="form-control" id="input-age" :class="validationErrors?.response?.age ? 'is-invalid' : ''" v-model.number="getResponseData().age" min="10" max="80" type="number" placeholder="Enter your age" aria-describedby="input-age-invalid">
            <FormValidationErrors id="input-age-invalid" :validationErrors="validationErrors?.response?.age"/>
          </div>
          <div class="col-12 mb-3">
            <label class="form-label" for="input-gender">Which gender do you identify as?</label>
            <select class="form-select" id="input-gender" :class="validationErrors?.response?.gender ? 'is-invalid' : ''" v-model="getResponseData().gender" aria-describedby="input-gender-invalid">
              <option :value="(null)">-----</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
            <FormValidationErrors id="input-gender-invalid" :validationErrors="validationErrors?.response?.gender"/>
          </div>
        </div>
      </div>
    </div>

    <template v-if="animeSeriesIds && animeSeriesIds.length">
      <h3 class="mb-4 p-2 rounded shadow row justify-content-between align-items-center bg-primary bg-opacity-75 text-light">
        <div class="col-auto">Anime Series</div>
        <div class="col-auto">
          <SurveyFormMissingAnimeModal :missingAnimeData="missingAnimeData" :survey="data.survey"/>
        </div>
      </h3>

      <div class="row row-cols-1 row-cols-md-2">
        <div class="col mb-4" v-for="animeId in animeSeriesIds" :key="animeId">
          <SurveyFormAnime :animeData="getAnimeData(animeId)" :animeResponseData="getAnimeResponseData(animeId)" :isSurveyPreseason="isSurveyPreseason" :isAnimeNew="isAnimeNew(animeId)" :validationErrors="getAnimeResponseValidationErrors(animeId)"/>
        </div>
      </div>
    </template>

    <template v-if="specialAnimeIds && specialAnimeIds.length">
      <h3 class="mb-4 p-2 rounded shadow row justify-content-between align-items-center bg-primary bg-opacity-75 text-light">
        <div class="col-auto">Anime Movies/ONAs/OVAs/Specials</div>
        <div class="col-auto">
          <SurveyFormMissingAnimeModal :missingAnimeData="missingAnimeData" :survey="data.survey"/>
        </div>
      </h3>

      <div class="row row-cols-1 row-cols-md-2">
        <div class="col mb-4" v-for="animeId in specialAnimeIds" :key="animeId">
          <SurveyFormAnime :animeData="getAnimeData(animeId)" :animeResponseData="getAnimeResponseData(animeId)" :isSurveyPreseason="isSurveyPreseason" :isAnimeNew="isAnimeNew(animeId)" :validationErrors="getAnimeResponseValidationErrors(animeId)"/>
        </div>
      </div>
    </template>


    <div class="row justify-content-end">
      <div class="col-6 col-md-3 mb-3 form-check">
        <input class="form-check-input" type="checkbox" id="input-link" autocomplete="off" v-model="data.isResponseLinkedToUser">
        <label for="input-link">Link this response to your account?</label>
        <br>
        <span class="text-muted" style="font-size:80%;">
          By doing this, you can easily edit your response on any of your devices simply by re-opening this survey while logged in to the same account.
        </span>
      </div>
    </div>


    <div class="row justify-content-between">
      <div class="col-auto">
        <router-link to="/" class="btn btn-secondary">Back to index</router-link>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary" @click="submit()">Submit</button>
      </div>
    </div>
  </template>
</template>

<script lang="ts">
import Ajax, { Response } from '@/util/ajax';
import { AnimeData, AnimeNameType, SurveyData } from '@/util/data';
import { getAnimeName, getSurveyName, isAnimeSeries } from '@/util/helpers';
import { Options, Vue } from 'vue-class-component';
import SurveyFormAnime from './components/SurveyFormAnime.vue';
import { groupBy, map, orderBy } from 'lodash';
import NotificationService from '@/util/notification-service';
import FormValidationErrors from '@/components/FormValidationErrors.vue';
import SurveyFormMissingAnimeModal from './components/SurveyFormMissingAnimeModal.vue';


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
  isResponseLinkedToUser: boolean;
}

interface SurveyFromSubmitData {
  responseData: ResponseData;
  animeResponseDataDict: Record<number, AnimeResponseData>;
  isResponseLinkedToUser: boolean;
}

interface MissingAnimeData {
  name: string;
  link: string;
  description: string;
}

@Options({
  components: {
    SurveyFormAnime,
    FormValidationErrors,
    SurveyFormMissingAnimeModal,
  },
  data() {
    return {
      surveyName: '',
      isSurveyPreseason: true,
      data: null,
      animeSeriesIds: [],
      specialAnimeIds: [],
      validationErrors: null,

      // Needed here because we want the same data shared by the two identical modals
      missingAnimeData: {
        name: '',
        link: '',
        description: '',
      } as MissingAnimeData,
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
    getAnimeResponseValidationErrors(id: number) {
      if (this.validationErrors?.animeResponse) {
        return this.validationErrors.animeResponse[id] ?? null;
      } else {
        return null;
      }
    },
    isAnimeNew(id: number): boolean {
      const data = this.data as SurveyFormData;
      return data.isAnimeNewDict[id];
    },

    async submit() {
      const data = this.data as SurveyFormData;
      const submitData = {
        responseData: data.responseData,
        animeResponseDataDict: data.animeResponseDataDict,
        isResponseLinkedToUser: data.isResponseLinkedToUser,
      } as SurveyFromSubmitData;

      const response = await Ajax.post(this.getApiUrl(), submitData);
      if (Response.isErrorData(response.data)) {
        // Should also handle validation errors
        NotificationService.pushMsgList(response.getGlobalErrors(null), 'danger');

        const validationErrors = response.data.errors.validation ?? null;
        if (validationErrors != null) {
          this.validationErrors = validationErrors;
          NotificationService.push({
            message: 'One or more of your responses are invalid',
            color: 'danger'
          });
          console.log(validationErrors);
        }
      } else {
        NotificationService.push({
          message: 'Your response was successfully sent!',
          color: 'success',
        });
        this.$router.push({name: 'Index'});
      }
    },
  },
  async mounted() {
    const response = await Ajax.get<SurveyFormData>(this.getApiUrl());
    if (Response.isErrorData(response.data)) {
      NotificationService.pushMsgList(response.getGlobalErrors(), 'danger');

      this.$router.push({name: 'Index'});
      return;
    }

    const surveyFormData = response.data;

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
