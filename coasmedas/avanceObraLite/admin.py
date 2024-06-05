from django.contrib import admin
from .models import APeriodicidadG,BEsquemaCapitulosG,CEsquemaCapitulosActividadesG,Cronograma
from .models import EPresupuesto,FDetallePresupuesto, PeriodoProgramacion, DetallePeriodoProgramacion, DetalleReporteTrabajo
from .models import UnidadConstructiva, ManoDeObra, Material, DesgloceManoDeObra, DesgloceMaterial
from .models import TipoUnidadConstructiva, CatalogoUnidadConstructiva, ReporteTrabajo
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


class AdminCronogramaGrafico(admin.ModelAdmin):
	list_display=('nombre','proyecto','esquema','programacionCerrada','fechaInicio','fechaFinal')
	search_display=('nombre',)
	list_filter=('proyecto','esquema')

admin.site.register(Cronograma,AdminCronogramaGrafico)


class AdminPeriodoProgramacion(admin.ModelAdmin):
	list_display=('cronograma','fechaDesde','fechaHasta')
	search_display=('nombre',)
	list_filter=('cronograma',)

admin.site.register(PeriodoProgramacion,AdminPeriodoProgramacion)


class AdminDetallePeriodoProgramacion(admin.ModelAdmin):
	list_display=('id','periodoProgramacion','detallePresupuesto','cantidad')
	# search_display=('presupuesto',)
	list_filter=('detallePresupuesto','periodoProgramacion')

admin.site.register(DetallePeriodoProgramacion,AdminDetallePeriodoProgramacion)

# -------------------------------------------------------------------------------

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

#---------------------------------------------------------------


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




class AdminReporteTrabajo(admin.ModelAdmin):
	list_display=('id','fechaReporte','periodoProgramacion','reporteCerrado','sinAvance')
	# search_display=('nombre',)
	list_filter=('reporteCerrado','sinAvance')

admin.site.register(ReporteTrabajo,AdminReporteTrabajo)



class AdminDetalleReporteTrabajo(admin.ModelAdmin):
	list_display=('id','reporteTrabajo','detallePresupuesto','cantidad')
	# search_display=('nombre',)
	list_filter=('detallePresupuesto','reporteTrabajo')

admin.site.register(DetalleReporteTrabajo,AdminDetalleReporteTrabajo)