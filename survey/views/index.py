from django.core.cache import cache
from django.views.generic import TemplateView
from survey.views.results import ResultsGenerator, ResultsType
from survey.models import Anime, Survey, Image
from survey.util import SurveyUtil
from .mixins import UserMixin

class IndexView(UserMixin, TemplateView):
    """View containing a list of all current and past surveys."""
    template_name = 'survey/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey_queryset = Survey.objects.order_by('-year', '-season', 'is_preseason')

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

            if survey.state != Survey.State.FINISHED:
                anime_queryset, _, _ = SurveyUtil.get_survey_anime(survey)
                items[year][season][pre_or_post]['data'] = Image.objects.filter(anime__in=anime_queryset).order_by('?')[:12]
            else:
                survey_results = {}
                items[year][season][pre_or_post]['data'] = survey_results

                anime_series_results, _ = ResultsGenerator(survey).get_anime_results_data()
                resulttype_list = [ResultsType.POPULARITY, ResultsType.SCORE]
                for resulttype in resulttype_list:
                    sorted_results = sorted(anime_series_results.items(), key=lambda value: value[1][resulttype], reverse=True)
                    survey_results[resulttype] = [{'anime': anime, 'value': results[resulttype]} for anime, results in sorted_results[:2] if results[ResultsType.POPULARITY] > 2.0]
                    survey_results[resulttype].extend([None] * (2 - len(survey_results[resulttype])))
        
        context['items'] = items
        return context
