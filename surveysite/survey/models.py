from django.db import models
from django.utils.translation import gettext_lazy as _

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
    
    start_season = models.CharField(
        max_length=6,
        blank=True,
    )
    end_season = models.CharField(
        max_length=6,
        blank=True,
    )
    subbed_season = models.CharField(
        max_length=6,
        blank=True,
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
        max_length=50
    )
    url = models.URLField()

    # Relation fields
    anime = models.ForeignKey(
        to='Anime',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
    


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
        return self.name



class Survey(models.Model):
    # Fields
    is_preseason = models.BooleanField()
    season = models.CharField(
        max_length=6,
    )

    # Relation fields
    anime = models.ManyToManyField(
        to='Anime',
    )

    def __str__(self):
        return self.season + ' (' + ('pre-season' if self.is_preseason else 'post-season') + ')'
    



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
        blank=True
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
    anime = models.OneToOneField(
        to='Anime',
        on_delete=models.CASCADE,
    )