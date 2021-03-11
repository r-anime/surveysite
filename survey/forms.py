from django.forms import ModelForm, NumberInput #, modelform_factory, inlineformset_factory, modelformset_factory
#from django.db.models.query import EmptyQuerySet
from .models import Response, AnimeResponse

#AnimeResponseForm = modelform_factory(AnimeResponse, fields=['watching', 'underwatched', 'score', 'expectations'])

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
        model = AnimeResponse
        fields = '__all__'
        labels = {
            'underwatched': 'Did you find this underwatched?',
            'expectations': 'Was this a surprise or disappointment?',
        }

    def __init__(self, *args, **kwargs):
        is_preseason = kwargs.pop('is_preseason', False)

        super().__init__(*args, **kwargs)

        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

        self.fields['watching'].label = 'Will you watch this?' if is_preseason else 'Did you watch this?'
        self.fields['score'].label = 'How good will this be?' if is_preseason else 'What did you think of this?'
