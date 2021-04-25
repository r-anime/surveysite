from django.forms import ModelForm, NumberInput, CheckboxInput, Select
from .models import Response, AnimeResponse


class ResponseForm(ModelForm):
    class Meta:
        model = Response
        fields = '__all__'
        labels = {
            'age': 'How old are you?',
            'gender': 'Which gender do you identify as?',
        }
        widgets = {
            'age': NumberInput(attrs={'min': 10, 'max': 80}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


def get_anime_response_form(is_preseason, is_continuing):
    if is_preseason:
        if is_continuing:
            return PreSeasonContinuingAnimeResponseForm
        else:
            return PreSeasonNewAnimeResponseForm
    else:
        return PostSeasonAnimeResponseForm


# Pre-season survey needs underwatched/expectations hidden/excluded
class AnimeResponseForm(ModelForm):
    class Meta:
        exclude = []
        model = AnimeResponse
        widgets = {
            'score': Select(choices=[
                (None, '---------'),
                (5, '5/5 - Great'),
                (4, '4/5'),
                (3, '3/5 - Average'),
                (2, '2/5'),
                (1, '1/5 - Bad'),
            ])
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.visible_fields():
            if isinstance(field.field.widget, CheckboxInput):
                field.field.widget.attrs['class'] = 'form-check-input'
            else:
                field.field.widget.attrs['class'] = 'form-control'

    def is_empty(self):
        watching = self.cleaned_data.get('watching', False)
        score = self.cleaned_data.get('score', None)
        underwatched = self.cleaned_data.get('underwatched', False)
        expectations = self.cleaned_data.get('expectations', None)

        return not watching and not score and not underwatched and not expectations

class PreSeasonNewAnimeResponseForm(AnimeResponseForm):
    class Meta(AnimeResponseForm.Meta):
        labels = {
            'watching': 'Will you watch this?',
            'score': 'How good do you expect this to be?',
        }

class PreSeasonContinuingAnimeResponseForm(AnimeResponseForm):
    class Meta(AnimeResponseForm.Meta):
        labels = {
            'watching': 'Did you watch this and will you continue watching this?',
            'score': 'How good do you expect the remainder to be?',
        }

class PostSeasonAnimeResponseForm(AnimeResponseForm):
    class Meta(AnimeResponseForm.Meta):
        labels = {
            'watching': 'Did you watch this?',
            'score': 'What did you think of this?',
            'underwatched': 'Did you find this underwatched?',
            'expectations': 'Was this a surprise or disappointment?',
        }
