<template>
  <div class="row justify-content-center">
    <h5 class="col-12 subsection-title mb-1">{{ title }}</h5>
    <p class="col-12 text-center" v-if="description">{{ description }}</p>
    <div class="col-md-4 col-8 text-center">
      <div v-if="ranking.length > 0" class="row justify-content-center mb-4">
        <div class="col-8 mb-2">
          <AnimeImages :animeImages="ranking[0].anime.images" enableCarouselControls/>
        </div>
        <div class="col-12">
          <AnimeNames :animeNames="ranking[0].anime.names" showShortName/>
        </div>
      </div>
      <div v-if="ranking.length > 1" class="row justify-content-center text-smaller">
        <div :class="{'col-6': ranking.length > 2, 'col': ranking.length === 2}">
          <div class="row justify-content-center">
            <div class="col-11 mb-1">
              <AnimeImages :animeImages="ranking[1].anime.images" enableCarouselControls/>
            </div>
            <div class="col-12">
              <AnimeNames :animeNames="ranking[1].anime.names" showShortName/>
            </div>
          </div>
        </div>
        <div v-if="ranking.length > 2" class="col-6">
          <div class="row justify-content-center">
            <div class="col-11 mb-1">
              <AnimeImages :animeImages="ranking[2].anime.images" enableCarouselControls/>
            </div>
            <div class="col-12">
              <AnimeNames :animeNames="ranking[2].anime.names" showShortName/>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="col-md col-12">
      <SimpleResultsTable :ranking="ranking" :resultTypes="resultTypes" :isAnimeSeries="isAnimeSeries" :top="top" :bottom="bottom"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import SimpleResultsTable from './SimpleResultsTable.vue';
import AnimeImages from '@/components/AnimeImages.vue';
import AnimeNames from '@/components/AnimeNames.vue';
import type { AnimeViewModel, ResultType } from '@/util/data';

defineProps<{
  ranking: { anime: AnimeViewModel, result: number, extraResult?: number }[];
  resultTypes: ResultType[];
  isAnimeSeries?: boolean;
  top: number;
  bottom?: number;
  title: string;
  description?: string;
}>();
</script>