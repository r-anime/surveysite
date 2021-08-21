<template>
  <div class="container-md">
    <div class="row row-cols-1">
      
      <!-- The lodash stuff returns a survey array like this: [[2020 surveys], [2019 surveys], ...] -->
      <div class="col" v-for="(surveysInYear, idx0) in _.orderBy(_.groupBy(surveys, 'year'), ['0.year'], ['desc'])" :key="idx0">

        <div class="row justify-content-center">
          <div class="col col-11 d-flex align-items-center">
            <h3 class="my-2 p-0">{{ surveysInYear[0].year }}</h3>
          </div>
        </div>
        
        <!-- The lodash stuff returns a survey array like this: [[2020 fall surveys], [2020 summer surveys], ...] -->
        <div class="row justify-content-center" v-for="(surveysInSeason, idx1) in _.orderBy(_.groupBy(surveysInYear, 'season'), ['0.season'], ['desc'])" :key="idx1">
          <div class="col col-2 col-sm-1 border rounded-start d-flex justify-content-center align-items-center text-center" :class="'bg-'+getSeasonName(surveysInSeason[0].season).toLowerCase()">
            <div class="row row-cols-1">
              <div class="col">
                <i class="bi" :class="getSeasonIconClass(surveysInSeason[0].season)"></i>
              </div>
              <div class="col text-season fw-bold">
                <span>{{ getSeasonName(surveysInSeason[0].season) }}</span>
              </div>
            </div>
          </div>
          <div class="col col-9 col-sm-10">
            <div class="row h-100">

              <div v-if="_.find(surveysInSeason, { isPreseason: false })" class="col col-lg-6 col-12 border p-3 d-lg-block">
                <Survey :survey="_.find(surveysInSeason, { isPreseason: false })"/>
              </div>
              <div v-else class="col col-lg-6 col-12 border p-3 d-lg-block bg-unavailable"></div>

              <div v-if="_.find(surveysInSeason, { isPreseason: true })" class="col col-lg-6 col-12 border p-3 d-lg-block">
                <Survey :survey="_.find(surveysInSeason, { isPreseason: true })"/>
              </div>
              <div v-else class="col col-lg-6 col-12 border p-3 d-lg-block bg-unavailable"></div>

            </div>
          </div>
          
        </div>

      </div>
    </div>
  </div>
</template>


<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import Survey from '@/components/Survey.vue';
import Ajax from '@/util/ajax';
import { AnimeSeason, SurveyData } from '@/util/data';
import _ from 'lodash';


@Options({
  components: {
    Survey,
  },
  data() {
    return {
      surveys: [],
      _: _
    }
  },
  methods: {
    getSeasonName(season: string): string {
      const seasonNumber = Number(season);
      const seasonNameUpper = AnimeSeason[seasonNumber];
      return seasonNameUpper.charAt(0) + seasonNameUpper.slice(1).toLowerCase()
    },
    getSeasonIconClass(season: string): string {
      const seasonNumber = Number(season);
      switch (seasonNumber) {
        case AnimeSeason.WINTER:
          return 'bi-snow';
        case AnimeSeason.SPRING:
          return 'bi-flower2';
        case AnimeSeason.SUMMER:
          return 'bi-sun';
        case AnimeSeason.FALL:
          return 'bi-tree';
        default:
          return '';
      }
    },
  },
  async mounted() {
    this.surveys = await Ajax.get<SurveyData[]>('api/index/');
  }
})
export default class Index extends Vue {}
</script>


<style lang="scss" scoped>
.bi {
    font-size: 2rem;
}

.bg-winter {
    background-color: rgb(123, 171, 193);
}
.bg-spring {
    background-color: rgb(168, 215, 44);
}
.bg-summer {
    background-color: rgb(223, 129, 60);
}
.bg-fall {
    background-color: rgb(253, 215, 10);
}
.bg-unavailable {
    background-color: rgb(227, 227, 227)!important;
}

.text-season {
    hyphens: auto;
    font-size: 90%;
}
</style>
