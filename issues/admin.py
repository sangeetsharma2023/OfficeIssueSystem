from django.contrib import admin
from .models import Issue, Event, Reference, Tag

admin.site.register(Issue)
admin.site.register(Event)
admin.site.register(Reference)
admin.site.register(Tag)
