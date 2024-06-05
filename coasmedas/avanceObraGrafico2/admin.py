from django.contrib import admin
from .models import APeriodicidadG,BEsquemaCapitulosG,CEsquemaCapitulosActividadesG,CReglasEstadoG,Cronograma,DiagramaGrahm
from .models import EPresupuesto,FDetallePresupuesto,GCapa,HNodo,IEnlace
from .models import UnidadConstructiva, ManoDeObra, Material, DesgloceManoDeObra, DesgloceMaterial
from .models import TipoUnidadConstructiva, CatalogoUnidadConstructiva
from .models import FotoNodo, EReformado, EReformadoDetalle
from .models import MLiquidacionUUCC
# Register your models here.

class AdminAPeriodicidadGrafico(admin.ModelAdmin):
	list_display=('nombre','numero_dias')
	search_display=('nombre',)

admin.site.register(APeriodicidadG,AdminAPeriodicidadGrafico)


class AdminEsqsuemaCapituloGrafico(admin.ModelAdmin):
	list_display=('nombre','macrocontrato')
	search_display=('nombre',)
	list_filter=('macrocontrato',)

admin.site.register(BEsquemaCapitulosG,AdminEsqsuemaCapituloGrafico)

class AdminEsqsuemaCapituloActividadGrafico(admin.ModelAdmin):
	list_display=('nombre','esquema','nivel','padre')
	search_display=('nombre',)
	list_filter=('esquema','padre')

admin.site.register(CEsquemaCapitulosActividadesG,AdminEsqsuemaCapituloActividadGrafico)


class AdminReglaEstadoGrafico(admin.ModelAdmin):
	list_display=('nombre','esquema','orden',)
	search_display=('nombre',)
	list_filter=('esquema',)

admin.site.register(CReglasEstadoG,AdminReglaEstadoGrafico)


class AdminCronogramaGrafico(admin.ModelAdmin):
	list_display=('nombre','proyecto','estado','esquema','programacionCerrada')
	search_display=('nombre',)
	list_filter=('proyecto','estado','esquema')

admin.site.register(Cronograma,AdminCronogramaGrafico)


class AdminDiagramaGrahmGrafico(admin.ModelAdmin):
	list_display=('cronograma','actividad','fechaInicio','fechaFinal','actividad_inicial')
	search_display=('cronograma',)
	list_filter=('cronograma','actividad',)

admin.site.register(DiagramaGrahm,AdminDiagramaGrahmGrafico)

class AdminPresupuestoGrafico(admin.ModelAdmin):
	list_display=('nombre','cronograma','cerrar_presupuesto')
	search_display=('nombre',)
	list_filter=('cronograma',)

admin.site.register(EPresupuesto,AdminPresupuestoGrafico)


class AdminDetallePresupuestoGrafico(admin.ModelAdmin):
	list_display=('presupuesto','actividad','codigoUC','descripcionUC',
		'valorGlobal','porcentaje','catalogoUnidadConstructiva')
	search_display=('presupuesto',)
	list_filter=('presupuesto','actividad','catalogoUnidadConstructiva')

admin.site.register(FDetallePresupuesto,AdminDetallePresupuestoGrafico)


class AdminCapaGrafico(admin.ModelAdmin):
	list_display=('nombre','color')
	search_display=('nombre',)

admin.site.register(GCapa,AdminCapaGrafico)


class AdminNodoGrafico(admin.ModelAdmin):
	list_display=('presupuesto','nombre','latitud','longitud','noProgramado')
	search_display=('presupuesto',)
	list_filter=('presupuesto',)

admin.site.register(HNodo,AdminNodoGrafico)


class AdminEnlaceGrafico(admin.ModelAdmin):
	list_display=('detallepresupuesto','nodoOrigen','nodoDestino','capa')
	search_display=('detallepresupuesto',)
	list_filter=('detallepresupuesto',)

admin.site.register(IEnlace,AdminEnlaceGrafico)

class AdminTipoUnidadConstructiva(admin.ModelAdmin):
	list_display=('id','nombre','activa',)
	search_display=('nombre',)
	list_filter=('activa',)

admin.site.register(TipoUnidadConstructiva,AdminTipoUnidadConstructiva)

class AdminCatalogoUnidadConstructiva(admin.ModelAdmin):
	list_display=('id','nombre','ano','activo')
	search_display=('nombre',)
	list_filter=('ano','activo')

admin.site.register(CatalogoUnidadConstructiva,AdminCatalogoUnidadConstructiva)

class AdminUnidadConstructiva(admin.ModelAdmin):
	list_display=('id','codigo','descripcion','tipoUnidadConstructiva', 'catalogo')
	search_fields=('codigo','descripcion')
	list_filter=('tipoUnidadConstructiva', 'catalogo')

admin.site.register(UnidadConstructiva,AdminUnidadConstructiva)

class AdminMaterial(admin.ModelAdmin):
	list_display=('id','codigo','descripcion','valorUnitario', 'unidadMedida')
	search_display=('codigo','descripcion')
	#list_filter=('tipoUnidadConstructiva', 'catalogo')

admin.site.register(Material,AdminMaterial)

class AdminDesgloceMaterial(admin.ModelAdmin):
	list_display=('id','unidadConstructiva','material','cantidad')
	search_display=('unidadConstructiva__codigo','unidadConstructiva__descripcion')
	#list_filter=('tipoUnidadConstructiva', 'catalogo')

admin.site.register(DesgloceMaterial,AdminDesgloceMaterial)

class AdminManoDeObra(admin.ModelAdmin):
	list_display=('id','codigo','descripcion','valorHora')
	search_display=('codigo','descripcion')
	#list_filter=('tipoUnidadConstructiva', 'catalogo')

admin.site.register(ManoDeObra,AdminManoDeObra)

class AdminDesgloceManoDeObra(admin.ModelAdmin):
	list_display=('id','unidadConstructiva','manoDeObra','rendimiento')
	search_display=('unidadConstructiva__codigo','unidadConstructiva__descripcion')
	#list_filter=('tipoUnidadConstructiva', 'catalogo')

admin.site.register(DesgloceManoDeObra,AdminDesgloceManoDeObra)

class AdminFotoNodo(admin.ModelAdmin):
	list_display=('id','proyecto','nodo','fecha','ruta','comentario')
	search_display=('nodo',)
	#list_filter=('tipoUnidadConstructiva', 'catalogo')

admin.site.register(FotoNodo,AdminFotoNodo)

class AdminReformadoGrafico(admin.ModelAdmin):
	list_display=('usuario_registro','fecha_registro')
	search_display=('usuario_registro')
	list_filter=('fecha_registro',)

admin.site.register(EReformado,AdminReformadoGrafico)

class AdminReformadoDetalle(admin.ModelAdmin):
	list_display=('apoyo','codigo_uucc','cantidad_anterior','cantidad_final','diferencia','reformado')
	search_display=('codigo_uucc',)
	list_filter=('reformado',)

admin.site.register(EReformadoDetalle,AdminReformadoDetalle)

class AdminLiquidacionUUCC(admin.ModelAdmin):
	list_display=('id','estado','fecha','presupuesto')
	# search_display=('nodo',)
	#list_filter=('tipoUnidadConstructiva', 'catalogo')

admin.site.register(MLiquidacionUUCC,AdminLiquidacionUUCC)