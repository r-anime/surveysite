<template>
  <div class="row">
    <h5 class="col-12 subsection-title mb-1">{{ title }}</h5>
    <p class="col-12 text-center" v-if="description">{{ description }}</p>
    <div class="col-6 mt-3 pe-4">
      <SimpleResultsTable :ranking="leftRanking" :resultTypes="leftResultTypes" :top="top"/>
    </div>
    <div class="col-6 mt-3 ps-4"> <!-- reverse() modifies an array in-place too, so we use slice() to create a copy first -->
      <SimpleResultsTable :ranking="rightRanking ?? leftRanking.slice().reverse()" :resultTypes="rightResultTypes ?? leftResultTypes" :top="top"/>
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
    leftRanking: Array, // { anime: AnimeData, result: number, extraResult: number }[]
    rightRanking: Array, // Optional
    leftResultTypes: Array,
    rightResultTypes: Array, // Optional
    title: String,
    description: String, // Optional
    top: Number,
  },
})
export default class TablePair extends Vue {}
</script>