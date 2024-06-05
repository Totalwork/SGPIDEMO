from django.contrib import admin
from .models import APeriodicidad,BCronograma,CIntervaloCronograma,Comentario,DActividad,Linea,Meta,Porcentaje,Soporte
from .models import AEsquemaCapitulos,AEsquemaCapitulosActividades,AReglasEstado

# Register your models here.
class AdminPeriodicidad(admin.ModelAdmin):
	list_display=('nombre','numero_dias',)
	search_fields=('nombre',)
	list_filter=('nombre',)		

admin.site.register(APeriodicidad,AdminPeriodicidad)


class AdminCronograma(admin.ModelAdmin):
	list_display=('nombre','proyecto','intervalos','linea_base_terminada','fecha_inicio_cronograma','periodicidad','esquema','estado',)
	search_fields=('nombre','proyecto','linea_base_terminada','esquema',)
	list_filter=('nombre','proyecto','linea_base_terminada','esquema',)		

admin.site.register(BCronograma,AdminCronograma)

class AdminReglaEstado(admin.ModelAdmin):
	list_display=('esquema','orden','operador','limite','estado',)
	search_fields=('esquema','operador',)
	list_filter=('esquema','operador',)		

admin.site.register(AReglasEstado,AdminReglaEstado)

class AdminIntervaloCronograma(admin.ModelAdmin):
	list_display=('cronograma','intervalo','tipo_linea','fecha_corte',)
	search_fields=('cronograma',)
	list_filter=('cronograma',)		

admin.site.register(CIntervaloCronograma,AdminIntervaloCronograma)

class AdminComentario(admin.ModelAdmin):
	list_display=('intervalo','tipo_linea','comentario',)
	search_fields=('tipo_linea',)
	list_filter=('tipo_linea',)		

admin.site.register(Comentario,AdminComentario)


class AdminActividades(admin.ModelAdmin):
	list_display=('cronograma','esquema_actividades',)
	search_fields=('cronograma','esquema_actividades',)
	list_filter=('cronograma','esquema_actividades',)		

admin.site.register(DActividad,AdminActividades)


class AdminLinea(admin.ModelAdmin):
	list_display=('intervalo','tipo_linea','cantidad','actividad',)
	search_fields=('tipo_linea',)
	list_filter=('tipo_linea',)		

admin.site.register(Linea,AdminLinea)


class AdminMeta(admin.ModelAdmin):
	list_display=('actividad','cantidad',)

admin.site.register(Meta,AdminMeta)


class AdminPorcentaje(admin.ModelAdmin):
	list_display=('intervalo','tipo_linea','porcentaje',)
	search_fields=('tipo_linea',)
	list_filter=('tipo_linea',)		

admin.site.register(Porcentaje,AdminPorcentaje)

class AdminSoporte(admin.ModelAdmin):
	list_display=('intervalo','ruta','nombre',)
	search_fields=('nombre',)
	list_filter=('nombre',)		

admin.site.register(Soporte,AdminSoporte)

class AdminEsquemaCapitulos(admin.ModelAdmin):
	list_display=('nombre','macrocontrato',)
	search_fields=('macrocontrato',)
	list_filter=('macrocontrato',)		

admin.site.register(AEsquemaCapitulos,AdminEsquemaCapitulos)

class AdminEsquemaCapitulosActividades(admin.ModelAdmin):
	list_display=('esquema','nivel','nombre','padre','peso',)
	search_fields=('esquema',)
	list_filter=('esquema',)		

admin.site.register(AEsquemaCapitulosActividades,AdminEsquemaCapitulosActividades)

