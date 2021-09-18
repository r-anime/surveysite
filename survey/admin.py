from django.contrib import admin, messages
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db.models import Q, Count
from django.db.models.functions import Concat
from django.forms.models import BaseInlineFormSet
from django.utils import timezone
from datetime import datetime

from .models import Anime, AnimeName, Video, Image, Survey, Response, AnimeResponse, SurveyAdditionRemoval, MissingAnime
from .util import AnimeUtil
from io import StringIO, BytesIO
import uuid
import PIL


class YearSeasonListFilter(admin.SimpleListFilter):
    title = 'year/season'
    parameter_name = 'yearseason'
    year_season_list = [(year, season) for year in range(2015, datetime.now().year + 2) for season in Anime.AnimeSeason]

    def lookups(self, request, model_admin):
        return [
            (str(year) + str(season.value), season.label + ' ' + str(year)) for (year, season) in self.year_season_list
        ]
    
    def queryset(self, request, queryset):
        if self.value():
            return AnimeUtil.annotate_year_season(queryset).filter(AnimeUtil.is_ongoing_filter_func(int(self.value())))
        else:
            return queryset

class YearSeasonEmptyFilter(admin.SimpleListFilter):
    title = 'empty year/season'
    parameter_name = 'empty'

    def lookups(self, request, model_admin):
        return [
            ('start',  'Start year/season' ),
            ('end',    'End year/season'   ),
            ('subbed', 'Subbed year/season'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'start':
            return queryset.filter(Q(start_year__isnull =True) | Q(start_season__isnull =True))
        elif self.value() == 'end':
            return queryset.filter(Q(end_year__isnull   =True) | Q(end_season__isnull   =True))
        elif self.value() == 'subbed':
            return queryset.filter(Q(subbed_year__isnull=True) | Q(subbed_season__isnull=True))
        else:
            return queryset
        
class CondensedAnimeTypeFilter(admin.SimpleListFilter):
    title = 'anime category'
    parameter_name = 'animecat'

    def lookups(self, request, model_admin):
        return [
            ('series', 'Anime series'),
            ('special', 'Special anime'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'series':
            return queryset.filter(AnimeUtil.anime_series_filter)
        elif self.value() == 'special':
            return queryset.filter(AnimeUtil.special_anime_filter)
        else:
            return queryset

class HasImageFilter(admin.SimpleListFilter):
    title = 'image existence'
    parameter_name = 'hasimage'

    def lookups(self, request, model_admin):
        return [
            ('true', 'Has image'),
            ('false', 'No images'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.annotate(image_count=Count('image')).filter(image_count__gt=0)
        if self.value() == 'false':
            return queryset.annotate(image_count=Count('image')).filter(image_count=0)
        else:
            return queryset


class AnimeNameInline(admin.TabularInline):
    model = AnimeName
    extra = 1

class ImageInlineFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        model = super().save_new(form, False)

        image_org = PIL.Image.open(model.file_original)

        # Try to remove alpha channel - not all non-RGB modes have an alpha channel, but this should not affect the output
        if image_org.mode !='RGB':
            bg = PIL.Image.new('RGBA', image_org.size, (255, 255, 255, 255))
            image_org_noalpha = PIL.Image.alpha_composite(bg, image_org.convert('RGBA')).convert('RGB')

            if self.request:
                messages.info(self.request, 'Removed alpha channel from image.')

        image_formats = {
            'jpg': {
                'format': 'JPEG',
                'extension': 'jpg',
                'kwargs': {'quality': 80},
                'alpha': False,
            },
            'png': {
                'format': 'PNG',
                'extension': 'png',
                'kwargs': {},
                'alpha': True,
            },
        }
        image_types = {
            'original': {
                'width': None,
                'model_field': model.file_original,
                'format': image_formats['png'],
            },
            'large': {
                'width': 600,
                'model_field': model.file_large,
                'format': image_formats['jpg'],
            },
            'medium': {
                'width': 375,
                'model_field': model.file_medium,
                'format': image_formats['jpg'],
            },
            'small': {
                'width': 150,
                'model_field': model.file_small,
                'format': image_formats['jpg'],
            },
        }
        image_base_name = str(uuid.uuid4()).split('-')[0]

        for image_type, image_values in image_types.items():
            image_format = image_values['format']

            if image_format['alpha']:
                image = image_org.copy()
            else:
                image = image_org_noalpha.copy()

            image_width = image_values['width']
            if image_width:
                image.thumbnail((image_width, image_width * 2))

            content = BytesIO()
            image.save(fp=content, format=image_format['format'], **image_format['kwargs'])

            image_name = f'{image_base_name}-{image_type}.{image_format["extension"]}'
            image_values['model_field'].save(image_name, ContentFile(content.getvalue()))

        return model

class ImageInline(admin.StackedInline):
    model = Image
    formset = ImageInlineFormSet
    readonly_fields = ['file_large', 'file_medium', 'file_small']
    
    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj:
            return max(0, extra - obj.image_set.count())
        else:
            return extra
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

class VideoInline(admin.TabularInline):
    model = Video
    
    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj:
            return max(0, extra - obj.video_set.count())
        else:
            return extra

class SurveyAdditionRemovalInline(admin.TabularInline):
    model = SurveyAdditionRemoval
    readonly_fields = ['timestamp', 'survey', 'anime', 'is_addition', 'response_count']
    extra = 0
    ordering = ['survey__year', 'survey__season', 'anime__id', 'response_count']

class AnimeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,         {'fields': ['anime_type', 'note', ('start_year', 'start_season'), ('end_year', 'end_season'), ('subbed_year', 'subbed_season')]}),
        ('Deprecated', {'fields': ['flags'], 'classes': ['collapse']}),
    ]
    inlines = [AnimeNameInline, ImageInline, VideoInline, SurveyAdditionRemovalInline]
    search_fields = ['animename__name']
    list_filter = [
        CondensedAnimeTypeFilter,
        'anime_type',
        HasImageFilter,
        YearSeasonEmptyFilter,
        YearSeasonListFilter,
    ]
    list_display = [
        '__str__',
        'anime_type',
        'get_start_year_season',
        'get_end_year_season',
        'get_subbed_year_season',
        'has_image',
    ]

    @admin.display(ordering=Concat('start_year', 'start_season'), description='Start')
    def get_start_year_season(self, anime):
        if anime.start_year is not None and anime.start_season is not None:
            return str(anime.start_year) + ' Q' + str(anime.start_season + 1)
        else:
            return None

    @admin.display(ordering=Concat('end_year', 'end_season'), description='End')
    def get_end_year_season(self, anime):
        if anime.end_year is not None and anime.end_season is not None:
            return str(anime.end_year) + ' Q' + str(anime.end_season + 1)
        else:
            return None

    @admin.display(ordering=Concat('subbed_year', 'subbed_season'), description='Subbed')
    def get_subbed_year_season(self, anime):
        if anime.subbed_year is not None and anime.subbed_season is not None:
            return str(anime.subbed_year) + ' Q' + str(anime.subbed_season + 1)
        else:
            return None

    @admin.display(boolean=True, description='Has Image')
    def has_image(self, anime):
        return anime.image_set.count() > 0

    def get_survey_validity_list(self, anime):
        survey_validity_list = []

        # Only get if start year/season is something
        if anime.start_year is not None and anime.start_season is not None:
            start_year_season = AnimeUtil.combine_year_season(anime.start_year, anime.start_season)
            
            # If previous anime is series, go from start to end
            if AnimeUtil.anime_is_series(anime):
                # Get end year/season (if it's nothing, then ~2 years from now)
                if anime.end_year is not None and anime.end_season is not None:
                    end_year_season = AnimeUtil.combine_year_season(anime.end_year, anime.end_season)
                else:
                    end_year_season = AnimeUtil.combine_year_season(datetime.now().year + 2, anime.start_season)
                
                i = start_year_season
                while i <= end_year_season:
                    survey_validity_list += [(i, True), (i, False)]
                    i = AnimeUtil.increment_year_season(i)
            
            # If previous anime is special, only add start and (if it exists) subbed
            else:
                survey_validity_list.append((start_year_season, True))
                if anime.subbed_year is not None and anime.subbed_season is not None:
                    subbed_year_season = AnimeUtil.combine_year_season(anime.subbed_year, anime.subbed_season)
                    survey_validity_list.append((subbed_year_season, False))
        
        return survey_validity_list

    def save_model(self, request, anime, form, change):
        survey_validity_list = self.get_survey_validity_list(anime)

        prev_anime_query = Anime.objects.filter(pk=anime.id)
        if prev_anime_query:
            prev_anime = prev_anime_query[0]
            prev_survey_validity_list = self.get_survey_validity_list(prev_anime)
        else:
            prev_survey_validity_list = []
            
        super().save_model(request, anime, form, change)
        cache.clear()
        
        now = timezone.now()
        ongoing_survey_queryset = Survey.objects.filter(opening_time__lt=now, closing_time__gte=now)
        for survey in ongoing_survey_queryset:
            survey_year_season = AnimeUtil.combine_year_season(survey.year, survey.season)
            
            was_included = (survey_year_season, survey.is_preseason) in prev_survey_validity_list
            is_included = (survey_year_season, survey.is_preseason) in survey_validity_list

            # If anime was removed from survey
            if was_included and not is_included:
                survey_response_count = survey.response_set.count()
                SurveyAdditionRemoval(
                    survey=survey,
                    anime=anime,
                    response_count=survey_response_count,
                    is_addition=False,
                ).save()

            # If anime was added to survey
            elif not was_included and is_included:
                survey_response_count = survey.response_set.count()
                SurveyAdditionRemoval(
                    survey=survey,
                    anime=anime,
                    response_count=survey_response_count,
                    is_addition=True,
                ).save()



class AnimeResponseInline(admin.TabularInline):
    autocomplete_fields = ['anime']
    model = AnimeResponse
    extra = 0

class ResponseAdmin(admin.ModelAdmin):
    fields = [
        'survey',
        'timestamp',
        ('age', 'gender')
    ]
    readonly_fields = ['timestamp', 'survey']
    radio_fields = {'gender': admin.HORIZONTAL}
    inlines = [AnimeResponseInline]
    list_display = [
        'survey',
        'timestamp',
        'age',
        'gender',
        'get_anime_response_count',
    ]

    @admin.display(description='Response Count')
    def get_anime_response_count(self, response):
        return response.animeresponse_set.count()

class SurveyAdmin(admin.ModelAdmin):
    fields = [
        'is_preseason',
        ('opening_time', 'closing_time'),
        ('year', 'season')
    ]
    list_display = [
        '__str__',
        'opening_time',
        'closing_time'
    ]
    inlines = [SurveyAdditionRemovalInline]


class MissingAnimeAdmin(admin.ModelAdmin):
    list_display = ('name', 'survey', 'admin_has_reviewed')
    fieldsets = (
        ('Information', {
            'fields': ('user', 'name', 'link', 'survey', 'description', 'user_has_read'),
        }),
        ('Admin', {
            'fields': ('reason', 'anime', 'admin_has_reviewed'),
        })
    )
    autocomplete_fields = ['anime']
    readonly_fields = ['user', 'survey', 'user_has_read', 'description', 'name', 'link']


admin.site.register(Anime, AnimeAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(MissingAnime, MissingAnimeAdmin)
