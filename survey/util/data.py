from __future__ import annotations
from dataclasses import dataclass
from django.db.models import Model
from django.forms.models import model_to_dict
from django.utils.functional import classproperty
from enum import Enum
from json import JSONEncoder
from survey.models import Anime, AnimeName, Image, Survey
from typing import Any, Callable, Optional, Tuple, Type


def json_encoder_factory(fields_per_model: dict[Type[Model], list[str]] = {}, excluded_fields_per_model: dict[Type[Model], list[str]] = {}):
    class JsonEncoder(JSONEncoder):
        def __init__(self, *, ensure_ascii: bool, check_circular: bool, sort_keys: bool, separators: Optional[Tuple[str, str]], default: Optional[Callable[..., Any]], **kwargs) -> None:
            super().__init__(allow_nan=False, skipkeys=False, indent=None, ensure_ascii=ensure_ascii, check_circular=check_circular, sort_keys=sort_keys, separators=separators, default=default)

            self.fields_per_model = fields_per_model
            self.excluded_fields_per_model = excluded_fields_per_model
            
        def default(self, o: Any) -> Any:
            if isinstance(o, ViewModelBase):
                return o.to_dict()

            elif isinstance(o, Model):
                return model_to_dict(
                    o,
                    fields=self.fields_per_model.get(o.__class__, None),
                    exclude=self.excluded_fields_per_model.get(o.__class__, None)
                )
            
            return super().default(o)

    return JsonEncoder


@dataclass
class ViewModelBase:
    @classmethod
    def get_fields(cls):
        return list(cls.__dataclass_fields__.keys())

    @classmethod
    def from_dict(cls, d: dict[str, Any]):
        fields = cls.get_fields()
        parsers = cls.dict_field_parsers

        # Filter only the known fields from the dict, and parse values if necessary
        try:
            kwargs = {
                field: (
                    parsers[field](d[field])
                    if field in parsers else
                    d[field]
                ) for field in fields
            }
        except KeyError as e:
            raise KeyError('Field ' + str(e) + ' was not found (class ' + cls.__name__ + ')')
        return cls(**kwargs)

    def to_dict(self):
        fields = self.get_fields()
        return { field: value.to_dict() if isinstance(value := getattr(self, field), ViewModelBase) else value for field in fields }

    @classproperty
    def dict_field_parsers(cls) -> dict[str, Callable[[Any], Any]]:
        return {}

@dataclass
class ImageViewModel(ViewModelBase):
    name: str
    url_small: str
    url_medium: str
    url_large: str

    @staticmethod
    def from_model(model: Image) -> ImageViewModel:
        return ImageViewModel(
            name=model.name,
            url_small=model.file_small.url,
            url_medium=model.file_medium.url,
            url_large=model.file_large.url,
        )

@dataclass
class AnimeNameViewModel(ViewModelBase):
    name: str
    is_official: bool
    type: AnimeName.AnimeNameType

    @staticmethod
    def from_model(model: AnimeName) -> AnimeNameViewModel:
        return AnimeNameViewModel(
            name=model.name,
            is_official=model.official,
            type=model.anime_name_type,
        )

@dataclass
class AnimeViewModel(ViewModelBase):
    id: int
    names: list[AnimeNameViewModel]
    images: list[ImageViewModel]
    anime_type: str

    @staticmethod
    def from_model(model: Anime) -> AnimeViewModel:
        name_data_list = [AnimeNameViewModel.from_model(name) for name in model.animename_set.all()]
        image_data_list = [ImageViewModel.from_model(image) for image in model.image_set.all()]
        return AnimeViewModel(
            id=model.id,
            names=name_data_list,
            images=image_data_list,
            anime_type=model.anime_type,
        )

@dataclass
class SurveyViewModel(ViewModelBase):
    year: int
    season: int
    is_preseason: bool
    opening_epoch_time: int
    closing_epoch_time: int

    @staticmethod
    def from_model(model: Survey) -> SurveyViewModel:
        return SurveyViewModel(
            year         = model.year,
            season       = model.season,
            is_preseason = model.is_preseason,
            opening_epoch_time = model.opening_time.timestamp() * 1000,
            closing_epoch_time = model.closing_time.timestamp() * 1000,
        )


class ResultType(int, Enum):
    """Enum representing all types of result values."""
    POPULARITY                  =  1 #"Popularity"
    POPULARITY_MALE             =  2 #"Popularity (Male)"
    POPULARITY_FEMALE           =  3 #"Popularity (Female)"
    GENDER_POPULARITY_RATIO     =  4 #"Gender Ratio (♂:♀)"
    SCORE                       = 11 #"Score"
    SCORE_MALE                  = 12 #"Score (Male)"
    SCORE_FEMALE                = 13 #"Score (Female)"
    GENDER_SCORE_DIFFERENCE     = 14 #"Gender Score Difference (♂-♀)"
    UNDERWATCHED                = 21 #"Underwatched"
    SURPRISE                    = 22 #"Surprise"
    DISAPPOINTMENT              = 23 #"Disappointment"
    AGE                         = 24 #"Average Viewer Age"
