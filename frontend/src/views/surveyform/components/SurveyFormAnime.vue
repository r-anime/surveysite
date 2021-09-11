<template>
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
            {{ japaneseName }}
            <span style="font-size:60%;" v-if="shortName">({{ shortName }})</span>
          </h5>
          <h6 style="color:#777777;" v-if="englishName">
            {{ englishName }}
          </h6>
        </div>

        <!-- Watching checkbox -->
        <div class="mb-3">
          <input type="checkbox" class="btn-check" :id="`input-anime-${animeId}-watching`" autocomplete="off" v-model="animeResponseData.watching">
          <label class="btn btn-primary" :for="`input-anime-${animeId}-watching`">{{ animeResponseData.watching }}</label>
        </div>

        <!-- If post-season && series: Underwatched checkbox -->
        <div class="mb-3"> <!-- v-if="!data.survey.isPreseason" -->
          <input type="checkbox" class="btn-check" :id="`input-anime-${animeId}-underwatched`" autocomplete="off" v-model="animeResponseData.underwatched">
          <label class="btn btn-primary" :for="`input-anime-${animeId}-underwatched`">{{ animeResponseData.underwatched }}</label>
        </div>

        <!-- Score input -->
        <div class="mb-3">
          <label class="form-label" :for="`input-anime-${animeId}-score`">How good do you expect this to be? {{ animeResponseData.score }}-{{ typeof animeResponseData.score }}</label>
          <select class="form-select" :id="`input-anime-${animeId}-score`" v-model="animeResponseData.score">
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
          <label class="form-label" :for="`input-anime-${animeId}-expectations`">Was this a surprise or disappointment? {{ animeResponseData.expectations }}-{{ typeof animeResponseData.expectations }}</label>
          <select class="form-select" :id="`input-anime-${animeId}-expectations`" v-model="animeResponseData.expectations">
            <option :value="(null)">-----</option>
            <option value="S">Surprise</option>
            <option value="D">Disappointment</option>
          </select>
        </div>
      </div></div>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import AnimeImages from '@/components/AnimeImages.vue';
import { AnimeData, AnimeNameType } from '@/util/data';
import { getAnimeName } from '@/util/helpers';

@Options({
  props: {
    animeData: Object,
    animeResponseData: Object,
  },
  components: {
    AnimeImages,
  },
  data() {
    return {
      animeId: (this.animeData as AnimeData)?.id,
      japaneseName: null,
      englishName: null,
      shortName: null,
    };
  },
  mounted() {
    this.japaneseName = getAnimeName(this.animeData, AnimeNameType.JAPANESE_NAME);
    this.englishName = getAnimeName(this.animeData, AnimeNameType.ENGLISH_NAME);
    this.shortName = getAnimeName(this.animeData, AnimeNameType.SHORT_NAME);
  }
})
export default class SurveyFormAnime extends Vue {}
</script>
