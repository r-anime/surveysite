from django.core.cache import cache
from django.views.generic import TemplateView
from survey.views.results import ResultsGenerator, ResultsType
from survey.models import Survey
from survey.util import SurveyUtil, get_user_info

class IndexView(TemplateView):
    """View containing a list of all current and past surveys."""
    template_name = 'survey/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey_queryset = Survey.objects.order_by('-year', '-season', 'is_preseason')

        for survey in survey_queryset:
            if survey.is_ongoing:
                score_ranking = []
            else:
                def get_score_ranking():
                    anime_series_results, _ = ResultsGenerator(survey).get_anime_results_data()
                    return sorted(
                        [(anime, anime_data[ResultsType.SCORE]) for anime, anime_data in anime_series_results.items()],
                        key=lambda item: item[1] if item[1] == item[1] else -1,
                        reverse=True,
                    )

                if SurveyUtil.is_survey_old(survey):
                    score_ranking = cache.get_or_set('survey_score_ranking_%i' % survey.id, get_score_ranking, version=1, timeout=SurveyUtil.get_old_survey_cache_timeout())
                else:
                    score_ranking = get_score_ranking()

            survey.score_ranking = score_ranking[:3]

        context['survey_list'] = survey_queryset
        context['user_info'] = get_user_info(self.request.user)
        return context
