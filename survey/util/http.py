from http import HTTPStatus
from django.http import HttpResponse, JsonResponse
from json import JSONEncoder
from typing import Any, Optional, Type, Union

class JsonErrorResponse(JsonResponse):
    def __init__(self, data: Union[str, list[Any], dict[Any, Any]], status: Union[HTTPStatus, int], encoder: Optional[Type[JSONEncoder]] = None, safe: bool = True, *args, **kwargs) -> None:
        if isinstance(data, str):
            error_data = {'global': [data]}
        elif isinstance(data, list):
            error_data = {'global': data}
        else:
            error_data = data
            
        super().__init__({'errors': error_data}, encoder=encoder, safe=safe, status=status, *args, **kwargs)

class HttpEmptyErrorResponse(HttpResponse):
    def __init__(self, status: Union[HTTPStatus, int], *args, **kwargs) -> None:
        super().__init__({}, status=status, *args, **kwargs)
