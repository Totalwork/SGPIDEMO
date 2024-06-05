
from django.contrib import admin

from activos.models import Categoria, Tipo_Activo, Activo, Atributo, Activo_atributo, Activo_atributo_soporte, Activo_gps, Activo_persona, Motivo,Mantenimiento, Soporte_mantenimiento

class AdminCategoria (admin.ModelAdmin):
	list_display=('id','nombre',)
	search_fields=('nombre',)

class AdminTipo_Activo (admin.ModelAdmin):
	list_display=('id','categoria','nombre','prefijo',)
	list_filter=('categoria',)
	search_fields=('nombre','categoria__nombre',)

class AdminActivo (admin.ModelAdmin):
	list_display=('id','identificacion','serial_placa','tipo','descripcion','contrato','valor_compra','responsable',
		'periodicidad_mantenimiento','debaja','motivo_debaja','soportedebaja','fecha_baja','fecha_alta',)
	list_filter=('tipo','contrato','responsable','debaja',)
	search_fields=('identificacion','serial_placa','descripcion',)


class AdminActivo_gps (admin.ModelAdmin):
	list_display= ('id','activo','nombre','longitud','latitud',)
	list_filter= ('activo',)
	search_fields= ('activo__identificacion','nombre',)

class AdminAtributo (admin.ModelAdmin):
	list_display=('id','tipo','nombre','requiere_soporte',)
	list_filter=('tipo','requiere_soporte',)
	search_fields=('nombre','tipo__nombre',)

class AdminActivo_atributo (admin.ModelAdmin):
	list_display=('id','activo','atributo','valor',)
	list_filter=('activo','atributo',)
	search_fields=('activo__identificacion','atributo__nombre',)


class AdminActivo_atributo_soporte (admin.ModelAdmin):
	list_display=('id','activo_atributo','documento',)
	list_filter=('activo_atributo',)
	search_fields=('activo_atributo',)

class AdminActivo_persona (admin.ModelAdmin):
	list_display=('id','persona','activo',)
	list_filter=('activo',)
	search_fields=('persona__nombre','activo__descripcion',)

class AdminMotivo (admin.ModelAdmin):
	list_display=('id','nombre','tipo_activo',)
	list_filter=('tipo_activo',)
	search_fields=('nombre',)

class AdminMantenimiento (admin.ModelAdmin):
	list_display=('id','activo','motivo','fecha','hora','observaciones','contrato',)
	list_filter=('activo','motivo','contrato',)
	search_fields=('activo__descripcion','motivo__nombre','contrato__nombre',)


class AdminSoporte_mantenimiento (admin.ModelAdmin):
	list_display=('id','mantenimiento','nombre','archivo',)
	list_filter=('mantenimiento',)
	search_fields=('nombre','archivo',)



admin.site.register(Categoria,  AdminCategoria)
admin.site.register(Tipo_Activo, AdminTipo_Activo)
admin.site.register(Activo, AdminActivo)
admin.site.register(Atributo, AdminAtributo)
admin.site.register(Activo_gps, AdminActivo_gps)
admin.site.register(Activo_atributo, AdminActivo_atributo)
admin.site.register(Activo_atributo_soporte, AdminActivo_atributo_soporte)
admin.site.register(Activo_persona, AdminActivo_persona)
admin.site.register(Motivo,AdminMotivo)
admin.site.register(Mantenimiento, AdminMantenimiento)
admin.site.register(Soporte_mantenimiento,AdminSoporte_mantenimiento)