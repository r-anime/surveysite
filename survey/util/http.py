from http import HTTPStatus
from django.http import JsonResponse
from json import JSONEncoder
from typing import Type, Union

class JsonErrorResponse(JsonResponse):
    def __init__(self, data: Union[str, list, dict], status: Union[HTTPStatus, int], encoder: Type[JSONEncoder] = None, safe: bool = True, *args, **kwargs) -> None:
        super().__init__({'errors': data}, encoder=encoder, safe=safe, status=status, *args, **kwargs)