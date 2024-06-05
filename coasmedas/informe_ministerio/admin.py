from django.contrib import admin
from .models import Planilla,Tag

# Register your models here.
class AdminPlanilla(admin.ModelAdmin):
	list_display=('tipo','empresa','archivo',)
	search_fields=('tipo','empresa',)
	list_filter=('tipo','empresa',)		

admin.site.register(Planilla,AdminPlanilla)


class AdminTag(admin.ModelAdmin):
	list_display=('nombre','modelo','campo',)
	search_fields=('nombre','modelo','campo',)
	list_filter=('nombre','modelo','campo',)		

admin.site.register(Tag,AdminTag)