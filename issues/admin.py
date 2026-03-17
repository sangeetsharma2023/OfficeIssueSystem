from .models import Issue, Event, Reference, Tag, File, FileTag
from django.contrib import admin

admin.site.register(Issue)
admin.site.register(Event)
admin.site.register(Reference)
admin.site.register(Tag)
admin.site.register(File)
admin.site.register(FileTag)