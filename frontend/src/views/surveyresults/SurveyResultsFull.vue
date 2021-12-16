<template>
  <div>
    SurveyResultsFull test<br/>
    {{ surveyResultsData }}

    <router-link :to="{ name: 'SurveyResultsSummary' }">To results summary</router-link>
  </div>
</template>

<script lang="ts">
import { AnimeData, Gender, ResultsType, SurveyData } from "@/util/data";
import { ComputedRef } from "@vue/reactivity";
import { Options, Vue } from "vue-class-component";

// TODO: Move to own file
interface SurveyResultsData {
  results: Record<number, Record<ResultsType, number>>;
  anime: Record<number, AnimeData>;
  survey: SurveyData;
  miscellaneous: {
    responseCount: number;
    ageDistribution: Record<number, number>;
    genderDistribution: Record<Gender, number>;
  };
}

@Options({
  inject: [
    'surveyResultsDataRef',
  ],
})
export default class SurveyResultsFull extends Vue {
  surveyResultsDataRef!: ComputedRef<SurveyResultsData>;
  surveyResultsData?: SurveyResultsData;

  created(): void {
    this.surveyResultsData = this.surveyResultsDataRef.value;
  }
}
</script>