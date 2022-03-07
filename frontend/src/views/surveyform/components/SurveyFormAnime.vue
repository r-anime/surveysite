<template>
  <div class="card shadow-sm h-100">
    <div class="row">
      <!-- Card image -->
      <div class="col-lg-3 col-md-4 col-sm-3 col-4">
        <AnimeImages :animeImages="animeData.images" enableCarouselControls alignStart imgClass="rounded-start"/>
      </div>

      <!-- Card info -->
      <div class="col"><div class="card-body">
        <div class="card-title mb-3">
          <h5 class="mb-1">
            {{ japaneseName }}
            <span style="font-size:60%;" v-if="shortName">({{ shortName }})</span>
          </h5>
          <h6 style="color:#777777;" v-if="englishName">
            {{ englishName }}
          </h6>
        </div>

        <!-- Watching checkbox -->
        <div class="mb-3">
          <span class="mb-1">
            {{
              isSurveyPreseason ?
                isAnimeNew ?
                  'Will you watch this?' :
                  'Did you watch this and will you continue watching this?' :
                'Did you watch this?'
            }}
          </span>
          <br/>
          <input type="checkbox" class="btn-check" :id="`input-anime-${animeId}-watching`" autocomplete="off" v-model="animeResponseData.watching">
          <label class="btn w-100 mt-1" :class="animeResponseData.watching ? 'btn-outline-success' : 'btn-outline-secondary'" :for="`input-anime-${animeId}-watching`">
            {{ animeResponseData.watching ? 'Yes' : 'No' }}
          </label>
        </div>

        <!-- If post-season && series: Underwatched checkbox -->
        <div class="mb-3" v-if="!isSurveyPreseason && isAnimeSeries">
          <span class="mb-1">
            Did you find this underwatched?
          </span>
          <br/>
          <input type="checkbox" class="btn-check" :id="`input-anime-${animeId}-underwatched`" autocomplete="off" v-model="animeResponseData.underwatched">
          <label class="btn w-100 mt-1" :class="animeResponseData.underwatched ? 'btn-outline-success' : 'btn-outline-secondary'" :for="`input-anime-${animeId}-underwatched`">
            {{ animeResponseData.underwatched ? 'Yes' : 'No' }}
          </label>
        </div>

        <!-- Score input -->
        <div class="mb-3">
          <label class="form-label" :for="`input-anime-${animeId}-score`">
            {{
              isSurveyPreseason ?
                isAnimeNew ?
                  'How good do you expect this to be?' :
                  'How good do you expect the remainder to be?' :
                'What did you think of this?'
            }}
          </label>
          <select class="form-select" :id="`input-anime-${animeId}-score`" :class="{'is-invalid': validationErrors?.score}" autocomplete="off" v-model.number="animeResponseData.score" :aria-describedby="`input-anime-${animeId}-score-invalid`">
            <option :value="(null)">-----</option>
            <option value="5">5/5 - Great</option>
            <option value="4">4/5</option>
            <option value="3">3/5 - Average</option>
            <option value="2">2/5</option>
            <option value="1">1/5 - Bad</option>
          </select>
          <FormValidationErrors :id="`input-anime-${animeId}-score-invalid`" :validationErrors="validationErrors?.score"/>
        </div>

        <!-- If post-season && series: Expectations selectbox -->
        <div class="mb-3" v-if="!isSurveyPreseason && isAnimeSeries">
          <label class="form-label" :for="`input-anime-${animeId}-expectations`">Was this a surprise or disappointment?</label>
          <select class="form-select" :id="`input-anime-${animeId}-expectations`" :class="{'is-invalid': validationErrors?.expectations}" autocomplete="off" v-model="animeResponseData.expectations" :aria-describedby="`input-anime-${animeId}-expectations-invalid`">
            <option :value="(null)">-----</option>
            <option value="S">Surprise</option>
            <option value="D">Disappointment</option>
          </select>
          <FormValidationErrors :id="`input-anime-${animeId}-expectations-invalid`" :validationErrors="validationErrors?.expectations"/>
        </div>
      </div></div>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import AnimeImages from '@/components/AnimeImages.vue';
import { AnimeData, AnimeNameType } from '@/util/data';
import { getAnimeName, isAnimeSeries } from '@/util/helpers';
import FormValidationErrors from '@/components/FormValidationErrors.vue';

@Options({
  props: {
    animeData: Object,
    animeResponseData: Object,
    isSurveyPreseason: Boolean,
    isAnimeNew: Boolean,
    validationErrors: Object,
  },
  components: {
    AnimeImages,
    FormValidationErrors,
  },
})
export default class SurveyFormAnime extends Vue {
  animeData!: AnimeData;

  isAnimeSeries = false;
  animeId?: number;

  japaneseName: string | null = null;
  englishName: string | null = null;
  shortName: string | null = null;

  created(): void {
    this.isAnimeSeries = isAnimeSeries(this.animeData);
    this.animeId = this.animeData.id;

    this.japaneseName = getAnimeName(this.animeData, AnimeNameType.JAPANESE_NAME);
    this.englishName = getAnimeName(this.animeData, AnimeNameType.ENGLISH_NAME);
    this.shortName = getAnimeName(this.animeData, AnimeNameType.SHORT_NAME);
  }
}
</script>
