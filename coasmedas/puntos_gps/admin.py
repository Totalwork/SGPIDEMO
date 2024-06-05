from django.contrib import admin
from puntos_gps.models import PuntosGps
# Register your models here.
class AdminPuntosGps(admin.ModelAdmin):
	list_display=('proyecto','longitud','latitud',)
	search_fields=('proyecto__nombre',)	

admin.site.register(PuntosGps,AdminPuntosGps)
