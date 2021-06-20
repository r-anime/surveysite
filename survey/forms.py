from django.forms import ModelForm, NumberInput, CheckboxInput, Select, BooleanField
from django.forms.widgets import Textarea
from .models import Response, AnimeResponse, MissingAnime

def bootstrapmixin_factory(css_class_list=[]):
    """Creates a BootstrapMixin ModelForm mixin that applies basic Bootstrap CSS classes and potential provided CSS classes."""
    class BootstrapMixinInternal:
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            for field in self.visible_fields():
                if isinstance(field.field.widget, CheckboxInput):
                    field.field.widget.attrs['class'] = ' '.join(['form-check-input'] + css_class_list)
                else:
                    field.field.widget.attrs['class'] = ' '.join(['form-control']     + css_class_list)
    return BootstrapMixinInternal

BootstrapMixin = bootstrapmixin_factory()



class ResponseForm(BootstrapMixin, ModelForm):
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

    link_user_to_response = BooleanField(
        required=False,
        label='Link this response to your account?',
        help_text='By doing this, you can easily edit your response on any of your devices simply by re-opening this survey while logged in to the same account.',
    )


def get_anime_response_form(is_preseason, is_continuing):
    if is_preseason:
        if is_continuing:
            return PreSeasonContinuingAnimeResponseForm
        else:
            return PreSeasonNewAnimeResponseForm
    else:
        return PostSeasonAnimeResponseForm


# Pre-season survey needs underwatched/expectations hidden/excluded
class AnimeResponseForm(BootstrapMixin, ModelForm):
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



class MissingAnimeForm(bootstrapmixin_factory(['mb-2']), ModelForm):
    class Meta:
        model = MissingAnime
        fields = ['name', 'link', 'description']
        labels = {
            'name': 'Anime name',
            'link': 'Link to anime',
            'description': 'Extra information (optional)',
        }
        widgets = {
            'description': Textarea(attrs={'rows': 3}),
        }
