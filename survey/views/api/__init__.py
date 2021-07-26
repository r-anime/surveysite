from typing import Iterable
from django.core.serializers import serialize
from django.db.models import Model
from django.http import HttpResponse

class JsonResponse(HttpResponse):
    def __init__(self, data: Iterable[Model], **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        data = serialize('json', data)
        super().__init__(content=data, **kwargs)