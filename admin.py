from django.contrib import admin

from .models import *

class PictureAdmin(admin.ModelAdmin):
    exclude = ("content", "content_type")

admin.site.register(Chest)
admin.site.register(Item)
admin.site.register(Note)
admin.site.register(Picture, PictureAdmin)
admin.site.register(Settings)
