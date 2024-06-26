from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^hitos/$', views.avanceObraLite, name='avanceObraLite.hitos'),    
    url(r'^eliminar_esquema/$', views.eliminar_esquema, name='avanceObraLite.eliminar_esquema'),
    url(r'^actividades/(?P<id_esquema>[0-9]+)/$', views.actividades, name='avanceObraLite.actividad'),
    url(r'^eliminar_id_capitulo_actividad_esquema/$', views.eliminar_id_capitulo_actividad_esquema, name='avanceObraLite.eliminar_id_capitulo_actividad_esquema'),
    url(r'^clonacion_esquema/$', views.clonacion_esquema, name='avanceObraLite.clonacion_esquema'),
    url(r'^regla_estado/(?P<id_esquema>[0-9]+)/$', views.regla_estado, name='avanceObraLite.regla_estado'),    
    url(r'^eliminar_id_regla_estado/$', views.eliminar_id_regla_estado, name='avanceObraLite.eliminar_id_regla_estado'),
    url(r'^cronograma/$', views.cronograma, name='avanceObraLite.cronograma'),
    url(r'^cronograma_proyecto/(?P<id_proyecto>[0-9]+)/$', views.cronograma_proyecto, name='avanceObraLite.cronograma_proyecto'),    
    url(r'^presupuesto/(?P<id_cronograma>[0-9]+)/$', views.presupuesto, name='avanceObraLite.presupuesto'),    
    url(r'^eliminar_id_cronograma/$', views.eliminar_id_cronograma, name='avanceObraLite.eliminar_id_cronograma'),
    url(r'^detalle_presupuesto/(?P<id_presupuesto>[0-9]+)/$', views.presupuesto_detalle, name='avanceObraLite.presupuesto_detalle'),   
    url(r'^eliminar_id_presupuesto/$', views.eliminar_id_presupuesto, name='avanceObraLite.eliminar_id_presupuesto'),
    url(r'^eliminar_id_reformado/$', views.eliminar_id_reformado, name='avanceObraLite.eliminar_id_reformado'),
    url(r'^eliminar_id_reportetrabajo/$', views.eliminar_id_reportetrabajo, name='avanceObraLite.eliminar_id_reportetrabajo'),
    url(r'^descargar_plantilla_presupuesto/$', views.descargar_plantilla_presupuesto, name='avanceObraLite.descargar_plantilla_presupuesto'),
    url(r'^guardar_presupuesto_archivo/$', views.guardar_presupuesto_archivo, name='avanceObraLite.guardar_presupuesto_archivo'),
    url(r'^actualizar_cantidad/$', views.actualizar_cantidad, name='avanceObraLite.actualizar_cantidad'),
    url(r'^cierre_presupuesto/$', views.cierre_presupuesto, name='avanceObraLite.cierre_presupuesto'),
    url(r'^programacion/(?P<id_cronograma>[0-9]+)/$', views.programacion, name='avanceObraLite.programacion'),
    url(r'^eliminar_diagrama/$', views.eliminar_diagrama, name='avanceObraLite.eliminar_diagrama'),
    url(r'^informe_diagrama/$', views.informe_diagrama, name='avanceObraLite.informe_diagrama'),
    url(r'^apoyo_con_gps/(?P<id_presupuesto>[0-9]+)/$', views.apoyo_con_gps, name='avanceObraLite.apoyo_con_gps'),
    url(r'^apoyo_sin_gps/(?P<id_presupuesto>[0-9]+)/$', views.apoyo_sin_gps, name='avanceObraLite.apoyo_sin_gps'),
    url(r'^descargar_plantilla_apoyo/$', views.descargar_plantilla_apoyo, name='avanceObraLite.descargar_plantilla_apoyo'),
    url(r'^guardar_apoyo_archivo/$', views.guardar_apoyo_archivo, name='avanceObraLite.guardar_apoyo_archivo'),
    url(r'^eliminar_apoyos/$', views.eliminar_apoyos, name='avanceObraLite.eliminar_apoyos'),
    url(r'^descargar_plantilla_apoyo_sinposicion/$', views.descargar_plantilla_apoyo_sinposicion, name='avanceObraLite.descargar_plantilla_apoyo_sinposicion'),
    url(r'^guardar_apoyo_archivo_sinposicion/$', views.guardar_apoyo_archivo_sinposicion, name='avanceObraLite.guardar_apoyo_archivo_sinposicion'),
    url(r'^cantidad_apoyo/(?P<id_presupuesto>[0-9]+)/$', views.cantidad_apoyo, name='avanceObraLite.cantidad_apoyo'),
    url(r'^descargar_plantilla_cantidadApoyo/$', views.descargar_plantilla_cantidadApoyo, name='avanceObraLite.descargar_plantilla_cantidadApoyo'),
    url(r'^guardar_cantidadApoyo_archivo/$', views.guardar_cantidadApoyo_archivo, name='avanceObraLite.guardar_cantidadApoyo_archivo'),
    url(r'^informe_cantidad_apoyo/$', views.informe_cantidad_apoyo, name='avanceObraLite.informe_cantidad_apoyo'),
    url(r'^cantidad_apoyo_id/(?P<id_presupuesto>[0-9]+)/(?P<id_detalle>[0-9]+)/$', views.cantidad_apoyo_id, name='avanceObraLite.cantidad_apoyo_id'),
    url(r'^guardar_cantidad_apoyo/$', views.guardar_cantidad_apoyo, name='avanceObraLite.guardar_cantidad_apoyo'),
    url(r'^reporte_trabajo/(?P<id_cronograma>[0-9]+)/$', views.reporte_trabajo, name='avanceObraLite.reporte_trabajo'),
    url(r'^reformado/(?P<id_presupuesto>[0-9]+)/$', views.reformado, name='avanceObraLite.reformado'),
    url(r'^reformadoDetalle/(?P<id_reformado>[0-9]+)/$', views.reformadoDetalle, name='avanceObraLite.reformadoDetalle'),    
    url(r'^avance_con_gps/(?P<id_reporte>[0-9]+)/$', views.avance_con_gps, name='avanceObraLite.avance_con_gps'),
    url(r'^consultar_avance_obra/$', views.consultar_avance_obra, name='avanceObraLite.consultar_avance_obra'),
    url(r'^cambios/$', views.cambios, name='avanceObraLite.cambios'),
    url(r'^consultar_ingresos_datos/$', views.consultar_ingresos_datos, name='avanceObraLite.consultar_ingresos_datos'),
    url(r'^guardar_cambio_cantidades/$', views.guardar_cambio_cantidades, name='avanceObraLite.guardar_cambio_cantidades'),
    url(r'^guardar_cambio_detalle/$', views.guardar_cambio_detalle, name='avanceObraLite.guardar_cambio_detalle'),
    url(r'^eliminar_id_nodo_destino/$', views.eliminar_id_nodo_destino, name='avanceObraLite.eliminar_id_nodo_destino'),
    url(r'^avance_sin_gps/(?P<id_reporte>[0-9]+)/$', views.avance_sin_gps, name='avanceObraLite.avance_sin_gps'),
    url(r'^cierre_programacion/$', views.cierre_programacion, name='avanceObraLite.cierre_programacion'),
    url(r'^informe_detallepresupuesto/$', views.informe_detallepresupuesto, name='avanceObraLite.informe_detallepresupuesto'),
    url(r'^menu_gps/(?P<id_presupuesto>[0-9]+)/$', views.menu_gps, name='avanceObraLite.menu_gps'),
    url(r'^guardar_reporte_trabajo/(?P<id_reporte>[0-9]+)/$', views.guardar_reporte_trabajo, name='avanceObraLite.guardar_reporte_trabajo'),
    url(r'^aprobacion/$', views.aprobacion, name='avanceObraLite.aprobacion'),
    url(r'^corregido/$', views.corregido, name='avanceObraLite.corregido'),
    url(r'^registrado/$', views.registrado, name='avanceObraLite.registrado'),
    url(r'^reporte_trabajo_registrado/(?P<id_proyecto>[0-9]+)/$', views.reporte_trabajo_registrado, name='avanceObraLite.reporte_trabajo_registrado'),
    url(r'^detalle_registrado/(?P<id_reporte>[0-9]+)/$', views.detalle_registrado, name='avanceObraLite.detalle_registrado'),
    url(r'^guardar_archivo_aprobacion/$', views.guardar_archivo_aprobacion, name='avanceObraLite.guardar_archivo_aprobacion'),
    url(r'^guardar_rechazo_reporte/$', views.guardar_rechazo_reporte, name='avanceObraLite.guardar_rechazo_reporte'),
    url(r'^reporte_trabajo_corregido/(?P<id_proyecto>[0-9]+)/$', views.reporte_trabajo_corregido, name='avanceObraLite.reporte_trabajo_corregido'),
    url(r'^detalle_corregido/(?P<id_reporte>[0-9]+)/$', views.detalle_corregido, name='avanceObraLite.detalle_corregido'),
    url(r'^grafico/(?P<id_presupuesto>[0-9]+)/$', views.grafico, name='avanceObraLite.grafico'),
    url(r'^consultar_graficos/$', views.consultar_graficos, name='avanceObraLite.consultar_graficos'),
    url(r'^rechazados/$', views.rechazados, name='avanceObraLite.rechazados'),
    url(r'^reporte_trabajo_rechazados/(?P<id_proyecto>[0-9]+)/$', views.reporte_trabajo_rechazados, name='avanceObraLite.reporte_trabajo_rechazados'),
    url(r'^consultar_cantidad_reportes/$', views.consultar_cantidad_reportes, name='avanceObraLite.consultar_cantidad_reportes'),
    url(r'^index_cambio/(?P<id_presupuesto>[0-9]+)/$', views.index_cambio, name='avanceObraLite.index_cambio'),
    url(r'^actualizar_cancelado/$', views.actualizar_cancelado, name='avanceObraLite.actualizar_cancelado'),
    url(r'^detalle_cambio/(?P<id_cambio>[0-9]+)/$', views.detalle_cambio, name='avanceObraLite.detalle_cambio'),
    url(r'^agregar_detalle/(?P<id_cambio>[0-9]+)/$', views.agregar_detalle, name='avanceObraLite.agregar_detalle'),
    url(r'^aprobacion_cambio/$', views.aprobacion_cambio, name='avanceObraLite.aprobacion_cambio'),
    url(r'^autorizacion_cambio/$', views.autorizacion_cambio, name='avanceObraLite.autorizacion_cambio'),
    url(r'^reportar_sin_poste/$', views.reportar_sin_poste, name='avanceObraLite.reportar_sin_poste'),
    url(r'^apu/(?P<idUnidadConstructiva>[0-9]+)/$', views.get_apuUnidadConstructiva, name='avanceObraLite.apu'),
    url(r'^cantidadesnodo/(?P<nodo_id>[0-9]+)/(?P<presupuesto_id>[0-9]+)/$', 
        views.get_cantidadesDeNodo, name='avanceObraLite.cantidadesNodo'),
    # url(r'^verfoto/$', views.verFoto, name='VerSoporte'),
    url(r'^graficacronograma/(?P<id>[0-9]+)/$', views.graficaCronograma, 
        name='avanceObraLite.graficacronograma'),
    url(r'^tablero/(?P<id_mcontrato>[0-9]+)/$', views.tablero_contrato,
     name='avanceObraLite.tablero_contrato'),
    url(r'^graficatablero/(?P<id>[0-9]+)/$', views.graficasTablero, 
        name='avanceObraLite.graficasTablero'),
    url(r'^consultarcantidadesaliquidar/(?P<id>[0-9]+)/$', 
        views.cantidadesAliquidar, 
        name='avanceObraLite.cantidadesAliquidar'), 
    url(r'^seguimientocantidades/(?P<id_presupuesto>[0-9]+)/$', views.seguimientoCantidades,
     name='avanceObraLite.seguimientoCantidades'),
    # url(r'^ver-liquidacionuucc/(?P<id_presupuesto>[0-9]+)/$', views.liquidacionuucc, name='avanceObraLite.liquidacionuucc'),
    url(r'^consultar_uucc_ejecutados/$', views.consultar_uucc_ejecutados, name='avanceObraLite.consultar_uucc_ejecutados'),
    url(r'^guardar_liquidacionuucc/$', views.guardar_liquidacionuucc, name='avanceObraLite.guardar_liquidacionuucc'),
    url(r'^cerrar_liquidacionuucc/$', views.cerrar_liquidacionuucc, name='avanceObraLite.cerrar_liquidacionuucc'),
    url(r'^consultar_detallereporte_liquidacion/$', views.consultar_detallereporte_liquidacion, name='avanceObraLite.consultar_detallereporte_liquidacion'),
    url(r'^consultarcantidadesaliquidarlite/$', 
        views.cantidadesAliquidarlite, 
        name='avanceObraLite.cantidadesAliquidarlite'),
    url(r'^exportReporteLiquidacion/$', 
        views.exportReporteLiquidacion, 
        name='avanceObraLite.exportReporteLiquidacion'),
    url(r'^anularReporteLiquidacion/$', 
        views.anularReporteLiquidacion, 
        name='avanceObraLite.anularReporteLiquidacion'),
    url(r'^consultarmotivoanulacion/$', 
        views.consultarmotivoanulacion, 
        name='avanceObraLite.consultarmotivoanulacion'),
    url(r'^exportCronograma/$', 
        views.exportCronograma, 
        name='avanceObraLite.exportCronograma'),
    url(r'^seguimientomateriales/(?P<id_presupuesto>[0-9]+)/$', 
        views.seguimientoMateriales,
     name='avanceObraLite.seguimientoMateriales'),
    url(r'^consultarmaterialesaliquidarlite/(?P<id>[0-9]+)/$',
        views.materialesAliquidarlite, 
        name='avanceObraLite.materialesAliquidarlite'),
    url(r'^exportarmaterialesaliquidar/$',
        views.exportarMaterialesaLiquidar, 
        name='avanceObraLite.exportarmaterialesaliquidar'),
    url(r'^exportarcantidadesaliquidar/$',
        views.exportarCantidadesaLiquidar, 
        name='avanceObraLite.exportarCantidadesaLiquidar'),

    url(r'^descargar-plantilla-programacion/$', 
        views.descargar_plantilla_programacion, 
        name='avanceObraLite.descargar_plantilla_programacion'),

    url(r'^guardar-programacion-archivo/$', 
        views.guardar_programacion_archivo, 
        name='avanceObraLite.guardar_programacion_archivo'),


    url(r'^catalogo/$', views.catalogo, name='avanceObraLite.catalogos'),    
    url(r'^inactivar-catalogo/$', views.inactivar_catalogo, name='avanceObraLite.inactivar_catalogo'),    
    url(r'^activar-catalogo/$', views.activar_catalogo, name='avanceObraLite.activar_catalogo'),    
    url(r'^excel_catalogo/$', views.excel_catalogo, name='avanceObraLite.excel_catalogo'),    
    
    url(r'^uucc/(?P<catalogo_id>[0-9]+)/$', views.uucc, name='avanceObraLite.uucc'),        
    url(r'^eliminar_id_uucc/$', views.eliminar_id_uucc, name='avanceObraLite.eliminar_id_uucc'), 
    url(r'^excel_uucc/$', views.excel_uucc, name='avanceObraLite.excel_uucc'),    

    url(r'^materiales/(?P<catalogo_id>[0-9]+)/$', views.materiales, name='avanceObraLite.materiales'),                   
    url(r'^eliminar_id_materiales/$', views.eliminar_id_materiales, name='avanceObraLite.eliminar_id_materiales'), 
    url(r'^excel_mat/$', views.excel_mat, name='avanceObraLite.excel_mat'),    

    url(r'^mano_obra/(?P<catalogo_id>[0-9]+)/$', views.mano_obra, name='avanceObraLite.manoObra'),                   
    url(r'^eliminar_id_mano_obra/$', views.eliminar_id_mano_obra, name='avanceObraLite.eliminar_id_mano_obra'),     
    url(r'^excel_mo/$', views.excel_mo, name='avanceObraLite.excel_mo'),    

    url(r'^desgl_mat/(?P<uucc_id>[0-9]+)/$', views.desgloce_mat, name='avanceObraLite.desgl_mat'),  
    url(r'^eliminar_id_desgl_mat/$', views.eliminar_id_desgl_mat, name='avanceObraLite.eliminar_id_mano_obra'),     
    url(r'^excel_desgl_mat/$', views.excel_desgl_mat, name='avanceObraLite.excel_desgl_mat'),    

    url(r'^desgl_mo/(?P<uucc_id>[0-9]+)/$', views.desgloce_mo, name='avanceObraLite.desgl_mo'),  
    url(r'^eliminar_id_desgl_mo/$', views.eliminar_id_desgl_mo, name='avanceObraLite.eliminar_id_desgl_mo'),         
    url(r'^excel_desgl_mo/$', views.excel_desgl_mo, name='avanceObraLite.excel_desgl_mo'),    

    url(r'^descargar_plantilla_masiva/$', views.descargar_plantilla_masiva, name='avanceObraLite.descargar_plantilla_masiva'),
    url(r'^carga_masiva_catalogo/$', views.cargar_excel_catalogo_masivo, name='avanceObraLite.carga_masiva_catalogo'),

    url(r'^ActualizarPeriodoPrincipal/$', views.ActualizarPeriodoPrincipal, name='avanceObraLite.ActualizarPeriodoPrincipal'),  
    url(r'^confirmar_fechas/$', views.confirmar_fechas, name='avanceObraLite.confirmar_fechas'),

    url(r'^cerrar_reportetrabajo/$', views.cerrar_reportetrabajo, name='avanceObraLite.cerrar_reportetrabajo'),
    url(r'^cantidad_maxima_detallePresupuesto/$', views.cantidad_maxima_detallePresupuesto, name='avanceObraLite.cantidad_maxima_detallePresupuesto'),
    
    url(r'^seguimientoSemanal/$', views.seguimientoSemanal, name='avanceObraLite.seguimientoSemanal'),
    # url(r'^seguimientoDiario/$', views.seguimientoDiario, name='avanceObraLite.seguimientoDiario'),
    


    url(r'^descargar-plantilla-reporte-trabajo/$', 
        views.descargar_plantilla_reporte_trabajo, 
        name='avanceObraLite.descargar_plantilla_reporte_trabajo'),

    url(r'^guardar-reporte-archivo/$', 
        views.guardar_reporte_archivo, 
        name='avanceObraLite.guardar_reporte_archivo'),

    url(r'^seguimientoContratual/(?P<id>[0-9]+)/$', views.seguimientoContratual, 
        name='avanceObraLite.seguimientoContratual'),

    url(r'^excel-seguimiento-contractual/$', 
        views.excel_seguimiento_contractual, 
        name='avanceObraLite.excel_seguimiento_contractual'),
    
]