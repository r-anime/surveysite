<template>
  <div class="row">
    <div class="col col-4">
      {{ resultName }}
    </div>
    <div class="col">
      <SimpleResultsTable :ranking="ranking" :resultName="resultName" :top="10"/>
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
    ranking: Object, // { anime: AnimeData, result: number }[]
    resultName: String,
  },
})
export default class TableWithTop3 extends Vue {

}
</script>