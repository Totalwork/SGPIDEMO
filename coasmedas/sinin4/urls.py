from django.urls import path, include
from django.conf.urls import handler404, handler500
from django.conf import settings
from rest_framework import routers
from empresa.views import EmpresaViewSet , EmpresaAccesoViewSet,EmpresaCuentaViewSet
from usuario.views import UsuarioViewSet, PersonaViewSet
from seguridad_social.views import EmpleadoViewSet, NovedadViewSet, PlanillaViewSet,MatriculaViewSet,EscolaridadViewSet, CargoSeguridadSocialViewSet, CorreoContratistaViewSet, PlanillaEmpleadoViewSet
#import seguridad_social



from avance_de_obra.views import PeriodicidadViewSet,CronogramaViewSet,IntervaloCronogramaViewSet,ComentarioViewSet,ActividadViewSet,ReglaEstadoViewSet
from parametrizacion.views import DepartamentoViewSet,MunicipioViewSet,BancoViewSet,CargoViewSet,FuncionarioViewSet,NotificacionViewSet,ResponsabilidadesViewSet,TransaccionesViewSet

from avance_de_obra.views import LineaViewSet,MetaViewSet,PorcentajeViewSet,AvanceObraSoporteViewSet,EsquemaCapitulosViewSet,EsquemaCapitulosActividadesViewSet

from opcion.views import OpcionViewSet, Opcion_UsuarioViewSet
from django.conf.urls.static import static
from contrato.views import ContratoViewSet, Vigencia_contratoViewSet, Empresa_contratoViewSet, RubroViewSet, Sub_contratistaViewSet, Contrato_cesionViewSet, Cesion_economicaViewSet
from contrato.views import ActaAsignacionRecursosContratoViewSet
#from cuenta.views import  CuentaViewSet , CuentaMovimientoViewSet #CREADO : LUIS ALBERTO MENDOZA  **  MODIFICADO :24-10-2016


from tipo.views import TipoViewSet# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 04-11-2016
from estado.views import EstadoViewSet , EstadosPosiblesViewSet# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 04-11-2016
from ubicacion.views import UbicacionViewSet
from giros.views import NombreGiroViewSet,EncabezadoGiroViewSet,DetalleGiroViewSet,RechazoGiroViewSet


from financiero.views import FinancieroCuentaViewSet,FinancieroCuentaMovimientoViewSet,ExtractoCuentaViewSet,ContratistaContratoViewSet

from descargo.views import CorreoDescargoViewSet,AIdInternoDescargoViewSet,ManiobraViewSet,MotivoSgiViewSet,MotivoInterventorViewSet,DescargoTrabajoViewSet,DescargoViewSet,FotoDescargoViewSet
from administrador_fotos.views import CategoriaViewSet,SubcategoriaViewSet,FotosProyectoViewSet,FotosSubcategoriaViewSet



from poliza.views import AseguradoraViewSet, PolizaViewSet, VigenciaPolizaViewSet
from puntos_gps.views import PuntosGpsViewSet


from proceso.views import ProcesoViewSet, ItemViewSet, PermisoEmpresaItemViewSet, VinculoViewSet
from proceso.views import ProcesoRelacionViewSet, ProcesoRelacionDatoViewSet
from proceso.views import SoporteProcesoRelacionDatoViewSet, NotificacionVencimientoViewSet

from factura.views import FacturaViewSet, MesCausadoViewSet, CesionViewSet, DescuentoViewSet, CompensacionViewSet, DetalleCompensacionViewSet, FacturaProyectoViewSet

from seguimiento_retie.views import ConfiguracionPorcentajesViewSet, ProyectosNotificadosViewSet, RetieViewSet, AsistenteVisitaViewSet, HistorialViewSet, NoConformidadRetieViewSet, NotificarCorreoViewSet


from administrador_tarea.views import EquipoViewSet,ColaboradorViewSet,TareaViewSet,AsignacionTareaViewSet,SoporteAsignacionTareaViewSet
from administrador_tarea.views import TareaActividadViewSet,TareaComentarioViewSet,TareaActividadSoporteViewSet

from gestion_proyecto.views import FondoViewSet,CampanaViewSet,SolicitanteViewSet,UnidadMedidaViewSet,CampanaEmpresaViewSet,SoporteSolicitudViewSet
from gestion_proyecto.views import SolicitudDisenoViewSet,DatoDisenoViewSet,DisenoViewSet,DocumentoEstadoViewSet,EstadoDisenoViewSet,ComentarioDisenoViewSet
from gestion_proyecto.views import InfoDisenoViewSet,MapaDisenoViewSet,PermisoDisenoViewSet,SoporteEstadoViewSet,SoporteEstadoComentarioViewSet,VersionDisenoViewSet


from seguimiento_factura.views import GestionOpViewSet


from informe_ministerio.views import TagViewSet,InformePlanillaViewSet
from  deploy.views import SistemaVersionViewSet, InformacionArchivosViewSet

from solicitud.views import SolicitudContratoViewSet, RequisitoJuridicoViewSet, FavorabilidadJuridicaViewSet, FavorabilidadJuridicaRequisitoViewSet
from solicitud.views import RequisitoComprasViewSet, FavorabilidadComprasViewSet, FavorabilidadComprasRequisitoViewSet
from solicitud.views import RequisitoTecnicoViewSet, FavorabilidadTecnicaViewSet, FavorabilidadTecnicaRequisitoViewSet
from solicitud.views import RequisitoPolizaViewSet, ValidarPolizaViewSet, PolizaTipoViewSet, PolizaTipoRequisitoViewSet
from solicitud_giro.views import EncabezadoSolicitudGiroViewSet, DetalleGiroSolicitudGiroViewSet

from control_cambios.views import SolicitaViewSet,UnidadConstructivaViewSet,CambioViewSet,MaterialViewSet,UUCCMaterialViewSet,CambioProyectoViewSet,SoporteViewSet



from solicitudservicio.views import AreaViewSet, SolicitudServicioViewSet, SoporteSolicitudServicioViewSet


from avanceObraGrafico.views import PeriodicidadGViewSet,EsquemaCapitulosGViewSet,EsquemaCapitulosActividadesGViewSet,PresupuestoViewSet,DetallePresupuestoViewSet,ReglaEstadoGraficoViewSet
from avanceObraGrafico.views import CambioAvanceViewSet,NodoViewSet,CronogramaGraficoViewSet,LineaGraficoViewSet,EnlaceGraficoViewSet,EstadoCambioAvanceViewSet,DiagramaGrahmViewSet
from avanceObraGrafico.views import EjecucionProgramadaViewSet,CantidadNodoViewSet

from p_p_construccion.views import LoteViewSet,PropietarioViewSet,SoporteReunionViewSet,EstructurasViewSet,PropietarioLoteViewSet
from solicitudservicio.views import AreaViewSet,SolicitudServicioViewSet,SoporteSolicitudServicioViewSet

from bitacora.views import BitacoraViewSet

from no_conformidad.views import NoConformidadViewSet

from proyecto.views import ProyectoViewSet, P_tipoViewSet , ProyectoEmpresaViewSet , ProyectoFondoViewSet ,ProyectoCampoInfoTecnicaViewSet ,ProyectoInfoTecnicaViewSet, ProyectoActividadesViewSet #CREADO : LUIS ALBERTO MENDOZA  **  MODIFICADO :24-10-2016
from mi_nube.views import ArchivoViewSet , ArchivoUsuarioViewSet
from correspondencia.views import CorresPfijoViewSet , CorrespondenciaEnviadaViewSet , CorrespondenciaSoporteViewSet , CorrespondenciaConsecutivoViewSet , CorrespondenciaRadicadoViewSet , CorrespondenciaPlantillaViewSet
from correspondencia_recibida.views import CorrespondenciaRecibidaViewSet , CorrespondenciaRecibidaAsignadaViewSet , CorrespondenciaRecibidaSoporteViewSet
from multa.views import SolicitudConsecutivoViewSet , ConjuntoEventoViewSet , EventoViewSet , SolicitudViewSet , SolicitudEmpresaViewSet , SolicitudEventoViewSet , SolicitudHistorialViewSet , SolicitudSoporteViewSet , SolicitudApelacionViewSet , SolicitudPronunciamientoViewSet

from indicadorCalidad.views import IndicadorViewSet, SeguimientoIndicadorViewSet
from informe_mme.views import InformeMMEViewSet


from avanceObraGrafico2.views import ProyectoEmpresaLiteViewSet,PeriodicidadGraficoViewSet,EsquemaCapitulosGraficoViewSet,EsquemaCapitulosActividadesGraficoViewSet,ReglaEstadoAvanceGraficoViewSet
from avanceObraGrafico2.views import CronogramaAvanceGraficoViewSet,PresupuestoAvanceGraficoViewSet,DetallePresupuestoGraficoViewSet,DiagramaGrahmGraficoViewSet
from avanceObraGrafico2.views import NodoGraficoViewSet,CantidadNodoGraficoViewSet,EnlaceAvanceGraficoViewSet,ReporteTrabajoGraficoViewSet,DetalleReporteTrabajoGraficoViewSet
from avanceObraGrafico2.views import ProyectoReporteAvanceViewSet,MensajeRechazoViewSet,CambioGraficoViewSet,DetalleCambioGraficoViewSet, MaterialesViewSet, ManoObraViewSet, DesgloceMaterialViewSet, DesgloceManoDeObraViewSet

from cesion_economica.views import CesionEconomicaViewSet
from cesion_v2.views import CesionV2ViewSet, DetalleCesionViewSet


from cronogramacontrato.views import CapituloViewSet, ActividadCViewSet, ActividadContratoViewSet, ActividadContratoResponsableViewSet, ActividadContratoSoporteViewSet
from cronogramacontrato.views import CronogramaCViewSet



from servidumbre.views import Servidumbre_grupo_documentoViewSet
from servidumbre.views import Servidumbre_expedienteViewSet
from servidumbre.views import Servidumbre_documentoViewSet
from servidumbre.views import Servidumbre_personaViewSet
from servidumbre.views import Servidumbre_predioViewSet
from servidumbre.views import Servidumbre_predio_documentoViewSet
from servidumbre.views import Servidumbre_georeferenciaViewSet

from avanceObraGrafico2.views import TipoUnidadConstructivaViewSet
from avanceObraGrafico2.views import CatalogoUnidadConstructivaViewSet
from avanceObraGrafico2.views import UnidadConstructivaAOViewSet
from avanceObraGrafico2.views import FotoNodoViewSet
from avanceObraGrafico2.views import LiquidacionUUCCViewSet

# from contrato.Integracion import Integracion_ObtenerListaContratosViewSet, Integracion_ObtenerVigenciaContratoViewSet, Integracion_ObtenerActas2ContratoViewSet, \
# Integracion_ObtenerPolizasContratoViewSet, Integracion_ObtenerVigenciasPolizaViewSet, \
# Integracion_ObtenerEncabezadoGiroViewSet, Integracion_ObtenerGirosContratoViewSet, \
# Integracion_ObtenerFinancieroCuentaViewSet,Integracion_ObtenerFinancieroCuentaMovimientoViewSet, Integracion_ObtenerFinancieroCuentaExtractosViewSet, \
# Integracion_ObtenerProyectoViewSet,Integracion_ObtenerProyectoInformacionTecnicaViewSet, \
# Integracion_ObtenerProcesoInformeEstadoViewSet, \
# Integracion_ObtenerGestionProyectoViewSet, ProyectoEmpresaLite2ViewSet

from acta_reunion.views import ConsecutivoViewSet,TemaViewSet,ActaViewSet,Acta_historialViewSet,Participante_externoViewSet,Participante_internoViewSet,CompromisoViewSet,Compromiso_historialViewSet,NoParticipantesViewSet
from django.contrib import admin

admin.autodiscover()
admin.site.site_header = 'Administracion Sinin'
router =  routers.DefaultRouter()
router.register(r'empresa', EmpresaViewSet)
# empresas que puede ver una empresa
router.register(r'empresaAcceso', EmpresaAccesoViewSet)
router.register(r'empresaCuenta', EmpresaCuentaViewSet)

router.register(r'persona', PersonaViewSet)
router.register(r'usuario', UsuarioViewSet)
router.register(r'departamento', DepartamentoViewSet)
router.register(r'Municipio', MunicipioViewSet)
router.register(r'Banco', BancoViewSet)
router.register(r'Cargo', CargoViewSet)
router.register(r'Funcionario', FuncionarioViewSet)
router.register(r'Empleado', EmpleadoViewSet)
router.register(r'Transacciones', TransaccionesViewSet)

router.register(r'Contrato', ContratoViewSet)
router.register(r'Vigencia_contrato', Vigencia_contratoViewSet)
router.register(r'Empresa_contrato', Empresa_contratoViewSet)
router.register(r'Proyecto', ProyectoViewSet)# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 24-10-2016
router.register(r'Proyecto_fondos', ProyectoFondoViewSet)
router.register(r'Proyecto_tipos', P_tipoViewSet)# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 09-11-2016
router.register(r'Proyecto_empresas', ProyectoEmpresaViewSet)# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 09-11-2016
router.register(r'Proyecto_campo_info_tecnica', ProyectoCampoInfoTecnicaViewSet)# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 09-11-2016
router.register(r'Proyecto_info_tecnica', ProyectoInfoTecnicaViewSet)# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 09-11-2016
router.register(r'Proyecto_actividades', ProyectoActividadesViewSet)
router.register(r'Rubro', RubroViewSet)
router.register(r'Sub_contratista', Sub_contratistaViewSet)
router.register(r'Contrato_cesion', Contrato_cesionViewSet)
router.register(r'Cesion_economica', Cesion_economicaViewSet)
#router.register(r'Cuenta', CuentaViewSet)# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 24-10-2016
#router.register(r'Cuenta_movimiento', CuentaMovimientoViewSet)# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 24-10-2016

router.register(r'Tipos', TipoViewSet)# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 04-11-2016
router.register(r'Estados', EstadoViewSet)# CREADO : LUIS ALBERTO MENDOZA HERNANDEZ  MODIFICADO : 04-11-2016
router.register(r'EstadosPosibles', EstadosPosiblesViewSet)
router.register(r'opcion', OpcionViewSet)
router.register(r'opcion_usuario', Opcion_UsuarioViewSet)
router.register(r'matricula',MatriculaViewSet)
router.register(r'escolaridad',EscolaridadViewSet)
router.register(r'empleado',EmpleadoViewSet)

router.register(r'ubicacion', UbicacionViewSet)

router.register(r'Nombre_giro', NombreGiroViewSet)
router.register(r'Encabezado_giro', EncabezadoGiroViewSet)
router.register(r'Detalle_giro', DetalleGiroViewSet)
router.register(r'Rechazo_giro', RechazoGiroViewSet)


router.register(r'Novedad', NovedadViewSet)
router.register(r'Planilla', PlanillaViewSet)
router.register(r'CargosSeguridadSocial',CargoSeguridadSocialViewSet)
router.register(r'PlanillaEmpleado',PlanillaEmpleadoViewSet)

router.register(r'CorrespondenciaPantillas', CorrespondenciaPlantillaViewSet)
router.register(r'CorrespondenciaPrefijo', CorresPfijoViewSet)
router.register(r'CorrespondenciaRadicado', CorrespondenciaRadicadoViewSet)
router.register(r'CorrespondenciaConsecutivo', CorrespondenciaConsecutivoViewSet)
router.register(r'CorrespondenciaRecibida', CorrespondenciaRecibidaViewSet)
router.register(r'CorrespondenciaRecibidaAsignada', CorrespondenciaRecibidaAsignadaViewSet)
router.register(r'CorrespondenciaRecibidaSoporte', CorrespondenciaRecibidaSoporteViewSet)
router.register(r'CorrespondenciaEnviada', CorrespondenciaEnviadaViewSet)
router.register(r'CorrespondenciaSoporte', CorrespondenciaSoporteViewSet)

router.register(r'CronogramaCcontrato', CronogramaCViewSet)
router.register(r'CCapitulo', CapituloViewSet)
router.register(r'CActividad', ActividadCViewSet)
router.register(r'CActividad_contrato', ActividadContratoViewSet)
router.register(r'CActividad_contrato_soporte', ActividadContratoSoporteViewSet)
router.register(r'CActividad_contrato_responsable', ActividadContratoResponsableViewSet)


router.register(r'Financiero_cuenta', FinancieroCuentaViewSet)
router.register(r'Financiero_cuenta_movimiento', FinancieroCuentaMovimientoViewSet)
router.register(r'Financiero_extracto', ExtractoCuentaViewSet)

router.register(r'Correo_descargo', CorreoDescargoViewSet)
router.register(r'Idinterno_descargo', AIdInternoDescargoViewSet)
router.register(r'Maniobra', ManiobraViewSet)
router.register(r'MotivoSgi', MotivoSgiViewSet)
router.register(r'MotivoInterventor', MotivoInterventorViewSet)
router.register(r'DescargoTrabajo', DescargoTrabajoViewSet)
router.register(r'Descargo', DescargoViewSet)
router.register(r'FotoDescargo', FotoDescargoViewSet)


router.register(r'MiNubeArchivo', ArchivoViewSet)
router.register(r'MiNubeArchivoUsuario', ArchivoUsuarioViewSet)
router.register(r'Periodicidad', PeriodicidadViewSet)
router.register(r'Cronograma', CronogramaViewSet)
router.register(r'Intervalo_Cronograma', IntervaloCronogramaViewSet)
router.register(r'Comentario_avance_obra', ComentarioViewSet)
router.register(r'Actividad_avance_obra', ActividadViewSet)
router.register(r'Linea_avance_obra', LineaViewSet)
router.register(r'Meta_avance_obra', MetaViewSet)
router.register(r'Porcentaje_avance_obra', PorcentajeViewSet)
router.register(r'Soporte_avance_obra', AvanceObraSoporteViewSet)
router.register(r'Esquema_Capitulos_avance_obra', EsquemaCapitulosViewSet)
router.register(r'Esquema_Capitulos_Actividades_avance_obra', EsquemaCapitulosActividadesViewSet)
router.register(r'Regla_Estado_avance_obra', ReglaEstadoViewSet)

router.register(r'categoria', CategoriaViewSet)
router.register(r'subcategoria', SubcategoriaViewSet)
router.register(r'fotos_proyecto', FotosProyectoViewSet)
router.register(r'fotos_subcategoria', FotosSubcategoriaViewSet)
router.register(r'Proyecto_empresas_lite', ProyectoEmpresaLiteViewSet)

router.register(r'Aseguradora', AseguradoraViewSet)
router.register(r'Poliza', PolizaViewSet)
router.register(r'VigenciaPoliza', VigenciaPolizaViewSet)
router.register(r'Puntos_gps', PuntosGpsViewSet)


router.register(r'Procesos', ProcesoViewSet)
router.register(r'Items', ItemViewSet)
router.register(r'ItemsPorEmpresa', PermisoEmpresaItemViewSet)
router.register(r'ItemsVinculados', VinculoViewSet)
router.register(r'procesoRelacion', ProcesoRelacionViewSet)
router.register(r'procesoRelacionDato', ProcesoRelacionDatoViewSet)
router.register(r'soporteProcesoRelacionDato', SoporteProcesoRelacionDatoViewSet)
router.register(r'NotificacionVencimiento', NotificacionVencimientoViewSet)


router.register(r'Factura', FacturaViewSet)
router.register(r'FacturaMesCausado', MesCausadoViewSet)
router.register(r'FecturaCesion', CesionViewSet)
router.register(r'FacturaDescuento', DescuentoViewSet)
router.register(r'FacturaCompensacion', CompensacionViewSet)
router.register(r'FacturaDetalleCompensacion', DetalleCompensacionViewSet)
router.register(r'FacturaProyecto', FacturaProyectoViewSet)

router.register(r'ConfiguracionPorcentajes', ConfiguracionPorcentajesViewSet)
router.register(r'ProyectosNotificados', ProyectosNotificadosViewSet)
router.register(r'Retie', RetieViewSet)
router.register(r'AsistenteVisita', AsistenteVisitaViewSet)
router.register(r'HistorialVisita', HistorialViewSet)
router.register(r'NoConformidad', NoConformidadRetieViewSet)
router.register(r'NotificarCorreo', NotificarCorreoViewSet)

router.register(r'Notificacion', NotificacionViewSet)
router.register(r'Responsabilidades', ResponsabilidadesViewSet)

router.register(r'EquipoTarea', EquipoViewSet)
router.register(r'ColaboradorTarea', ColaboradorViewSet)
router.register(r'Tarea', TareaViewSet)
router.register(r'AsignacionTarea', AsignacionTareaViewSet)
router.register(r'SoporteAsignacionTarea', SoporteAsignacionTareaViewSet)
router.register(r'TareaActividad', TareaActividadViewSet)
router.register(r'TareaComentario', TareaComentarioViewSet)
router.register(r'TareaActividadSoporte', TareaActividadSoporteViewSet)

router.register(r'GestionProyectoFondo', FondoViewSet)
router.register(r'GestionProyectoCampana', CampanaViewSet)
router.register(r'GestionProyectoSolicitante', SolicitanteViewSet)
router.register(r'GestionProyectoUnidadMedida', UnidadMedidaViewSet)
router.register(r'GestionProyectoCampanaEmpresa', CampanaEmpresaViewSet)
router.register(r'GestionProyectoSolicitud', SolicitudDisenoViewSet)
router.register(r'GestionProyectoDatoDiseno', DatoDisenoViewSet)
router.register(r'GestionProyectoDiseno', DisenoViewSet)
router.register(r'GestionProyectoDocumentoEstado', DocumentoEstadoViewSet)
router.register(r'GestionProyectoEstadoDiseno', EstadoDisenoViewSet)
router.register(r'GestionProyectoInfoDiseno', InfoDisenoViewSet)
router.register(r'GestionProyectoMapaDiseno', MapaDisenoViewSet)
router.register(r'GestionProyectoPermisoDiseno', PermisoDisenoViewSet)
router.register(r'GestionProyectoSoporteEstado', SoporteEstadoViewSet)
router.register(r'GestionProyectoSoporteEstadoComentario', SoporteEstadoComentarioViewSet)
router.register(r'GestionProyectoSoporteSolicitud', SoporteSolicitudViewSet)
router.register(r'GestionProyectoComentarioDiseno', ComentarioDisenoViewSet)
router.register(r'GestionProyectoVersionesDiseno', VersionDisenoViewSet)



router.register(r'MultaSolicitudConsecutivo', SolicitudConsecutivoViewSet)
router.register(r'MultaConjuntoEvento', ConjuntoEventoViewSet)
router.register(r'MultaEvento', EventoViewSet)
router.register(r'MultaSolicitud', SolicitudViewSet)
router.register(r'MultaSolicitudSoporte', SolicitudSoporteViewSet)
router.register(r'MultaSolicitudEmpresa', SolicitudEmpresaViewSet)
router.register(r'MultaSolicitudEvento', SolicitudEventoViewSet)
router.register(r'MultaSolicitudHistorial', SolicitudHistorialViewSet)
router.register(r'MultaSolicitudApelacion', SolicitudApelacionViewSet)
router.register(r'MultaSolicitudPronunciamiento', SolicitudPronunciamientoViewSet)


router.register(r'InformePlanilla', InformePlanillaViewSet)
router.register(r'InformeTag', TagViewSet)

router.register(r'gestion_op', GestionOpViewSet)

router.register(r'SistemaVersion', SistemaVersionViewSet)
router.register(r'InformacionArchivos', InformacionArchivosViewSet)

router.register(r'Solicitud', SolicitudContratoViewSet)
router.register(r'SolicitudRequisitoJuridico', RequisitoJuridicoViewSet)
router.register(r'SolicitudRequisitoCompras', RequisitoComprasViewSet)
router.register(r'SolicitudRequisitoTecnico', RequisitoTecnicoViewSet)
router.register(r'SolicitudRequisitoPoliza', RequisitoPolizaViewSet)
router.register(r'SolicitudFavorabilidadJuridica', FavorabilidadJuridicaViewSet)
router.register(r'SolicitudFavorabilidadCompras', FavorabilidadComprasViewSet)
router.register(r'SolicitudFavorabilidadTecnica', FavorabilidadTecnicaViewSet)
router.register(r'SolicitudValidarPoliza', ValidarPolizaViewSet)
router.register(r'SolicitudPolizaTipo', PolizaTipoViewSet)
router.register(r'SolicitudFavorabilidadJuridicaRequisito', FavorabilidadJuridicaRequisitoViewSet)
router.register(r'SolicitudFavorabilidadComprasRequisito', FavorabilidadComprasRequisitoViewSet)
router.register(r'SolicitudFavorabilidadTecnicaRequisito', FavorabilidadTecnicaRequisitoViewSet)
router.register(r'SolicitudPolizaTipoRequisito', PolizaTipoRequisitoViewSet)

router.register(r'CorreoContratista', CorreoContratistaViewSet)

router.register(r'Encabezado_solicitud_giro', EncabezadoSolicitudGiroViewSet)
router.register(r'Detalle_giro_solicitud_giro', DetalleGiroSolicitudGiroViewSet)

router.register(r'Solicita', SolicitaViewSet)
router.register(r'Unidad_contructiva', UnidadConstructivaViewSet)
router.register(r'Cambio', CambioViewSet)
router.register(r'Material', MaterialViewSet)
router.register(r'Uucc_material', UUCCMaterialViewSet)
router.register(r'Cambio_proyecto', CambioProyectoViewSet)
router.register(r'Soporte_cambio', SoporteViewSet)
router.register(r'solicitudServicioArea', AreaViewSet)
router.register(r'solicitudServicioSolicitud', SolicitudServicioViewSet)

router.register(r'solicitudServicioSoporte', SoporteSolicitudViewSet)
router.register(r'bitacora', BitacoraViewSet)
router.register(r'no_conformidad', NoConformidadViewSet)
from . import views

router.register(r'Lote', LoteViewSet)
router.register(r'Propietario', PropietarioViewSet)
router.register(r'SoporteReunion', SoporteReunionViewSet)
router.register(r'Estructura', EstructurasViewSet)
router.register(r'PropietarioLote', PropietarioLoteViewSet)

router.register(r'avanceObraGraficoPerioricidad', PeriodicidadGViewSet)
router.register(r'avanceObraGraficoEsquemaCapitulos', EsquemaCapitulosGViewSet)
router.register(r'avanceObraGraficoEsquemaCapitulosActividades', EsquemaCapitulosActividadesGViewSet)
router.register(r'avanceObraGraficoPresupuesto', PresupuestoViewSet)
router.register(r'avanceObraGraficoDetallePresupuesto', DetallePresupuestoViewSet)
router.register(r'avanceObraGraficoNodo', NodoViewSet)
router.register(r'avanceObraGraficoCantidadNodo', CantidadNodoViewSet)
router.register(r'avanceObraGraficoCronograma', CronogramaGraficoViewSet)
router.register(r'avanceObraGraficoLinea', LineaGraficoViewSet)
router.register(r'avanceObraGraficoEnlace', EnlaceGraficoViewSet)
router.register(r'avanceObraGraficoCambio', CambioAvanceViewSet)
router.register(r'avanceObraGraficoEstadoCambio', EstadoCambioAvanceViewSet)
router.register(r'avanceObraGraficoReglaEstado', ReglaEstadoGraficoViewSet)
router.register(r'avanceObraGraficoDiagramaGrahm', DiagramaGrahmViewSet)
router.register(r'avanceObraGraficoEjecucionProgramada', EjecucionProgramadaViewSet)

router.register(r'Indicadores', IndicadorViewSet)
router.register(r'SeguimientoIndicador', SeguimientoIndicadorViewSet)
router.register(r'avanceGrafico2Perioricidad', PeriodicidadGraficoViewSet)
router.register(r'avanceGrafico2EsquemaCapitulos', EsquemaCapitulosGraficoViewSet)
router.register(r'avanceGrafico2EsquemaCapitulosActividades', EsquemaCapitulosActividadesGraficoViewSet)
router.register(r'avanceGrafico2ReglaEstado', ReglaEstadoAvanceGraficoViewSet)
router.register(r'avanceGrafico2Cronograma', CronogramaAvanceGraficoViewSet)
router.register(r'avanceGrafico2Presupuesto', PresupuestoAvanceGraficoViewSet)
router.register(r'avanceGrafico2DetallePresupuesto', DetallePresupuestoGraficoViewSet)
router.register(r'avanceGraficoD2iagramaGrahm', DiagramaGrahmGraficoViewSet)
router.register(r'avanceGrafico2Nodo', NodoGraficoViewSet)
router.register(r'avanceGrafico2CantidadNodo', CantidadNodoGraficoViewSet)
router.register(r'avanceGrafico2Enlace', EnlaceAvanceGraficoViewSet)
router.register(r'avanceGrafico2ReporteTrabajo', ReporteTrabajoGraficoViewSet)
router.register(r'avanceGrafico2DetalleReporteTrabajo', DetalleReporteTrabajoGraficoViewSet)
router.register(r'avanceGrafico2ProyectoReporte', ProyectoReporteAvanceViewSet)
router.register(r'avanceGrafico2MensajeRechazoReporte', MensajeRechazoViewSet)
router.register(r'avanceGrafico2Cambio', CambioGraficoViewSet)
router.register(r'avanceGrafico2DetalleCambio', DetalleCambioGraficoViewSet)
router.register(r'liquidacionuucc',LiquidacionUUCCViewSet)

router.register(r'Informemme', InformeMMEViewSet)
router.register(r'CesionEconomica', CesionEconomicaViewSet)
router.register(r'contratistaContratoInforme', ContratistaContratoViewSet)
router.register(r'CesionV2', CesionV2ViewSet)
router.register(r'DetalleCesion', DetalleCesionViewSet)


router.register(r'servidumbregrupodocumento', Servidumbre_grupo_documentoViewSet)
router.register(r'servidumbredocumento', Servidumbre_documentoViewSet)
router.register(r'servidumbreexpediente', Servidumbre_expedienteViewSet)
router.register(r'servidumbrepersona', Servidumbre_personaViewSet)
router.register(r'servidumbrepredio', Servidumbre_predioViewSet)
router.register(r'servidumbreprediodocumento', Servidumbre_predio_documentoViewSet)
router.register(r'servidumbregeoreferencia',Servidumbre_georeferenciaViewSet)

router.register(r'actaasignacionrecursoscontrato',ActaAsignacionRecursosContratoViewSet)

router.register(r'tipounidadconstructiva',TipoUnidadConstructivaViewSet)
router.register(r'catalogounidadconstructiva',CatalogoUnidadConstructivaViewSet)
router.register(r'unidadconstructiva',UnidadConstructivaAOViewSet)
router.register(r'materiales',MaterialesViewSet)
router.register(r'mano-obra',ManoObraViewSet)
router.register(r'desgl-mat',DesgloceMaterialViewSet)
router.register(r'desgl-mo',DesgloceManoDeObraViewSet)
router.register(r'fotonodo',FotoNodoViewSet)


# #INTEGRACION CON SISTEMA SYSPOTEC
# router.register(r'integracion-obtenerlistacontratos', Integracion_ObtenerListaContratosViewSet)#Servicio 1
# router.register(r'integracion-obtenervigenciacontrato',Integracion_ObtenerVigenciaContratoViewSet)#Servicio 2
# router.register(r'integracion-obteneractas2contrato', Integracion_ObtenerActas2ContratoViewSet)#Servicio 3
# router.register(r'integracion-obtenerpolizascontrato',Integracion_ObtenerPolizasContratoViewSet)#Servicio 4
# router.register(r'integracion-obtenervigenciaspolizascontrato',Integracion_ObtenerVigenciasPolizaViewSet)#Servicio 5
# router.register(r'integracion-obtenerencabezadogiro',Integracion_ObtenerEncabezadoGiroViewSet)#Servicio 6
# router.register(r'integracion-obtenergiroscontrato', Integracion_ObtenerGirosContratoViewSet)#Servicio 7
# router.register(r'integracion-obtenerfinancierocuenta', Integracion_ObtenerFinancieroCuentaViewSet)#Servicio 8
# router.register(r'integracion-obtenerfinancierocuentaMovimiento', Integracion_ObtenerFinancieroCuentaMovimientoViewSet)#Servicio 9
# router.register(r'integracion-obtenerfinancierocuentaExtractos', Integracion_ObtenerFinancieroCuentaExtractosViewSet)#Servicio 10
# router.register(r'integracion-obtenerproyecto', Integracion_ObtenerProyectoViewSet)#Servicio 11
# router.register(r'integracion-obtenerproyectoinformaciontecnica', Integracion_ObtenerProyectoInformacionTecnicaViewSet)#Servicio 12
# router.register(r'integracion-obtenerprocesoinformeEstado', Integracion_ObtenerProcesoInformeEstadoViewSet)#Servicio 13
# router.register(r'integracion-avanceobra', ProyectoEmpresaLite2ViewSet)#Servicio 14
# router.register(r'integracion-obtenergestionproyecto', Integracion_ObtenerGestionProyectoViewSet)#Servicio 15


#APIS ACTA_REUNION

router.register(r'actareunion-consecutivo', ConsecutivoViewSet)
router.register(r'actareunion-tema', TemaViewSet)
router.register(r'actareunion-acta', ActaViewSet)
router.register(r'actareunion-actahistorial', Acta_historialViewSet)
router.register(r'actareunion-participanteexterno', Participante_externoViewSet)
router.register(r'actareunion-participanteinterno', Participante_internoViewSet)
router.register(r'actareunion-compromiso', CompromisoViewSet)
router.register(r'actareunion-compromisohistorial', Compromiso_historialViewSet)
router.register(r'actareunion-noparticipantes', NoParticipantesViewSet)


from activos.views import CategoriaViewSet, Tipo_ActivoViewSet, ActivoViewSet, AtributoViewSet, Activo_atributoViewSet, Activo_atributo_soporteViewSet, Activo_personaViewSet, MotivoViewSet, Puntos_gpsViewSet, MantenimientoViewSet, Soporte_mantenimientoViewSet
router.register(r'activoscategoria',CategoriaViewSet)
router.register(r'activostipo_Activo',Tipo_ActivoViewSet)
router.register(r'activosactivo',ActivoViewSet)
router.register(r'activosatributo',AtributoViewSet)
router.register(r'activosactivo_atributo',Activo_atributoViewSet)
router.register(r'activosactivo_atributo_soporte',Activo_atributo_soporteViewSet)
router.register(r'activosactivo_persona',Activo_personaViewSet)
router.register(r'activosmotivo',MotivoViewSet)
router.register(r'activospuntosgps',Puntos_gpsViewSet)
router.register(r'activosmantenimiento',MantenimientoViewSet)
router.register(r'activossoporte_mantenimiento',Soporte_mantenimientoViewSet)

from avanceObraLite.views import ProyectoEmpresaLiteViewSet,PeriodicidadGraficoViewSet,EsquemaCapitulosGraficoViewSet,EsquemaCapitulosActividadesGraficoViewSet
from avanceObraLite.views import CronogramaAvanceGraficoViewSet,PresupuestoAvanceGraficoViewSet,DetallePresupuestoGraficoViewSet, PeriodoProgramacionViewSet, DetallePeriodoProgramacionViewSet
from avanceObraLite.views import MaterialesViewSet, ManoObraViewSet, DesgloceMaterialViewSet, DesgloceManoDeObraViewSet, ReporteTrabajoGraficoViewSet, DetalleReporteTrabajoViewSet
from avanceObraLite.views import TipoUnidadConstructivaViewSet, CatalogoUnidadConstructivaViewSet, UnidadConstructivaAOViewSet, PeriodoProgramacion


router.register(r'Proyecto_empresas_lite', ProyectoEmpresaLiteViewSet)
router.register(r'avanceObraLitePerioricidad', PeriodicidadGraficoViewSet)
router.register(r'avanceObraLiteEsquemaCapitulos', EsquemaCapitulosGraficoViewSet)
router.register(r'avanceObraLiteEsquemaCapitulosActividades', EsquemaCapitulosActividadesGraficoViewSet)
router.register(r'avanceObraLiteCronograma', CronogramaAvanceGraficoViewSet)
router.register(r'avanceObraLitePeriodoProgramacion', PeriodoProgramacionViewSet)
router.register(r'avanceObraLiteDetallePeriodoProgramacion', DetallePeriodoProgramacionViewSet)
router.register(r'avanceObraLitePresupuesto', PresupuestoAvanceGraficoViewSet)
router.register(r'avanceObraLiteDetallePresupuesto', DetallePresupuestoGraficoViewSet)
router.register(r'avanceObraLiteReporteTrabajo', ReporteTrabajoGraficoViewSet)
router.register(r'avanceObraLiteDetalleReporteTrabajo', DetalleReporteTrabajoViewSet)
router.register(r'avanceObraLiteTipoUUCC',TipoUnidadConstructivaViewSet)
router.register(r'avanceObraLiteCatalogoUUCC',CatalogoUnidadConstructivaViewSet)
router.register(r'avanceObraLiteUUCC',UnidadConstructivaAOViewSet)
router.register(r'avanceObraLiteMateriales',MaterialesViewSet)
router.register(r'avanceObraLiteMano-obra',ManoObraViewSet)
router.register(r'avanceObraLiteDesgl-mat',DesgloceMaterialViewSet)
router.register(r'avanceObraLiteDesgl-mo',DesgloceManoDeObraViewSet)

from informe.views import Proyecto_ActividadViewSet, ActividadViewSet
router.register(r'actividad', ActividadViewSet)
router.register(r'proyecto_actividad', Proyecto_ActividadViewSet)

urlpatterns = [
    # path('oauth2/', include('provider.oauth2.urls', namespace = 'oauth2')),
    # path('api-token-auth/', views.obtain_auth_token),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('', views.inicio, name='sinin4.inicio'), 
    # path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    # path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    path('admin/', admin.site.urls),
    path('api/',include(router.urls)),
    path('usuario/', include('usuario.urls')),
    path('empresa/', include('empresa.urls')),
    path('opcion/', include('opcion.urls')),
    path('parametrizacion/', include('parametrizacion.urls')),
    path('giros/', include('giros.urls')),
    path('proyecto/', include('proyecto.urls')),
    path('contrato/', include('contrato.urls')),
    path('ubicacion/', include('ubicacion.urls')),
    #path('cuenta/', include('cuenta.urls')),
    path('seguridad-social/', include('seguridad_social.urls')),
    path('correspondencia/', include('correspondencia.urls')),
    path('correspondencia_recibida/', include('correspondencia_recibida.urls')),
    path('financiero/', include('financiero.urls')),
    path('miNube/', include('mi_nube.urls')),
    path('descargo/', include('descargo.urls')),
    path('avance_de_obra/', include('avance_de_obra.urls')),
    path('administrador_fotos/', include('administrador_fotos.urls')),
    path('poliza/', include('poliza.urls')),
    path('puntos_gps/', include('puntos_gps.urls')),

    path('proceso/', include('proceso.urls')),

    path('factura/', include('factura.urls')),
    path('administrador_tarea/', include('administrador_tarea.urls')),
    path('retie/', include('seguimiento_retie.urls')),
    path('gestion_proyecto/', include('gestion_proyecto.urls')),

    path('multa/', include('multa.urls')),
    path('informe/', include('informe.urls')),

    path('solicitud_giro/', include('solicitud_giro.urls')),
    path('seguimiento_factura/', include('seguimiento_factura.urls')),    
    path('deploy/', include('deploy.urls')),
    path('informe_ministerio/', include('informe_ministerio.urls')),
    path('solicitud/', include('solicitud.urls')),
    path('control_cambios/', include('control_cambios.urls')),
    path('solicitud-servicio/', include('solicitudservicio.urls')),
    path('avanceObraGrafico/', include('avanceObraGrafico.urls')),
    path('p_p_construccion/', include('p_p_construccion.urls')),
    path('bitacora/', include('bitacora.urls')),
    # path('oauth2/', include('provider.oauth2.urls', namespace = 'oauth2')),
    path('no_conformidad/', include('no_conformidad.urls')),
    path('avanceObraGrafico2/', include('avanceObraGrafico2.urls')),

    path('indicadorCalidad/', include('indicadorCalidad.urls')),
    path('informe_mme/', include('informe_mme.urls')),
    path('cesion_economica/', include('cesion_economica.urls')),
    path('cesion_v2/', include('cesion_v2.urls')),
    path('servidumbre/', include('servidumbre.urls')),
    path('balance_scorecard/', include('balance_scorecard.urls')),
    path('actareunion/', include('acta_reunion.urls')),
    path('activos/', include('activos.urls')),
    path('cronogramacontrato/', include('cronogramacontrato.urls')),
    path('avanceObraLite/', include('avanceObraLite.urls')),
        
]
#urlpatterns += patterns('',(r'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]

from sinin4 import views as sinin4_views

urlpatterns += [
    # Other url patterns ...
    path('sitio-en-construccion/', sinin4_views.sitio_construccion, name='sitio_construccion'),
]

handler404 = 'sinin4.views.error_404'
handler500 = 'sinin4.views.error_500'

