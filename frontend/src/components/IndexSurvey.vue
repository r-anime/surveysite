<template>
  <div class="row">
    <div class="col col-12 mb-1">
      <h5>
        {{ getSurveyName() }}
        <small class="text-muted" style="font-size: 80%;">Finished</small>
      </h5>
    </div>
    {{ survey.openingTime.toDateString() }}
    <!-- {% for resulttype, resulttype_results in data.items %}
        <div class="col col-6 col-lg-12{% if not forloop.last %} mb-lg-3{% endif %}">
            <div class="row mb-1">
                <div class="col">
                    <span>
                        {% if resulttype.value|lower == 'popularity' %}
                            Most popular series
                        {% elif resulttype.value|lower == 'score' %}
                            {% if survey.is_preseason %}
                                Most anticipated series
                            {% else %}
                                Most highly regarded series
                            {% endif %}
                        {% endif %}
                    </span>
                </div>
            </div>
            <div class="row px-1 align-items-center" style="font-size:70%;">
                {% for anime_value_pair in resulttype_results %}
                    <div class="col px-1{% if not forloop.first %} d-lg-flex d-none{% endif %}">
                        {% if anime_value_pair %}
                            {% include 'survey/index_ranking_row.html' with anime=anime_value_pair.anime value=anime_value_pair.value only %}
                        {% endif %}
                    </div>
                {% endfor %}
            </div>
        </div>
    {% endfor %} -->
  </div>
</template>

<script lang="ts">
import { SurveyData } from '@/util/data';
import { getSeasonName } from '@/util/helpers';
import { Options, Vue } from 'vue-class-component';

@Options({
  props: {
    survey: {} as SurveyData
  },
  data() {
    return {

    }
  },
  methods: {
    getSurveyName() {
      const survey = this.survey as SurveyData;
      return `The ${survey.isPreseason ? 'Start' : 'End'} of ${getSeasonName(survey.season)} ${survey.year} Survey`;
    }
  }
})
export default class IndexSurvey extends Vue {
  survey!: SurveyData;
}
</script>
