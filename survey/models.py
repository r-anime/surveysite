from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from enum import Enum, auto
import uuid

class Anime(models.Model):
    class Meta:
        verbose_name_plural = "anime"

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





def generate_unique_image_file_path(instance, filename):
    return 'survey/images/anime/' + str(instance.anime.id) + '/' + filename

class Image(models.Model):
    # Fields
    name = models.CharField(
        max_length=20,
    )
    file_original = models.ImageField(
        upload_to=generate_unique_image_file_path,
    )
    file_small = models.ImageField(
        editable=False,
        null=True,
        upload_to=generate_unique_image_file_path,
    )
    file_medium = models.ImageField(
        editable=False,
        null=True,
        upload_to=generate_unique_image_file_path,
    )
    file_large = models.ImageField(
        editable=False,
        null=True,
        upload_to=generate_unique_image_file_path,
    )

    # Relation fields
    anime = models.ForeignKey(
        to='Anime',
        on_delete=models.CASCADE,
    )

    def delete(self, *args, **kwargs):
        for storage, path in [(f.storage, f.path) for f in [self.file_large, self.file_medium, self.file_small]]:
            storage.delete(path)

        super().delete(*args, **kwargs)

    def __str__(self):
        return str(self.anime) + ' - ' + self.name



class Survey(models.Model):
    class Meta:
        ordering = ['-year', '-season', 'is_preseason']


    # Fields
    is_preseason = models.BooleanField()
    opening_time = models.DateTimeField()
    closing_time = models.DateTimeField()

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


    class State(Enum):
        UPCOMING = auto()
        ONGOING = auto()
        FINISHED = auto()

    @property
    def state(self):
        now = timezone.now()
        if now < self.opening_time:
            return Survey.State.UPCOMING
        elif self.closing_time < now:
            return Survey.State.FINISHED
        else:
            return Survey.State.ONGOING


    def clean(self):
        super().clean()
        if self.closing_time <= self.opening_time:
            raise ValidationError({'closing_time': 'The closing time must be after the opening time.'})

    def __str__(self):
        return 'The ' + ('Start' if self.is_preseason else 'End') + ' of ' + Anime.AnimeSeason.labels[self.season] + ' ' + str(self.year) + ' Survey'


class SurveyAdditionRemoval(models.Model):
    class Meta:
        verbose_name = 'survey addition/removal'
        verbose_name_plural = 'survey additions & removals'

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
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    timestamp = models.DateTimeField(
        auto_now=True,
    )
    age = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(5), MaxValueValidator(80)],
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
        editable=False,
    )



class AnimeResponse(models.Model):
    # Enums
    class Expectations(models.TextChoices):
        SURPRISE =       'S', _('Surprise')
        DISAPPOINTMENT = 'D', _('Disappointment')
        __empty__ =           _('Met expectations / no answer')
    
    # Fields
    score = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    watching = models.BooleanField()
    underwatched = models.BooleanField()
    expectations = models.CharField(
        max_length=1,
        choices=Expectations.choices,
        blank=True,
        null=True,
    )

    # Relation fields
    response = models.ForeignKey(
        to='Response',
        on_delete=models.CASCADE,
        editable=False,
    )
    anime = models.ForeignKey(
        to='Anime',
        on_delete=models.CASCADE,
        editable=False,
    )



class MtmUserResponse(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['username_hash', 'survey']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['username_hash', 'survey'], name='unique_username_survey'),
        ]

    # Relation fields
    username_hash = models.BinaryField(
        max_length=64, # We're using SHA-512
        editable=False,
    )
    survey = models.ForeignKey(
        to='Survey',
        on_delete=models.CASCADE,
        editable=False,
    )
    response = models.ForeignKey(
        to='Response',
        on_delete=models.CASCADE,
        null=True,
        editable=False,
    )



class MissingAnime(models.Model):
    class Meta:
        verbose_name_plural = "missing anime"

    # Fields
    name = models.CharField(
        max_length=128,
    )
    link = models.URLField()
    description = models.TextField(
        blank=True,
    )
    user_has_read = models.BooleanField(
        default=False,
    )
    admin_has_reviewed = models.BooleanField(
        default=False,
    )
    reason = models.TextField(
        blank=True,
    )

    # Relation fields
    survey = models.ForeignKey(
        to='Survey',
        on_delete=models.CASCADE,
        editable=False,
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
    )
    anime = models.ForeignKey(
        to='Anime',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
    )
