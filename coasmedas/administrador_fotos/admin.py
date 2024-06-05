from django.contrib import admin
from administrador_fotos.models import ACategoria,BSubcategoria,CFotosProyecto,DFotosSubcategoria
# Register your models here.
class Categoria(admin.ModelAdmin):
	list_display=('proyecto','categoria','contrato',)
	search_fields=('categoria','contrato__nombre','proyecto__nombre')		

admin.site.register(ACategoria,Categoria)


class Subcategoria(admin.ModelAdmin):
	list_display=('categoria','titulo','contenido','proyecto',)
	search_fields=('titulo','contenido','categoria__categoria','proyecto__nombre',)	

admin.site.register(BSubcategoria,Subcategoria)


class FotosProyecto(admin.ModelAdmin):
	list_display=('proyecto','fecha','ruta','comentarios','asociado_reporte','tipo',)
	list_filter=('tipo','fecha',)
	search_fields=('comentarios','proyecto__nombre',)	

admin.site.register(CFotosProyecto,FotosProyecto)


class FotosSubcategoria(admin.ModelAdmin):
	list_display=('subcategoria','ruta',)
	search_fields=('subcategoria__titulo',)	

admin.site.register(DFotosSubcategoria,FotosSubcategoria)