<template>

  <template v-if="animeImages.length === 1">
    <img :src="animeImages[0].urlSmall" :alt="animeImages[0].name" class="img-fluid">
  </template>

  <template v-else-if="animeImages.length > 1">
    <div :id="'animeImageCarousel'+id" class="carousel slide carousel-fade">
      <div class="carousel-inner d-flex align-items-center">
        <div v-for="(image, idx) in animeImages" :key="idx" class="carousel-item d-block" :class="idx==0 ? 'active' : ''">
          <img :src="image.urlSmall" :alt="image.name" class="d-block w-100">
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
    <img src="../assets/image-unavailable.png" alt="Image unavailable" class="img-fluid">
  </template>

</template>

<script lang="ts">
import { ImageData } from '@/util/data';
import { Options, Vue } from 'vue-class-component';
import { Carousel } from 'bootstrap';

@Options({
  props: {
    animeImages: {
      type: Array,
      default: () => [{}],
    },
    enableCarouselControls: {
      type: Boolean,
      default: () => true,
    }
  },
  data() {
    return {
      
    }
  },
  methods: {
    
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
  animeImages!: Array<ImageData>;
  enableCarouselControls!: boolean;

  // https://stackoverflow.com/a/61010067
  id = 0;
  private static componentId = 0;

  created(): void {
    this.id = AnimeImages.componentId;
    AnimeImages.componentId++;
  }
}
</script>
