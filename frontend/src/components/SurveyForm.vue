<template>
  <div>abc</div>
</template>

<script lang="ts">
import { SurveyData } from '@/util/data';
import { getSurveyName } from '@/util/helpers';
import { Options, Vue } from 'vue-class-component';

@Options({
  props: {
    survey: Object
  },
  data() {
    return {
      surveyName: getSurveyName(this.survey as SurveyData),
    }
  },
  methods: {
  }
})
export default class SurveyForm extends Vue {
  survey!: SurveyData;
}
</script>
