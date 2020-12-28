from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from django_resized import ResizedImageField
import uuid

class Anime(models.Model):
    # Enums
    class AnimeType(models.TextChoices):
        TV_SERIES    = 'TV',   _('TV series')
        ONA_SERIES   = 'ONAS', _('ONA series')
        BULK_RELEASE = 'BULK', _('Bulk-released series')
        MOVIE        = 'MV',   _('Movie')
        ONA          = 'ONA',  _('Original Net Animation (ONA)')
        OVA          = 'OVA',  _('Original Video Animation (OVA)')
        TV_SPECIAL   = 'TVSP', _('TV special')

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
        if self.animename_set.all():
            return ' / '.join([str(animename) for animename in self.animename_set.all()])
        else:
            return '__NO_NAMES__'



class AnimeName(models.Model):
    # Enums
    class AnimeNameType(models.TextChoices):
        JAPANESE_NAME = 'JP', _('Japanese name')
        ENGLISH_NAME  = 'EN', _('English name')
        SHORT_NAME    = 'SH', _('Short name')
    
    # Fields
    anime_name_type = models.CharField(
        max_length=2,
        choices=AnimeNameType.choices,
    )
    name = models.CharField(
        max_length=128,
    )
    official = models.BooleanField(
        default=True,
    )

    # Relation fields
    anime = models.ForeignKey(
        to='Anime',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name + ' (' + AnimeName.AnimeNameType(self.anime_name_type) + ')' + ('' if self.official else ' (unofficial)')
    


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
    def generate_unique_file_path(self):
        return lambda instance, filename: 'images/' + str(uuid.uuid4()) + '.' + filename.split('.')[-1]
    
    # Fields
    name = models.CharField(
        max_length=20,
    )
    file = ResizedImageField(
        size=[300, 600],
        force_format='JPEG',
        quality=80,
        upload_to=generate_unique_file_path,
    )

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

    def __str__(self):
        return 'The ' + ('Start' if self.is_preseason else 'End') + ' of ' + Anime.AnimeSeason.labels[self.season] + ' ' + str(self.year) + ' Survey'


class SurveyAdditionRemoval(models.Model):
    # Fields
    timestamp = models.DateTimeField(
        auto_now=True,
    )
    is_addition = models.BooleanField()
    response_count = models.SmallIntegerField()

    # Relation fields
    survey = models.ForeignKey(
        to='Survey',
        on_delete=models.CASCADE,
    )
    anime = models.ForeignKey(
        to='Anime',
        on_delete=models.CASCADE,
    )


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
        blank=True,
        null=True,
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        blank=True,
        null=True,
    )

    # Relation fields
    survey = models.ForeignKey(
        to='Survey',
        on_delete=models.CASCADE,
    )



class AnimeResponse(models.Model):
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
    watching = models.BooleanField()
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