<template>
  <div v-if="japaneseName">
    {{ japaneseName.name }}
    <span v-if="showShortName && shortName" style="font-size: 60%">
      ({{ shortName.name }})
    </span>
  </div>
  <div v-if="englishName" style="font-size: 80%">
    {{ englishName.name }}
  </div>
</template>

<script lang="ts">
import { AnimeNameData, AnimeNameType } from '@/util/data';
import { Options, Vue } from 'vue-class-component';

@Options({
  props: {
    animeNames: {
      type: Array,
      default: () => [{}],
    },
    showShortName: {
      type: Boolean,
      default: () => true,
    },
  },
  data() {
    return {
      japaneseName: null,
      englishName: null,
      shortName: null,
    }
  },
  methods: {
    
  },
  mounted() {
    const animeNames = this.animeNames as AnimeNameData[];
    this.japaneseName = animeNames.find(animeName => animeName.type == AnimeNameType.JAPANESE_NAME && animeName.isOfficial) ?? animeNames.find(animeName => animeName.type == AnimeNameType.JAPANESE_NAME);
    this.englishName = animeNames.find(animeName => animeName.type == AnimeNameType.ENGLISH_NAME && animeName.isOfficial) ?? animeNames.find(animeName => animeName.type == AnimeNameType.ENGLISH_NAME);
    this.shortName = animeNames.find(animeName => animeName.type == AnimeNameType.SHORT_NAME && animeName.isOfficial) ?? animeNames.find(animeName => animeName.type == AnimeNameType.SHORT_NAME);
  }
})
export default class AnimeNames extends Vue {
  animeNames!: Array<AnimeNameData>;
  showShortName!: boolean;
}
</script>
