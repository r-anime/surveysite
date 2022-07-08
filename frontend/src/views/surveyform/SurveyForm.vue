<template>
  <h1 class="page-title">{{ surveyName }}!</h1>

  <Spinner v-if="!surveyFormData" center/>

  <template v-else>
    <div class="row mb-5">
      <div class="col-12 col-md-4">
        <div class="row">
          <div class="col-12 mb-3">
            <label class="form-label" for="input-age">How old are you?</label>
            <input class="form-control" id="input-age" :class="{'is-invalid': validationErrors?.response?.age}" v-model.number="getResponseData().age" @blur="clampAge()" min="10" max="80" type="number" placeholder="Enter your age" aria-describedby="input-age-invalid">
            <FormValidationErrors id="input-age-invalid" :validationErrors="validationErrors?.response?.age"/>
          </div>
          <div class="col-12 mb-3">
            <label class="form-label" for="input-gender">Which gender do you identify as?</label>
            <select class="form-select" id="input-gender" :class="{'is-invalid': validationErrors?.response?.gender}" v-model="getResponseData().gender" aria-describedby="input-gender-invalid">
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
          <SurveyFormMissingAnimeModal :missingAnimeData="missingAnimeData" :survey="surveyFormData.survey"/>
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
          <SurveyFormMissingAnimeModal :missingAnimeData="missingAnimeData" :survey="surveyFormData.survey"/>
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
        <input class="form-check-input" type="checkbox" id="input-link" autocomplete="off" v-model="surveyFormData.isResponseLinkedToUser">
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
import { AnimeData, AnimeNameType, SurveyData, UserData, ValidationErrorData } from '@/util/data';
import { getAnimeName, getSurveyApiUrl, getSurveyName, getSurveyNameFromRoute, isAnimeSeries } from '@/util/helpers';
import { Options, Vue } from 'vue-class-component';
import SurveyFormAnime from './components/SurveyFormAnime.vue';
import _ from 'lodash';
import NotificationService from '@/util/notification-service';
import FormValidationErrors from '@/components/FormValidationErrors.vue';
import SurveyFormMissingAnimeModal from './components/SurveyFormMissingAnimeModal.vue';
import { MissingAnimeData } from './data/missing-anime-data';
import { AnimeResponseData, ResponseData, SurveyFormData, SurveyFormSubmitData } from './data/survey-form-data'
import HttpService from '@/util/http-service';
import UserService from '@/util/user-service';
import dayjs from 'dayjs';
import Spinner from '@/components/Spinner.vue';


@Options({
  components: {
    SurveyFormAnime,
    FormValidationErrors,
    SurveyFormMissingAnimeModal,
    Spinner,
  },
})
export default class SurveyForm extends Vue {
  surveyName = '';
  isSurveyPreseason = true;
  surveyFormData: SurveyFormData | null = null;
  animeSeriesIds: number[] = [];
  specialAnimeIds: number[] = [];
  validationErrors: ValidationErrorData | null = null;

  // Needed here because we want the same data shared by the two identical modals
  missingAnimeData: MissingAnimeData = {
    name: '',
    link: '',
    description: '',
  };

  async created(): Promise<void> {
    this.surveyName = getSurveyNameFromRoute(this.$route);

    const userData = await UserService.getUserData();

    let surveyApiUrl = getSurveyApiUrl(this.$route);
    let responseId = this.$route.query.responseId;
    if (responseId != null) {
      if (Array.isArray(responseId)) {
        responseId = responseId[0];
      }
      surveyApiUrl += '?responseId=' + responseId;
    }
    await HttpService.get<SurveyFormData>(surveyApiUrl, surveyFormData => {
      if (!this.checkAuthentication(userData, surveyFormData.survey)) {
        this.$router.push({ name: 'Index' });
        return;
      }

      this.surveyFormData = surveyFormData;
      this.isSurveyPreseason = surveyFormData.survey.isPreseason;

      const groupedAnime = _.groupBy(surveyFormData.animeDataDict, isAnimeSeries);
      const animeSeries = groupedAnime.true;
      this.animeSeriesIds = _.map(_.orderBy(animeSeries, [anime => getAnimeName(anime, AnimeNameType.JAPANESE_NAME)], ['asc']), anime => anime.id);
      const specialAnime = groupedAnime.false;
      this.specialAnimeIds = _.map(_.orderBy(specialAnime, [anime => getAnimeName(anime, AnimeNameType.JAPANESE_NAME)], ['asc']), anime => anime.id);
    }, failureResponse => {
      NotificationService.pushMsgList(failureResponse.errors?.global ?? (failureResponse.status === 404 ? ['Survey not found!'] : ['An unknown error occurred']), 'danger');
      this.$router.push({name: 'Index'});
    });
  }

  async submit(): Promise<void> {
    if (!this.surveyFormData) {
      return;
    }

    const submitData: SurveyFormSubmitData = {
      responseData: this.surveyFormData.responseData,
      animeResponseDataDict: this.surveyFormData.animeResponseDataDict,
      isResponseLinkedToUser: this.surveyFormData.isResponseLinkedToUser,
    };

    let surveyApiUrl = getSurveyApiUrl(this.$route);
    let responseId = this.$route.query.responseId;
    if (responseId != null) {
      if (Array.isArray(responseId)) {
        responseId = responseId[0];
      }
      surveyApiUrl += '?responseId=' + responseId;
    }
    await HttpService.put<{responseId?: string}, SurveyFormSubmitData>(surveyApiUrl, submitData, submitResponse => {
      NotificationService.push({
        message: 'Your response was successfully sent!',
        color: 'success',
      });
      if (submitResponse.responseId) {
        // TODO: Rework this, should probably use a modal
        this.$router.push({ name: 'SurveyFormLink', query: { responseId: submitResponse.responseId } });
      } else {
        this.$router.push({ name: 'Index' });
      }
    }, failureResponse => {
      NotificationService.pushMsgList(failureResponse.errors?.global ?? [], 'danger');

      if (failureResponse.errors) {
        this.validationErrors = failureResponse.errors.validation ?? null;
        NotificationService.push({
          message: 'One or more of your responses are invalid',
          color: 'danger'
        });
      }
    });
  }

  getResponseData(): ResponseData | undefined {
    return this.surveyFormData?.responseData;
  }

  getAnimeData(id: number): AnimeData | undefined {
    return this.surveyFormData?.animeDataDict[id];
  }

  getAnimeResponseData(id: number): AnimeResponseData | undefined {
    return this.surveyFormData?.animeResponseDataDict[id];
  }

  getAnimeResponseValidationErrors(id: number): ValidationErrorData | null {
    if (this.validationErrors?.animeResponse && !Array.isArray(this.validationErrors.animeResponse)) {
      const validationErrors = this.validationErrors.animeResponse[id] ?? null;
      return Array.isArray(validationErrors) ? null : validationErrors;
    } else {
      return null;
    }
  }

  // Not-so-pretty special workaround for when a user inputs an invalid age, 
  // scrolls down the page and hits 'Submit' only to be greeted with a generic error message,
  // while the error is all the way up on the page
  clampAge(): void {
    if (this.surveyFormData?.responseData?.age && _.isNumber(this.surveyFormData.responseData.age)) {
      // Assume the user typo'd and get the first two numbers, and then clamp
      this.surveyFormData.responseData.age = Math.max(10, Math.min(80, Number(this.surveyFormData.responseData.age.toString().slice(0, 2))));
    }
  }

  isAnimeNew(id: number): boolean | undefined {
    return this.surveyFormData?.isAnimeNewDict[id];
  }

  private checkAuthentication(userData: UserData | null, surveyData: SurveyData): boolean {
    if (!userData) {
      return false;
    }

    const currentTime = dayjs();
    const isSurveyOpen = dayjs(surveyData.openingEpochTime) < currentTime && currentTime < dayjs(surveyData.closingEpochTime);

    if (isSurveyOpen) {
      if (!userData.authenticated) {
        NotificationService.push({
          message: 'You need to be logged in to fill in a survey!',
          color: 'danger',
        });
        return false;
      }
    } else {
      if (!userData.authenticated || !userData.isStaff) {
        NotificationService.push({
          message: getSurveyName(surveyData) + ' is closed!',
          color: 'warning',
        });
        return false;
      }
    }

    return true;
  }
}
</script>
