from http import HTTPStatus
from django.http import JsonResponse
from json import JSONEncoder
from typing import Optional, Type, Union

class JsonErrorResponse(JsonResponse):
    def __init__(self, data: Union[str, list, dict], status: Union[HTTPStatus, int], encoder: Type[JSONEncoder] = None, safe: bool = True, *args, **kwargs) -> None:
        if isinstance(data, str):
            error_data = {'global': [data]}
        elif isinstance(data, list):
            error_data = {'global': data}
        else:
            error_data = data
            
        super().__init__({'errors': error_data}, encoder=encoder, safe=safe, status=status, *args, **kwargs)