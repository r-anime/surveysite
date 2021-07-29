from dataclasses import dataclass
from django.db.models import Model
from json import JSONEncoder
from typing import Any, Callable, Optional, Tuple, Type

from django.forms.models import model_to_dict

@dataclass
class DataBase:
    @classmethod
    def get_fields(cls):
        return list(cls.__dataclass_fields__.keys())

    def to_dict(self):
        fields = self.get_fields()
        return { field: value.to_dict() if isinstance(value := getattr(self, field), DataBase) else value for field in fields }


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
                return {
                    o.id: model_to_dict(
                        o,
                        fields=self.fields_per_model.get(o.__class__, None),
                        exclude=self.excluded_fields_per_model.get(o.__class__, None)
                    )
                }

            return super().default(o)

    return JsonEncoder
