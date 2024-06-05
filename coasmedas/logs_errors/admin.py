from django.contrib import admin
from .models import Excepciones

# Register your models here.
class AdminExcepciones(admin.ModelAdmin):
	list_display=('modulo', 'fecha_registro', 'error',)
	search_fields=('modulo', 'fecha_registro',)
	list_filter=('modulo', 'fecha_registro',)

admin.site.register(Excepciones,AdminExcepciones)	
