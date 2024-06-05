from django.contrib import admin
from informe_mme.models import InformeMME,InformeConsecutivo
# Register your models here.
class Informemme(admin.ModelAdmin):
	list_display=('empresa','contrato',)
	search_fields=('consecutivo','ano')		

admin.site.register(InformeMME,Informemme)
