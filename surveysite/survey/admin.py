from django.contrib import admin
from .models import Anime, AnimeName, Video, Image, Survey, Response, AnimeResponse

admin.site.register(Anime)
admin.site.register(AnimeName)
admin.site.register(Video)
admin.site.register(Image)
admin.site.register(Survey)
admin.site.register(Response)
admin.site.register(AnimeResponse)
