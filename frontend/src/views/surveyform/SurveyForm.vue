<template>
  <h1 class="page-title">{{ surveyName }}!</h1>

  <Spinner v-if="!surveyFormData" center/>

  <template v-else>
    <div class="row mb-5">
      <div class="col-12 col-md-4">
        <div class="row">
          <div class="col-12 mb-3">
            <label class="form-label" for="input-age">How old are you?</label>
            <input class="form-control" id="input-age" :class="{'is-invalid': validationErrors?.responseData?.age}" v-model.number="surveyFormData.responseData.age" @blur="clampAge()" min="10" max="80" type="number" placeholder="Enter your age" aria-describedby="input-age-invalid">
            <FormValidationErrors id="input-age-invalid" :validationErrors="validationErrors?.responseData?.age"/>
          </div>
          <div class="col-12 mb-3">
            <label class="form-label" for="input-gender">Which gender do you identify as?</label>
            <select class="form-select" id="input-gender" :class="{'is-invalid': validationErrors?.responseData?.gender}" v-model="surveyFormData.responseData.gender" aria-describedby="input-gender-invalid">
              <option :value="(null)">-----</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
            <FormValidationErrors id="input-gender-invalid" :validationErrors="validationErrors?.responseData?.gender"/>
          </div>
        </div>
      </div>
    </div>

    <template v-if="animeSeriesIds && animeSeriesIds.length">
      <h3 class="mb-4 p-2 rounded shadow row justify-content-between align-items-center bg-primary bg-opacity-75 text-light">
        <div class="col-auto">Anime Series</div>
        <div class="col-auto">
        <button class="btn btn-light p-n2" @click="openMissingAnimeModal">
          Is an anime missing?
        </button>
        </div>
      </h3>

      <div class="row row-cols-1 row-cols-md-2">
        <div class="col mb-4" v-for="animeId in animeSeriesIds" :key="animeId">
          <SurveyFormAnime :animeData="getAnimeData(animeId)" :animeResponseData="getAnimeResponseData(animeId)" :isSurveyPreseason="isSurveyPreseason" :isAnimeNew="isAnimeNew(animeId)" :validationErrors="validationErrors?.animeResponseDataDict[animeId]"/>
        </div>
      </div>
    </template>

    <template v-if="specialAnimeIds && specialAnimeIds.length">
      <h3 class="mb-4 p-2 rounded shadow row justify-content-between align-items-center bg-primary bg-opacity-75 text-light">
        <div class="col-auto">Anime Movies/ONAs/OVAs/Specials</div>
        <div class="col-auto">
        <button class="btn btn-light p-n2" @click="openMissingAnimeModal">
          Is an anime missing?
        </button>
        </div>
      </h3>

      <div class="row row-cols-1 row-cols-md-2">
        <div class="col mb-4" v-for="animeId in specialAnimeIds" :key="animeId">
          <SurveyFormAnime :animeData="getAnimeData(animeId)" :animeResponseData="getAnimeResponseData(animeId)" :isSurveyPreseason="isSurveyPreseason" :isAnimeNew="isAnimeNew(animeId)" :validationErrors="validationErrors?.animeResponseDataDict[animeId]"/>
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

<script setup lang="ts">
import FormValidationErrors from '@/components/FormValidationErrors.vue';
import Spinner from '@/components/Spinner.vue';
import SurveyFormAnime from './components/SurveyFormAnime.vue';
import SurveyFormMissingAnimeModal from './components/SurveyFormMissingAnimeModal.vue';

import { AnimeNameType } from '@/util/data';
import type { AnimeData, ValidationErrorData } from '@/util/data';
import { getAnimeName, getSurveyApiUrl, getSurveyNameFromRoute, isAnimeSeries } from '@/util/helpers';
import HttpService from '@/util/http-service';
import NotificationService from '@/util/notification-service';

import type { AnimeResponseData, SurveyFormData, SurveyFormSubmitData } from './data/survey-form-data';
import type { MissingAnimeData } from './data/missing-anime-data';

import _ from 'lodash';
import { useRouter } from 'vue-router';
import { ref } from 'vue';
import { ModalService } from '@/util/modal-service';
import SurveyFormLinkModal from './components/SurveyFormLinkModal.vue';
import LogInModal from '@/components/LogInModal.vue';



const router = useRouter();
const route = router.currentRoute;

const surveyName = getSurveyNameFromRoute(route.value);
const isSurveyPreseason = ref(true);
const surveyFormData = ref<SurveyFormData | null>(null);
const animeSeriesIds = ref<number[]>([]);
const specialAnimeIds = ref<number[]>([]);
const validationErrors = ref<ValidationErrorData<SurveyFormSubmitData> | null>(null);

// Needed here because we want the same data shared by the two identical modals
const missingAnimeData: MissingAnimeData = {
  name: '',
  link: '',
  description: '',
};



{
  let surveyApiUrl = getSurveyApiUrl(route.value);
  let responseId = route.value.query.responseId;
  if (responseId != null) {
    if (Array.isArray(responseId)) {
      responseId = responseId[0];
    }
    surveyApiUrl += '?responseId=' + responseId;
  }

  HttpService.get<SurveyFormData>(surveyApiUrl, data => {
    surveyFormData.value = data;
    isSurveyPreseason.value = surveyFormData.value.survey.isPreseason;

    const groupedAnime = _.groupBy(surveyFormData.value.animeDataDict, isAnimeSeries);

    const animeSeries = groupedAnime.true;
    animeSeriesIds.value = _.map(_.orderBy(animeSeries, [anime => getAnimeName(anime, AnimeNameType.JAPANESE_NAME)], ['asc']), anime => anime.id);

    const specialAnime = groupedAnime.false;
    specialAnimeIds.value = _.map(_.orderBy(specialAnime, [anime => getAnimeName(anime, AnimeNameType.JAPANESE_NAME)], ['asc']), anime => anime.id);
  }, failureResponse => {
    if (failureResponse.status === 401) { // Unauthorized (not logged in)
      ModalService.show(LogInModal, {
        emits: {
          onModalHide: () => router.push({ name: 'Index' }),
        },
      });
    } else {
      NotificationService.pushMsgList(failureResponse.errors?.global ?? ['An unknown error occurred'], 'danger');
      router.push({ name: 'Index' });
    }
  });
}



async function submit(): Promise<void> {
  if (!surveyFormData?.value) {
    return;
  }

  const submitData: SurveyFormSubmitData = {
    responseData: surveyFormData.value.responseData,
    animeResponseDataDict: surveyFormData.value.animeResponseDataDict,
    isResponseLinkedToUser: surveyFormData.value.isResponseLinkedToUser,
  };

  let surveyApiUrl = getSurveyApiUrl(route.value);
  let responseId = route.value.query.responseId;
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
      ModalService.show(SurveyFormLinkModal, {
        data: submitResponse.responseId,
        emits: {
          onModalHide: () => router.push({ name: 'Index' }),
        },
      });
    } else {
      router.push({ name: 'Index' });
    }
  }, failureResponse => {
    NotificationService.pushMsgList(failureResponse.errors?.global ?? [], 'danger');

    if (failureResponse.errors) {
      validationErrors.value = failureResponse.errors.validation ?? null;
      NotificationService.push({
        message: 'One or more of your responses are invalid',
        color: 'danger'
      });
    }
  });
}

function getAnimeData(id: number): AnimeData {
  if (!surveyFormData?.value) throw new TypeError('Failed to get surveyFormData');
  return surveyFormData.value.animeDataDict[id];
}

function getAnimeResponseData(id: number): AnimeResponseData {
  if (!surveyFormData?.value) throw new TypeError('Failed to get surveyFormData');
  return surveyFormData.value.animeResponseDataDict[id];
}

// Not-so-pretty special workaround for when a user inputs an invalid age, 
// scrolls down the page and hits 'Submit' only to be greeted with a generic error message,
// while the error is all the way up on the page
function clampAge(): void {
  if (surveyFormData.value?.responseData?.age != null) {
    if (_.isNumber(surveyFormData.value.responseData.age)) {
      // Assume the user typo'd and get the first two numbers, and then clamp
      surveyFormData.value.responseData.age = Math.max(10, Math.min(80, Number(surveyFormData.value.responseData.age.toString().slice(0, 2))));
    } else {
      surveyFormData.value.responseData.age = null;
    }
  }
}

function isAnimeNew(id: number): boolean {
  if (!surveyFormData?.value) throw new TypeError('Failed to get surveyFormData');
  return surveyFormData.value.isAnimeNewDict[id];
}




function openMissingAnimeModal() {
  ModalService.show(SurveyFormMissingAnimeModal, {
    data: {
      survey: surveyFormData.value?.survey,
      missingAnimeData: missingAnimeData,
    },
  });
}
</script>
