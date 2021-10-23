<template>
  {{ $route.path }}
  <br/>
  {{ surveyData }}
</template>

<script lang="ts">
import Ajax from "@/util/ajax";
import { getSurveyApiUrl } from "@/util/helpers";
import { Vue, Options } from "vue-class-component";

@Options({
  data() {
    return {
      surveyData: {},
    };
  },
  async mounted() {
    this.surveyData = await Ajax.get(getSurveyApiUrl(this.$route) + 'results/');
  },
})
export default class SurveyResults extends Vue {}
</script>