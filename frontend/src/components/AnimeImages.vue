<template>

  <template v-if="animeImages.length === 1">
    <img :src="animeImages[0].urlSmall" :alt="animeImages[0].name" class="img-fluid" :class="imgClass">
  </template>

  <template v-else-if="animeImages.length > 1">
    <div :id="'animeImageCarousel'+id" class="carousel slide carousel-fade">
      <div class="carousel-inner d-flex" :class="alignCenter ? 'align-items-center' : ''">
        <div v-for="(image, idx) in animeImages" :key="idx" class="carousel-item" :class="(idx==0 ? 'active' : '') + (alignCenter ? ' d-block' : '')">
          <img :src="image.urlSmall" :alt="image.name" class="w-100" :class="imgClass">
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
    <img src="../assets/image-unavailable.png" alt="Image unavailable" class="img-fluid" :class="imgClass">
  </template>

</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import { Carousel } from 'bootstrap';

@Options({
  props: {
    animeImages: {
      type: Array,
      default: [],
    },
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
  },
  mounted() {
    if (this.animeImages.length > 1) {
      this.$nextTick(() => {
        new Carousel(`#animeImageCarousel${this.id}`);
      });
    }
  }
})
export default class AnimeImages extends Vue {
  id = 0;
  private static componentId = 0;

  created(): void {
    this.id = AnimeImages.componentId;
    AnimeImages.componentId++;
  }
}
</script>
