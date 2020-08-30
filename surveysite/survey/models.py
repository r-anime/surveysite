from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

class Anime(models.Model):
    # Enums
    class AnimeType(models.TextChoices):
        TV           = 'TV',   _('TV series')
        MOVIE        = 'MV',   _('Movie')
        ONA          = 'ONA',  _('Original Net Animation (ONA)')
        OVA          = 'OVA',  _('Original Video Animation (OVA)')
        TV_SPECIAL   = 'TVSP', _('TV special')
        ONA_SERIES   = 'ONAS', _('ONA series')
        BULK_RELEASE = 'BULK', _('Bulk-released series')

    class AnimeSeason(models.IntegerChoices):
        WINTER = 0
        SPRING = 1
        SUMMER = 2
        FALL = 3

    # Fields
    anime_type = models.CharField(
        max_length=4,
        choices=AnimeType.choices,
        #default=AnimeType.TV
    )
    flags = models.CharField(
        max_length=4,
        blank=True,
    )
    note = models.CharField(
        max_length=50,
        blank=True,
    )

    japanese_name = models.CharField(
        max_length=128,
        blank=True,
    )
    english_name = models.CharField(
        max_length=128,
        blank=True,
    )
    short_name = models.CharField(
        max_length=32,
        blank=True,
    )

    def get_year(): return datetime.now().year
    def get_season(): return Anime.AnimeSeason(datetime.now().month // 4)

    start_year = models.SmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1960), MaxValueValidator(2040)],
        default=get_year,
    )
    start_season = models.SmallIntegerField(
        blank=True,
        null=True,
        choices=AnimeSeason.choices,
        default=get_season,
    )

    end_year = models.SmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1960), MaxValueValidator(2040)],
        default=None,
    )
    end_season = models.SmallIntegerField(
        blank=True,
        null=True,
        choices=AnimeSeason.choices,
        default=None,
    )

    subbed_year = models.SmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1960), MaxValueValidator(2040)],
        default=None,
    )
    subbed_season = models.SmallIntegerField(
        blank=True,
        null=True,
        choices=AnimeSeason.choices,
        default=None,
    )

    def __str__(self):
        result = ''
        if len(self.japanese_name) > 0 and len(self.english_name) > 0:
            result += self.japanese_name + ' / ' + self.english_name
        elif len(self.japanese_name) == 0 and len(self.english_name) == 0:
            result = '!!NO NAME!!'
        elif len(self.japanese_name) > 0:
            result = self.japanese_name
        else:
            result = self.english_name
        
        if len(self.short_name) > 0:
            result += ' (' + self.short_name + ')'

        return result
    


class Video(models.Model):
    # Fields
    name = models.CharField(
        max_length=50,
    )
    url = models.URLField()

    # Relation fields
    anime = models.ForeignKey(
        to='Anime',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.anime) + ' - ' + self.name
    


class Image(models.Model):
    # Fields
    name = models.CharField(
        max_length=20,
    )
    url = models.URLField()

    # Relation fields
    anime = models.ForeignKey(
        to='Anime',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.anime) + ' - ' + self.name



class Survey(models.Model):
    # Fields
    is_preseason = models.BooleanField()
    is_ongoing = models.BooleanField(
        default=False,
    )

    def get_relevant_year(): return datetime.now().year + (1 if datetime.now().month // 4 + 1 == 4 else 0),
    def get_relevant_season(): return Anime.AnimeSeason((datetime.now().month // 4 + 1) % 4)

    year = models.SmallIntegerField(
        validators=[MinValueValidator(1960), MaxValueValidator(2040)],
        default=get_relevant_year,
    )
    season = models.SmallIntegerField(
        choices=Anime.AnimeSeason.choices,
        default=get_relevant_season,
    )

    # Relation fields
    anime = models.ManyToManyField(
        to='Anime',
    )

    def __str__(self):
        return 'The ' + ('Start' if self.is_preseason else 'End') + ' of ' + Anime.AnimeSeason.labels[self.season] + ' ' + str(self.year) + ' Survey'
    



class Response(models.Model):
    # Enums
    class Gender(models.TextChoices):
        MALE      = 'M', _('Male')
        FEMALE    = 'F', _('Female')
        OTHER     = 'O', _('Other')

    # Fields
    timestamp = models.DateTimeField(
        auto_now=True,
    )
    age = models.IntegerField(
        blank=True
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        blank=True,
    )

    # Relation fields
    survey = models.ForeignKey(
        to='Survey',
        on_delete=models.CASCADE,
    )



class ResponseAnime(models.Model):
    # Enums
    class Expectations(models.TextChoices):
        SURPRISE =       'S', _('Surprise')
        DISAPPOINTMENT = 'D', _('Disappointment')
        __empty__ =           _('N/A')
    
    # Fields
    score = models.IntegerField(
        blank=True,
        null=True,
    )
    underwatched = models.BooleanField()
    expectations = models.CharField(
        max_length=1,
        choices=Expectations.choices,
        blank=True,
    )

    # Relation fields
    response = models.ForeignKey(
        to='Response',
        on_delete=models.CASCADE,
    )
    anime = models.ForeignKey(
        to='Anime',
        on_delete=models.CASCADE,
    )