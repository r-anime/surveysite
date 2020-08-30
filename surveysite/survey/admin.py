from django.contrib import admin
from .models import Anime, Video, Image, Survey, Response, ResponseAnime

admin.site.register(Anime)
admin.site.register(Video)
admin.site.register(Image)
admin.site.register(Survey)
admin.site.register(Response)
admin.site.register(ResponseAnime)