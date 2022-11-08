<template>
  <div class="row row-cols-1">
    <div class="col mb-1">
      <h5>
        {{ surveyName }}
        <small v-if="isSurveyFinished" class="text-muted" style="font-size:80%;">Finished</small>
        <span v-else-if="isSurveyUpcoming" class="badge bg-secondary rounded-pill" style="font-size:80%">Upcoming</span>
        <span v-else class="badge bg-primary rounded-pill" style="font-size:80%">Ongoing</span>
      </h5>
    </div>
    
    <template v-if="isSurveyFinished">
      <div v-for="(animeResultsList, resultType) in survey.animeResults" :key="resultType" class="col mb-3">
        <div class="row">
          <div class="col py-1 px-2 w-100">
            {{ getResultTypeTitle(resultType) }}
          </div>
        </div>
        <div class="row px-2 align-items-center">
          <div class="col px-0" :class="idx==0 ? '' : 'd-lg-block d-none'" v-for="(animeResults, idx) in animeResultsList" :key="idx">
            <IndexSurveyAnime :animeResults="animeResults"/>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="col position-relative">
        <div class="row row-cols-lg-6 px-3 align-items-center opacity-25">
          <div v-for="(image, imageIdx) in survey.animeImages"
               :key="imageIdx"
               class="col p-1"
               :class="imageIdx>=8 ? 'd-lg-block d-none' : imageIdx>=6 ? 'd-md-block d-none' : ''">
            <img :src="image.urlSmall" :alt="image.name" class="img-fluid">
          </div>
        </div>

        <div class="row align-items-center justify-content-center h-100 w-100 position-absolute top-0 start-0">
          <div class="col text-center fs-1" style="text-shadow: 0 0 2px rgba(0, 0, 0, 0.3);">
            {{ isSurveyUpcoming ? `Open ${openingTime?.format('MMM D, HH:mm') ?? 'soon'}!` : 'Survey open!' }}
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { ResultType } from '@/util/data';
import { getSurveyName } from '@/util/helpers';
import IndexSurveyAnime from './IndexSurveyAnime.vue';
import type { IndexSurveyViewModel } from '../data/index-survey-data';
import dayjs from 'dayjs';

const props = defineProps<{
  survey: IndexSurveyViewModel;
}>();

const surveyName = getSurveyName(props.survey);
const openingTime = dayjs(props.survey.openingEpochTime);
const closingTime = dayjs(props.survey.closingEpochTime);
const isSurveyUpcoming = dayjs() < openingTime;
const isSurveyFinished = closingTime < dayjs();


function getResultTypeTitle(resultType: ResultType): string {
  const resultTypeNumber = Number(resultType);
  switch (resultTypeNumber) {
    case ResultType.POPULARITY:
      return 'Most popular anime';
    case ResultType.SCORE:
      return props.survey.isPreseason ? 'Most anticipated anime' : 'Most highly regarded anime';
    default:
      return ResultType[resultTypeNumber];
  }
}
</script>
