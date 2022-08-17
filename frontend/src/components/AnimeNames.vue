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

<script lang="ts">
import { type AnimeNameData, AnimeNameType } from '@/util/data';
import { Options, Vue } from 'vue-class-component';

@Options({
  props: {
    animeNames: {
      type: Array,
      required: true,
    },
    showShortName: Boolean,
  },
})
export default class AnimeNames extends Vue {
  animeNames!: AnimeNameData[];
  japaneseName?: AnimeNameData;
  englishName?: AnimeNameData;
  shortName?: AnimeNameData;
  
  created(): void {
    this.japaneseName = this.animeNames.find(animeName => animeName.type == AnimeNameType.JAPANESE_NAME && animeName.isOfficial)
      ?? this.animeNames.find(animeName => animeName.type == AnimeNameType.JAPANESE_NAME);
    this.englishName = this.animeNames.find(animeName => animeName.type == AnimeNameType.ENGLISH_NAME && animeName.isOfficial)
      ?? this.animeNames.find(animeName => animeName.type == AnimeNameType.ENGLISH_NAME);
    this.shortName = this.animeNames.find(animeName => animeName.type == AnimeNameType.SHORT_NAME && animeName.isOfficial)
      ?? this.animeNames.find(animeName => animeName.type == AnimeNameType.SHORT_NAME);
  }
}
</script>
