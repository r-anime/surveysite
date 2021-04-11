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

    def clean(self):
        cleaned_data = super().clean()

        watching = cleaned_data.get('watching', False)
        score = cleaned_data.get('score', None)
        underwatched = cleaned_data.get('underwatched', False)
        expectations = cleaned_data.get('expectations', None)

        if not watching and not score and not underwatched and not expectations:
            return {}
        else:
            return cleaned_data

class PreSeasonAnimeResponseForm(AnimeResponseForm):
    class Meta(AnimeResponseForm.Meta):
        exclude = ['underwatched', 'expectations']
        labels = {
            'watching': 'Will you watch this?',
            'score': 'How good will this be?',
        }

class PostSeasonAnimeResponseForm(AnimeResponseForm):
    class Meta(AnimeResponseForm.Meta):
        exclude = []
        labels = {
            'watching': 'Did you watch this?',
            'score': 'What did you think of this?',
            'underwatched': 'Did you find this underwatched?',
            'expectations': 'Was this a surprise or disappointment?',
        }
