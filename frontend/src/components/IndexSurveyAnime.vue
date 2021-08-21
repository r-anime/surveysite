<template>
  <div class="row align-items-center">
    <div class="col col-3 col-lg-4">
      <AnimeImages :animeImages="surveyAnime.anime.images" :enableCarouselControls="false"/>
    </div>
    <div class="col ps-0" v-if="surveyAnime.anime.names">
      <AnimeNames :animeNames="surveyAnime.anime.names" :showShortName="false"/>
    </div>
  </div>
</template>

<script lang="ts">
import { SurveyAnimeData } from '@/util/data';
import AnimeNames from '@/components/AnimeNames.vue';
import AnimeImages from '@/components/AnimeImages.vue';
import { Options, Vue } from 'vue-class-component';

@Options({
  components: {
    AnimeNames,
    AnimeImages,
  },
  props: {
    surveyAnime: {
      type: Object,
    }
  },
  data() {
    return {

    }
  },
  methods: {
    
  }
})
export default class IndexSurveyAnime extends Vue {
  surveyAnime!: SurveyAnimeData;
}
</script>
