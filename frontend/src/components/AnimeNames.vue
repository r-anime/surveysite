<template>
  <div>
    <div v-if="japaneseName">
      {{ japaneseName.name }}
      <span v-if="showShortName && shortName" style="font-size: 60%">
        ({{ shortName.name }})
      </span>
    </div>
    <div v-if="englishName" style="font-size: 80%">
      {{ englishName.name }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { type AnimeNameData, AnimeNameType } from '@/util/data';

const props = defineProps<{
  animeNames: AnimeNameData[];
  showShortName?: boolean;
}>();

const japaneseName = tryGetNameOfType(AnimeNameType.JAPANESE_NAME);
const englishName = tryGetNameOfType(AnimeNameType.ENGLISH_NAME);
const shortName = tryGetNameOfType(AnimeNameType.SHORT_NAME);

function tryGetNameOfType(animeNameType: AnimeNameType): AnimeNameData | undefined {
  return props.animeNames.find(animeName => animeName.type == animeNameType && animeName.isOfficial)
    ?? props.animeNames.find(animeName => animeName.type == animeNameType);
}
</script>
