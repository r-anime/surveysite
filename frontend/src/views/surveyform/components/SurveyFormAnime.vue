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
          <DropdownFormControl :id="`input-anime-${animeData.id}-score`"
                               :validationErrors="validationErrors?.score"
                               :options="scoreOptions"
                               v-model="animeResponseData.score">
            {{
              isSurveyPreseason ?
                isAnimeNew ?
                  'How good do you expect this to be?' :
                  'How good do you expect the remainder to be?' :
                'What did you think of this?'
            }}
          </DropdownFormControl>
        </div>

        <!-- If post-season && series: Expectations selectbox -->
        <div class="mb-3" v-if="!isSurveyPreseason && isAnimeSeries">
          <DropdownFormControl :id="`input-anime-${animeData.id}-expectations`"
                               :validationErrors="validationErrors?.expectations"
                               :options="expectationOptions"
                               v-model="animeResponseData.expectations">
            Was this a surprise or disappointment?
          </DropdownFormControl>
        </div>
      </div></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AnimeImages from '@/components/AnimeImages.vue';
import BsTooltip from '@/components/BsTooltip.vue';
import DropdownFormControl from '@/components/DropdownFormControl.vue';
import type { AnimeViewModel, SelectInputOption, ValidationErrorData } from '@/util/data';
import { AnimeNameType } from '@/util/data';
import { getAnimeName, isAnimeSeries as isAnimeSeriesFn } from '@/util/helpers';
import { computed } from 'vue';
import type { AnimeResponseData } from '../data/survey-form-data';

const props = defineProps<{
  modelValue: AnimeResponseData;
  animeData: AnimeViewModel;
  isSurveyPreseason: boolean;
  isAnimeNew: boolean;
  validationErrors?: ValidationErrorData<AnimeResponseData>;
}>();

const emits = defineEmits<{
  (e: 'update:modelValue', value: AnimeResponseData): void;
}>();

const animeResponseData = computed<AnimeResponseData>({
  get() {
    return props.modelValue;
  },
  set(newValue) {
    emits('update:modelValue', newValue);
  },
});

const nullOption: SelectInputOption<null> = {
  id: 'null',
  displayName: '-----',
  value: null,
};

const scoreOptions: SelectInputOption<number | null>[] = [
  nullOption,
  {
    id: '5',
    displayName: '5/5 - Great',
    value: 5,
  },
  {
    id: '4',
    displayName: '4/5',
    value: 4,
  },
  {
    id: '3',
    displayName: '3/5 - Average',
    value: 3,
  },
  {
    id: '2',
    displayName: '2/5',
    value: 2,
  },
  {
    id: '1',
    displayName: '1/5 - Bad',
    value: 1,
  },
];

const expectationOptions: SelectInputOption<'S' | 'D' | null>[] = [
  nullOption,
  {
    id: 'S',
    displayName: 'Surprise',
    value: 'S',
  },
  {
    id: 'D',
    displayName: 'Disappointment',
    value: 'D',
  },
];

const isAnimeSeries = isAnimeSeriesFn(props.animeData);

const japaneseName = getAnimeName(props.animeData, AnimeNameType.JAPANESE_NAME);
const englishName = getAnimeName(props.animeData, AnimeNameType.ENGLISH_NAME);
const shortName = getAnimeName(props.animeData, AnimeNameType.SHORT_NAME);
</script>
