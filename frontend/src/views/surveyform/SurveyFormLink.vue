<template>
  <h1 class="page-title">{{ surveyName }}!</h1>

  <h3 class="mb-4 p-2 rounded shadow row justify-content-between align-items-center bg-primary bg-opacity-75 text-light">
    Your response was succesfully submitted!
  </h3>
  <div class="row row-cols-1">
    <p class="col">
      To edit your response in the future, save the link below. Without this link, you will not be able to edit your response. Do not share it either, as others could then also edit your response.
    </p>
    <div class="col">
      <router-link :to="editLink">
        <!-- Straight up show the link instead of hiding it behind a toggle for now, as the response id is in the user's navbar anyway -->
        {{ editLink }}
      </router-link>
    </div>
  </div>
  
  <div class="row mt-4 justify-content-between">
    <div class="col">
      <router-link :to="{ name: 'Index' }" class="btn btn-secondary">Back to index</router-link>
    </div>
    <div class="col"></div>
  </div>
</template>

<script lang="ts">
import { getSurveyNameFromRoute } from "@/util/helpers";
import { Options, Vue } from "vue-class-component";

// TODO: Replace this with maybe a modal? in the future
@Options({})
export default class SurveyFormLink extends Vue {
  surveyName = '';
  editLink = '';

  created() {
    this.surveyName = getSurveyNameFromRoute(this.$route);

    let responseId = this.$route.query.responseId;
    if (Array.isArray(responseId)) {
      responseId = responseId[0];
    }
    if (responseId == null) {
      this.$router.push({ name: 'Index', replace: true });
    }
    this.editLink = this.$router.resolve({ name: 'SurveyForm', query: { responseId } }).fullPath;
  }
}
</script>
