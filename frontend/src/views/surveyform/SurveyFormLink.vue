<template>
  <h1 class="page-title">{{ surveyName }}!</h1>

  <h2>Your response was succesfully submitted!</h2>
  <div class="row row-cols-1">
    <p class="col">
      To edit your response in the future, save the link below.
    </p>
    <p class="col">
      Without this link, you will not be able to edit your response. Do not share it either, as others will then be able to edit your response.
    </p>
    <div class="col">
      <div class="row" id="response-display">
        <div class="col col-auto mt-1">
          <button class="btn btn-primary" @click="displayEditLink = !displayEditLink">
            <template v-if="displayEditLink">
              Hide link
            </template>
            <template v-else>
              Show link
            </template>
          </button>
        </div>
        <div class="col" v-if="displayEditLink">
          <router-link :to="editLink">
            {{ editLink }}
          </router-link>
        </div>
      </div>
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

// TODO: Rework this
@Options({})
export default class SurveyFormLink extends Vue {
  surveyName = '';
  editLink = '';
  displayEditLink = false;

  created() {
    this.surveyName = getSurveyNameFromRoute(this.$route);

    let responseId = this.$route.query.responseId;
    if (Array.isArray(responseId)) {
      responseId = responseId[0];
    }
    this.editLink = this.$router.resolve({ name: 'SurveyForm', query: { responseId } }).fullPath;
  }
}
</script>
