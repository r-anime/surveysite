from datetime import datetime
from django.core.management.base import BaseCommand, CommandParser
from survey.models import Anime, Response, Survey
import sys
from typing import Optional

class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('year', type=int)
        parser.add_argument('season', choices=['winter', 'spring', 'summer', 'fall'])
        parser.add_argument('pre_or_post', choices=['pre', 'post'])

    def handle(self, *args, **options) -> Optional[str]:
        year: int = options['year']
        season = self.__parse_season(options['season'])
        is_preseason: bool = options['pre_or_post'] == 'pre'

        try:
            survey: Survey = Survey.objects.get(year=year, season=season, is_preseason=is_preseason)
        except Survey.DoesNotExist:
            print('That survey does not exist', file=sys.stderr)
            return

        response_queryset = Response.objects.filter(survey=survey)
        timestamps: list[datetime] = list(response_queryset.values_list('timestamp', flat=True).order_by('timestamp'))

        # Formatted specifically for Google Sheets
        print(*[timestamp.strftime('%Y-%m-%d %H:%M:%S') for timestamp in timestamps], sep='\n')

    def __parse_season(self, season_str: str) -> Anime.AnimeSeason:
        if season_str == 'winter':
            return Anime.AnimeSeason.WINTER
        elif season_str == 'spring':
            return Anime.AnimeSeason.SPRING
        elif season_str == 'summer':
            return Anime.AnimeSeason.SUMMER
        else:
            return Anime.AnimeSeason.FALL
