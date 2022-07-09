from datetime import datetime
from django.core.management.base import BaseCommand, CommandParser
import itertools
import math
from survey.models import Anime, Response, Survey
from typing import Optional


class Command(BaseCommand):
    help = 'Exports survey stuff from the database'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('mode', choices=['timeline'])
        parser.add_argument('--year', required=True, type=int)
        parser.add_argument('--season', required=True, choices=[choice[1].lower() for choice in Anime.AnimeSeason.choices])

    def handle(self, *args, **options) -> Optional[str]:
        mode: str = options['mode']
        if mode == 'histogram':
            self.__export_histogram(*args, **options)

    def __export_histogram(self, *args, **options):
        year: int = options['year']
        season = Anime.AnimeSeason[str(options['season']).upper()]

        survey = Survey.objects.filter(year=year, season=season).first()
        if survey is None:
            print('No survey found for {} {}'.format(year, season.label))
            return

        print(survey)

        response_timestamps: list[datetime] = list(Response.objects.filter(survey=survey).order_by('timestamp').values_list('timestamp', flat=True))

        response_count = len(response_timestamps)
        survey_length = response_timestamps[-1] - response_timestamps[0]
        survey_length_hours = math.ceil(survey_length.total_seconds() / 60 / 60)

        start_time = response_timestamps[0]
        print('responses: {}\nlength: {}\nhour count: {}\nstart time: {}'.format(response_count, survey_length, survey_length_hours, start_time))

        def get_hour_bin(timestamp: datetime):
            return math.ceil((timestamp - start_time).total_seconds() / 60 / 60)

        histogram_data = {hour: len(list(timestamps_in_hour)) for [hour, timestamps_in_hour] in itertools.groupby(response_timestamps, key=get_hour_bin)}
        print(histogram_data)
        for hour in range(survey_length_hours):
            count = histogram_data.get(hour, 0)
            if count > 0:
                print('hour: {:2d}\tcount: {:3d}'.format(hour, count))
