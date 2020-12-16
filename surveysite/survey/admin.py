from django.contrib import admin
from django.db.models import Q
from django.db.models.functions import Concat
from datetime import datetime
from .models import Anime, AnimeName, Video, Image, Survey, Response, AnimeResponse
from .util import AnimeUtil


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


class AnimeNameInline(admin.TabularInline):
    model = AnimeName
    extra = 1

class ImageInline(admin.TabularInline):
    model = Image
    
    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj:
            return max(0, extra - obj.image_set.count())
        else:
            return extra

class VideoInline(admin.TabularInline):
    model = Video
    
    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj:
            return max(0, extra - obj.video_set.count())
        else:
            return extra

class AnimeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,         {'fields': ['anime_type', 'note', ('start_year', 'start_season'), ('end_year', 'end_season'), ('subbed_year', 'subbed_season')]}),
        ('Deprecated', {'fields': ['flags'], 'classes': ['collapse']}),
    ]
    inlines = [AnimeNameInline, ImageInline, VideoInline]
    search_fields = ['animename__name']
    list_filter = [
        CondensedAnimeTypeFilter,
        'anime_type',
        YearSeasonEmptyFilter,
        YearSeasonListFilter,
    ]
    list_display = [
        '__str__',
        'anime_type',
        'get_start_year_season',
        'get_end_year_season',
        'get_subbed_year_season',
    ]

    def get_start_year_season(self, anime):
        if anime.start_year is not None and anime.start_season is not None:
            return str(anime.start_year) + ' Q' + str(anime.start_season + 1)
        else:
            return None
    get_start_year_season.short_description = 'Start'
    get_start_year_season.admin_order_field = Concat('start_year', 'start_season')

    def get_end_year_season(self, anime):
        if anime.end_year is not None and anime.end_season is not None:
            return str(anime.end_year) + ' Q' + str(anime.end_season + 1)
        else:
            return None
    get_end_year_season.short_description = 'End'
    get_end_year_season.admin_order_field = Concat('end_year', 'end_season')

    def get_subbed_year_season(self, anime):
        if anime.subbed_year is not None and anime.subbed_season is not None:
            return str(anime.subbed_year) + ' Q' + str(anime.subbed_season + 1)
        else:
            return None
    get_subbed_year_season.short_description = 'Subbed'
    get_subbed_year_season.admin_order_field = Concat('subbed_year', 'subbed_season')


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

    def get_anime_response_count(self, response):
        return response.animeresponse_set.count()
    get_anime_response_count.short_description = 'Response Count'


class SurveyAdmin(admin.ModelAdmin):
    fields = [
        'is_preseason',
        'is_ongoing',
        ('year', 'season')
    ]
    ordering = ['year', 'season', 'is_preseason']
    list_display = [
        '__str__',
        'is_ongoing',
    ]
    list_editable = [
        'is_ongoing',
    ]


admin.site.register(Anime, AnimeAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)
