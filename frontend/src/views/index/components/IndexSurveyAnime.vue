<template>
  <div class="row align-items-center text-smaller-2">
    <div class="col-lg-4 col-sm-2 col-3">
      <AnimeImages :animeImages="animeResults.anime.images" maxHeight="5rem"/>
    </div>
    <div class="col ps-0" v-if="animeResults.anime.names">
      <AnimeNames :animeNames="animeResults.anime.names"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import AnimeNames from '@/components/AnimeNames.vue';
import AnimeImages from '@/components/AnimeImages.vue';

defineProps({
  animeResults: {
    type: Object,
    required: true,
  },
});
</script>
