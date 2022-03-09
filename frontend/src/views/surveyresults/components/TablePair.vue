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

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import SimpleResultsTable from './SimpleResultsTable.vue';

@Options({
  components: {
    SimpleResultsTable,
  },
  props: {
    leftRanking: {
      type: Array, // { anime: AnimeData, result: number, extraResult: number }[]
      required: true,
    },
    rightRanking: Array,
    leftResultTypes: {
      type: Array,
      required: true,
    },
    rightResultTypes: Array,
    title: {
      type: String,
      required: true,
    },
    description: String,
    isAnimeSeries: Boolean, // Only used for the link under the tables
    top: {
      type: Number,
      required: true,
    },
    bottom: Number,
  },
})
export default class TablePair extends Vue {}
</script>