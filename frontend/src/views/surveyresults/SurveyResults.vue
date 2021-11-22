<template v-if="pageTitle">
  <h1 class="mb-4 mx-n2 p-3 shadow bg-primary bg-opacity-75 text-light">{{ pageTitle }}</h1>
  <div class="row">
    <div class="col-md-8">
      <div class="row"><div class="col">
        <p>
          Thanks everyone for filling in this survey! There were [[ TODO: Response count ]] responses,
          and the average age of everyone who answered was [[ TODO: Average age ]].
        </p>
        <p>
          Anime with a popularity of less than 2% will not be displayed here, as their data may be inaccurate.
        </p>
      </div></div>
      <div class="row mt-2"><div class="col">
        <canvas id="age-distribution-chart"></canvas>
      </div></div>
    </div>
    <div class="col-md-4">
      <canvas id="gender-distribution-chart"></canvas>
    </div>
  </div>
  
  {{ $route.path }}
  <br/>
  {{ surveyResultsData }}
</template>

<script lang="ts">
import Ajax, { Response } from "@/util/ajax";
import { AnimeData, Gender, ResultsType, SurveyData } from "@/util/data";
import { getSurveyApiUrl, getSurveyName } from "@/util/helpers";
import NotificationService from "@/util/notification-service";
import { Vue, Options } from "vue-class-component";

interface SurveyResultsData {
  results: Record<number, Record<ResultsType, number>>;
  anime: Record<number, AnimeData>;
  survey: SurveyData;
  miscellaneous: {
    responseCount: number;
    ageDistribution: Record<number, number>;
    genderDistribution: Record<Gender, number>;
  }
}

@Options({})
export default class SurveyResults extends Vue {
  private pageTitle?: string;
  private surveyResultsData?: SurveyResultsData;

  // eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
  data() {
    return {
      pageTitle: this.pageTitle,
      surveyResultsData: this.surveyResultsData,
    }
  }

  async mounted(): Promise<void> {
    const response = await Ajax.get<SurveyResultsData>(getSurveyApiUrl(this.$route) + 'results/');
    console.log(response);
    if (Response.isErrorData(response.data)) {
      NotificationService.pushMsgList(response.getGlobalErrors(), 'danger');

      this.$router.push({name: 'Index'});
      return;
    }

    this.surveyResultsData = response.data;
    this.pageTitle = getSurveyName(this.surveyResultsData.survey) + ' Results!';
  }
}
</script>