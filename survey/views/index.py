from django.core.cache import cache
from django.views.generic import TemplateView
from survey.views.results import ResultsGenerator, ResultsType
from survey.models import Anime, Survey
from survey.util import SurveyUtil, get_user_info

class IndexView(TemplateView):
    """View containing a list of all current and past surveys."""
    template_name = 'survey/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey_queryset = Survey.objects.order_by('-year', '-season', 'is_preseason')

        first_year = survey_queryset.last().year
        last_year = survey_queryset.first().year

        items = {}
        for survey in survey_queryset:
            year = survey.year
            season = Anime.AnimeSeason(survey.season)
            pre_or_post = 'pre' if survey.is_preseason else 'post'
            if year not in items:
                items[year] = {}
            if season not in items[year]:
                items[year][season] = {}
            if pre_or_post not in items[year][season]:
                items[year][season][pre_or_post] = {}
            items[year][season][pre_or_post]['survey'] = survey

            if survey.is_ongoing:
                items[year][season][pre_or_post]['data'] = SurveyUtil.get_survey_anime(survey)[0][0:12]
            else:
                survey_results = {}
                items[year][season][pre_or_post]['data'] = survey_results

                anime_series_results, _ = ResultsGenerator(survey).get_anime_results_data()
                resulttype_list = [ResultsType.POPULARITY, ResultsType.SCORE]
                for resulttype in resulttype_list:
                    sorted_results = sorted(anime_series_results.items(), key=lambda value: value[1][resulttype], reverse=True)
                    survey_results[resulttype] = [{'anime': anime, 'value': results[resulttype]} for anime, results in sorted_results[:2]]
        
        context['items'] = items
        context['user_info'] = get_user_info(self.request.user)
        return context

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
