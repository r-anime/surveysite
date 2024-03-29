<!-- eslint-disable vue/no-mutating-props -->
<template>
  <div class="card shadow-sm h-100">
    <div class="row">
      <!-- Card image -->
      <div class="col-lg-3 col-md-4 col-sm-3 col-4">
        <AnimeImages :animeImages="animeData.images" enableCarouselControls alignStart imgClass="rounded-start"/>
      </div>

      <!-- Card info -->
      <div class="col"><div class="card-body">
        <div class="card-title mb-3">
          <h5 class="mb-1">
            {{ japaneseName }}
            <span style="font-size:60%;" v-if="shortName">({{ shortName }})</span>
          </h5>
          <h6 style="color:#777777;" v-if="englishName">
            {{ englishName }}
          </h6>
        </div>

        <!-- Watching checkbox -->
        <div class="mb-3">
          <span class="mb-1">
            <template v-if="isSurveyPreseason">
              <template v-if="isAnimeNew">
                Will you watch this?
              </template>
              <template v-else>
                Have you watched this and will you continue watching this?
              </template>
            </template>
            <template v-else>
              <BsTooltip v-if="isAnimeSeries" text="At least one episode (of the last cour for multi-cour anime)" />
              Have you watched this?
            </template>
          </span>
          <br/>
          <input type="checkbox" class="btn-check" :id="`input-anime-${animeData.id}-watching`" autocomplete="off" v-model="animeResponseData.watching">
          <label class="btn w-100 mt-1" :class="animeResponseData.watching ? 'btn-outline-success' : 'btn-outline-secondary'" :for="`input-anime-${animeData.id}-watching`">
            {{ animeResponseData.watching ? 'Yes' : 'No' }}
          </label>
        </div>

        <!-- If post-season && series: Underwatched checkbox -->
        <div class="mb-3" v-if="!isSurveyPreseason && isAnimeSeries">
          <span class="mb-1">
            Did you find this underwatched?
          </span>
          <br/>
          <input type="checkbox" class="btn-check" :id="`input-anime-${animeData.id}-underwatched`" autocomplete="off" v-model="animeResponseData.underwatched">
          <label class="btn w-100 mt-1" :class="animeResponseData.underwatched ? 'btn-outline-success' : 'btn-outline-secondary'" :for="`input-anime-${animeData.id}-underwatched`">
            {{ animeResponseData.underwatched ? 'Yes' : 'No' }}
          </label>
        </div>

        <!-- Score input -->
        <div class="mb-3">
          <label class="form-label" :for="`input-anime-${animeData.id}-score`">
            {{
              isSurveyPreseason ?
                isAnimeNew ?
                  'How good do you expect this to be?' :
                  'How good do you expect the remainder to be?' :
                'What did you think of this?'
            }}
          </label>
          <select class="form-select" :id="`input-anime-${animeData.id}-score`" :class="{'is-invalid': validationErrors?.score}" autocomplete="off" v-model.number="animeResponseData.score" :aria-describedby="`input-anime-${animeData.id}-score-invalid`">
            <option :value="(null)">-----</option>
            <option value="5">5/5 - Great</option>
            <option value="4">4/5</option>
            <option value="3">3/5 - Average</option>
            <option value="2">2/5</option>
            <option value="1">1/5 - Bad</option>
          </select>
          <FormValidationErrors :id="`input-anime-${animeData.id}-score-invalid`" :validationErrors="validationErrors?.score"/>
        </div>

        <!-- If post-season && series: Expectations selectbox -->
        <div class="mb-3" v-if="!isSurveyPreseason && isAnimeSeries">
          <label class="form-label" :for="`input-anime-${animeData.id}-expectations`">Was this a surprise or disappointment?</label>
          <select class="form-select" :id="`input-anime-${animeData.id}-expectations`" :class="{'is-invalid': validationErrors?.expectations}" autocomplete="off" v-model="animeResponseData.expectations" :aria-describedby="`input-anime-${animeData.id}-expectations-invalid`">
            <option :value="(null)">-----</option>
            <option value="S">Surprise</option>
            <option value="D">Disappointment</option>
          </select>
          <FormValidationErrors :id="`input-anime-${animeData.id}-expectations-invalid`" :validationErrors="validationErrors?.expectations"/>
        </div>
      </div></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AnimeImages from '@/components/AnimeImages.vue';
import BsTooltip from '@/components/BsTooltip.vue';
import FormValidationErrors from '@/components/FormValidationErrors.vue';
import type { AnimeViewModel, ValidationErrorData } from '@/util/data';
import { AnimeNameType } from '@/util/data';
import { getAnimeName, isAnimeSeries as isAnimeSeriesFn } from '@/util/helpers';
import type { AnimeResponseData } from '../data/survey-form-data';

const props = defineProps<{
  animeData: AnimeViewModel;
  animeResponseData: AnimeResponseData;
  isSurveyPreseason: boolean;
  isAnimeNew: boolean;
  validationErrors?: ValidationErrorData<AnimeResponseData>;
}>();

const isAnimeSeries = isAnimeSeriesFn(props.animeData);

const japaneseName = getAnimeName(props.animeData, AnimeNameType.JAPANESE_NAME);
const englishName = getAnimeName(props.animeData, AnimeNameType.ENGLISH_NAME);
const shortName = getAnimeName(props.animeData, AnimeNameType.SHORT_NAME);
</script>
