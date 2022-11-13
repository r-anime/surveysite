from collections import OrderedDict
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.views.generic import View
from http import HTTPStatus
from survey.models import Response, Survey
from survey.util.data import AnimeViewModel, SurveyViewModel, json_encoder_factory
from survey.util.http import HttpEmptyErrorResponse, JsonErrorResponse
from survey.util.results import ResultsGenerator
from survey.util.survey import get_survey_anime, try_get_survey

class SurveyResultsApi(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        survey = try_get_survey(
            year=self.kwargs['year'],
            season=self.kwargs['season'],
            pre_or_post=self.kwargs['pre_or_post'],
        )
        if survey is None:
            return HttpEmptyErrorResponse(HTTPStatus.NOT_FOUND)

        if not request.user.is_staff:
            if survey.state == Survey.State.UPCOMING:
                return JsonErrorResponse('This survey is not open yet!', HTTPStatus.FORBIDDEN)
            elif survey.state == Survey.State.ONGOING:
                return JsonErrorResponse('This survey is still ongoing!', HTTPStatus.FORBIDDEN)

        # TODO: Optimize, this (and age/gender distr. stuff) prob do multiple DB lookups
        survey_results = ResultsGenerator(survey).get_anime_results_data()
        survey_responses = Response.objects.filter(survey=survey)

        survey_anime_queryset, _, _ = get_survey_anime(survey)
        survey_anime_data_list = {anime.id: AnimeViewModel.from_model(anime) for anime in survey_anime_queryset}
        survey_data = SurveyViewModel.from_model(survey)

        json_encoder = json_encoder_factory()
        return JsonResponse({
            'results': survey_results,
            'anime': survey_anime_data_list,
            'survey': survey_data,
            'miscellaneous': {
                'response_count': survey_responses.count(),
                'gender_distribution': self.__get_gender_distribution(survey_responses),
                'age_distribution': self.__get_age_distribution(survey_responses),
            },
        }, encoder=json_encoder, safe=False)

    def __get_gender_distribution(self, survey_responses: QuerySet[Response]):
        gender_answers_queryset = survey_responses.filter(~Q(gender=''), gender__isnull=False)
        gender_answers_count = len(gender_answers_queryset)
        gender_distribution = OrderedDict([
            (Response.Gender.MALE,   gender_answers_queryset.filter(gender=Response.Gender.MALE  ).count() / max(gender_answers_count, 1) * 100),
            (Response.Gender.FEMALE, gender_answers_queryset.filter(gender=Response.Gender.FEMALE).count() / max(gender_answers_count, 1) * 100),
            (Response.Gender.OTHER,  gender_answers_queryset.filter(gender=Response.Gender.OTHER ).count() / max(gender_answers_count, 1) * 100),
        ])

        return gender_distribution

    def __get_age_distribution(self, survey_responses: QuerySet[Response]):
        age_distribution = [0.0]*81
        age_list = survey_responses.filter(age__isnull=False, age__gt=0).values_list('age', flat=True)
        age_count = len(age_list)

        # Count for each age how many people are that old.
        for age in age_list:
            if age > 0 and age <= 80:
                age_distribution[int(age)] += 1

        # Normalize the values to 0-100.
        for i in range(len(age_distribution)):
            age_distribution[i] /= max(age_count, 1) / 100.0

        # Convert the list to a dict.
        age_distribution = OrderedDict([
            (idx, age_distribution[idx]) for idx in range(5, 81)
        ])

        return age_distribution
