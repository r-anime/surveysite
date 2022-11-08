<template>
  <div class="row">
    <h5 class="col-12 subsection-title mb-1">{{ title }}</h5>
    <p class="col-12 text-center" v-if="description">{{ description }}</p>
    <div class="col-6 mt-3 pe-4">
      <SimpleResultsTable :ranking="leftRanking" :resultTypes="leftResultTypes" :isAnimeSeries="isAnimeSeries" :top="top" :bottom="bottom"/>
    </div>
    <div class="col-6 mt-3 ps-4"> <!-- reverse() modifies an array in-place too, so we use slice() to create a copy first -->
      <SimpleResultsTable :ranking="rightRanking ?? leftRanking.slice().reverse()" :resultTypes="rightResultTypes ?? leftResultTypes" :isAnimeSeries="isAnimeSeries" :top="top" :bottom="bottom"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AnimeViewModel, ResultType } from '@/util/data';
import SimpleResultsTable from './SimpleResultsTable.vue';

defineProps<{
  leftRanking: { anime: AnimeViewModel, result: number, extraResult?: number }[];
  rightRanking?: { anime: AnimeViewModel, result: number, extraResult?: number }[];
  leftResultTypes: ResultType[];
  rightResultTypes?: ResultType[];

  title: string;
  description?: string;
  isAnimeSeries?: boolean; // Only used for the link under the tables

  top: number;
  bottom?: number;
}>();
</script>