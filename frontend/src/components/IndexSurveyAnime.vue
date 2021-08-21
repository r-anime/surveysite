<template>
  <div class="row align-items-center no-gutters">
    <div class="col col-3 col-lg-4 px-2 py-1">
      {% render_anime_images anime variant='s' enable_controls=False %}
    </div>
    <div class="col">
      {% get_official_names anime 'div class="mb-1"'%}
    </div>
  </div>
</template>

<script lang="ts">
import { SurveyAnimeData } from '@/util/data';
import { Options, Vue } from 'vue-class-component';

@Options({
  props: {
    surveyAnime: {} as SurveyAnimeData
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
