<template>
  <div class="row">
    <div class="col col-4">
      {{ resultTypes }}
    </div>
    <div class="col">
      <SimpleResultsTable :ranking="ranking" :resultTypes="resultTypes" :top="10"/>
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
    ranking: Array, // { anime: AnimeData, result: number, extraResult: number }[]
    resultTypes: Array,
  },
})
export default class TableWithTop3 extends Vue {

}
</script>