from __future__ import annotations
from dataclasses import dataclass
from survey.models import Anime, AnimeName, Image
from django.db.models import Model
from django.forms.models import model_to_dict
from json import JSONEncoder
from math import isnan
from typing import Any, Callable, Optional, Tuple, Type


def json_encoder_factory(fields_per_model: dict[Type[Model], list[str]] = {}, excluded_fields_per_model: dict[Type[Model], list[str]] = {}):
    class JsonEncoder(JSONEncoder):
        def __init__(self, *, skipkeys: bool, ensure_ascii: bool, check_circular: bool, allow_nan: bool, sort_keys: bool, indent: Optional[int], separators: Optional[Tuple[str, str]], default: Optional[Callable[..., Any]]) -> None:
            super().__init__(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, separators=separators, default=default)

            self.fields_per_model = fields_per_model
            self.excluded_fields_per_model = excluded_fields_per_model
            
        def default(self, o: Any) -> Any:
            if isinstance(o, DataBase):
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
class DataBase:
    @classmethod
    def get_fields(cls):
        return list(cls.__dataclass_fields__.keys())

    def to_dict(self):
        fields = self.get_fields()
        return { field: value.to_dict() if isinstance(value := getattr(self, field), DataBase) else value for field in fields }

@dataclass
class UserData(DataBase):
    authenticated: bool
    username: Optional[str]
    profile_picture: Optional[str]

@dataclass
class ImageData(DataBase):
    name: str
    url_small: str
    url_medium: str
    url_large: str

@dataclass
class AnimeNameData(DataBase):
    name: str
    is_official: bool
    type: AnimeName.AnimeNameType

@dataclass
class AnimeData(DataBase):
    names: list[AnimeNameData]
    images: list[ImageData]

    @staticmethod
    def from_model(model: Anime) -> AnimeData:
        name_model_list: list[AnimeName] = model.animename_set.all()
        name_data_list = [AnimeNameData(
            name.name,
            name.official,
            name.anime_name_type
        ) for name in name_model_list]

        image_model_list: list[Image] = model.image_set.all()
        image_data_list = [ImageData(
            image.name,
            image.file_small.url,
            image.file_medium.url,
            image.file_large.url
        ) for image in image_model_list]

        return AnimeData(name_data_list, image_data_list)
