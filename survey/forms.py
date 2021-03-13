from django.forms import ModelForm, NumberInput, CheckboxInput
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.visible_fields():
            if isinstance(field.field.widget, CheckboxInput):
                field.field.widget.attrs['class'] = 'form-check-input'
            else:
                field.field.widget.attrs['class'] = 'form-control'

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
