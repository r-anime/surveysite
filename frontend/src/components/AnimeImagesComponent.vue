<template>

  <template v-if="animeImages.length === 1">
    <img :src="animeImages[0].urlSmall" :alt="animeImages[0].name" :class="imgClassInternal" :style="maxHeight ? { maxHeight: maxHeight } : {}">
  </template>

  <template v-else-if="animeImages.length > 1">
    <div :id="carouselId" class="carousel slide carousel-fade">
      <div class="carousel-inner d-flex" :class="{ 'align-items-center': !alignStart }">
        <!-- d-block for the carousel item so that if images have different size, the carousel's size will consistently stay as large as needed -->
        <div v-for="(image, idx) in animeImages" :key="idx" class="carousel-item d-block" :class="{ 'active' : idx==0 }">
          <img :src="image.urlSmall" :alt="image.name" :class="imgClassInternal" :style="maxHeight ? { maxHeight: maxHeight } : {}">
        </div>
      </div>
      <button v-if="enableCarouselControls" class="carousel-control-prev" type="button" :data-bs-target="'#'+carouselId" data-bs-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Previous</span>
      </button>
      <button v-if="enableCarouselControls" class="carousel-control-next" type="button" :data-bs-target="'#'+carouselId" data-bs-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Next</span>
      </button>
    </div>
  </template>

  <template v-else>
    <img src="../assets/image-unavailable.png" alt="Image unavailable" class="img-fluid" :class="imgClassInternal" :style="maxHeight ? { maxHeight: maxHeight } : {}">
  </template>

</template>

<script setup lang="ts">
import { Carousel } from 'bootstrap';
import type { ImageViewModel } from '@/util/data';
import { nextTick, onMounted } from 'vue';
import IdGenerator from '@/util/id-generator';

const props = defineProps<{
  animeImages: ImageViewModel[],
  enableCarouselControls?: boolean,
  alignStart?: boolean,
  imgClass?: string,
  maxHeight?: string,
}>();

const carouselId = IdGenerator.generateUniqueId('animeImageCarousel');

const imgClassInternal = ['img-fluid', 'd-block'];
if (!props.alignStart) {
  imgClassInternal.push('mx-auto');
}
if (props.imgClass) {
  imgClassInternal.push(props.imgClass);
}

onMounted(() => {
  if (props.animeImages.length > 1) {
    nextTick(() => {
      new Carousel(`#${carouselId}`);
    });
  }
});
</script>
