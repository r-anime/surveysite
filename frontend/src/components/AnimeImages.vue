<template>

  <template v-if="animeImages.length === 1">
    <img :src="animeImages[0].urlSmall" :alt="animeImages[0].name" :class="imgClassInternal" :style="maxHeight ? { maxHeight: maxHeight } : {}">
  </template>

  <template v-else-if="animeImages.length > 1">
    <div :id="'animeImageCarousel'+id" class="carousel slide carousel-fade">
      <div class="carousel-inner d-flex" :class="{ 'align-items-center': alignCenter }">
        <!-- d-block for the carousel item so that if images have different size, the carousel's size will consistently stay as large as needed -->
        <div v-for="(image, idx) in animeImages" :key="idx" class="carousel-item d-block" :class="{ 'active' : idx==0 }">
          <img :src="image.urlSmall" :alt="image.name" :class="imgClassInternal" :style="maxHeight ? { maxHeight: maxHeight } : {}">
        </div>
      </div>
      <button v-if="enableCarouselControls" class="carousel-control-prev" type="button" :data-bs-target="'#animeImageCarousel'+id" data-bs-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Previous</span>
      </button>
      <button v-if="enableCarouselControls" class="carousel-control-next" type="button" :data-bs-target="'#animeImageCarousel'+id" data-bs-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Next</span>
      </button>
    </div>
  </template>

  <template v-else>
    <img src="../assets/image-unavailable.png" alt="Image unavailable" class="img-fluid" :class="imgClassInternal">
  </template>

</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import { Carousel } from 'bootstrap';
import { ImageData } from '@/util/data';

type CssClass = string | Record<string, boolean>;

@Options({
  props: {
    animeImages: Array,
    enableCarouselControls: {
      type: Boolean,
      default: true,
    },
    alignCenter: {
      type: Boolean,
      default: true,
    },
    imgClass: {
      type: String,
      default: '',
    },
    maxHeight: {
      type: String,
      default: '',
    },
  },
})
export default class AnimeImages extends Vue {
  animeImages!: ImageData[];
  imgClass!: CssClass;
  alignCenter!: boolean;

  imgClassInternal: CssClass[] = [];
  id = 0;

  private static componentId = 0;

  created(): void {
    this.id = AnimeImages.componentId;
    AnimeImages.componentId++;

    this.imgClassInternal = ['img-fluid', 'd-block', { 'mx-auto': this.alignCenter }, this.imgClass];
  }

  mounted(): void {
    if (this.animeImages.length > 1) {
      this.$nextTick(() => {
        new Carousel(`#animeImageCarousel${this.id}`);
      });
    }
  }
}
</script>
