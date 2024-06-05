from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^hitos/$', views.avance_de_obra_grafico2, name='avance_de_obra_grafico2.hitos'),
    url(r'^eliminar_esquema/$', views.eliminar_esquema, name='avance_de_obra_grafico2.eliminar_esquema'),
    url(r'^actividades/(?P<id_esquema>[0-9]+)/$', views.actividades, name='avance_de_obra_grafico2.actividad'),
    url(r'^eliminar_id_capitulo_actividad_esquema/$', views.eliminar_id_capitulo_actividad_esquema, name='avance_de_obra_grafico2.eliminar_id_capitulo_actividad_esquema'),
    url(r'^clonacion_esquema/$', views.clonacion_esquema, name='avance_de_obra_grafico2.clonacion_esquema'),
    url(r'^regla_estado/(?P<id_esquema>[0-9]+)/$', views.regla_estado, name='avance_de_obra_grafico2.regla_estado'),    
    url(r'^eliminar_id_regla_estado/$', views.eliminar_id_regla_estado, name='avance_de_obra_grafico2.eliminar_id_regla_estado'),
    url(r'^cronograma/$', views.cronograma, name='avance_de_obra_grafico2.cronograma'),
    url(r'^cronograma_proyecto/(?P<id_proyecto>[0-9]+)/$', views.cronograma_proyecto, name='avance_de_obra_grafico2.cronograma_proyecto'),    
    url(r'^presupuesto/(?P<id_cronograma>[0-9]+)/$', views.presupuesto, name='avance_de_obra_grafico2.presupuesto'),    
    url(r'^eliminar_id_cronograma/$', views.eliminar_id_cronograma, name='avance_de_obra_grafico2.eliminar_id_cronograma'),
    url(r'^detalle_presupuesto/(?P<id_presupuesto>[0-9]+)/$', views.presupuesto_detalle, name='avance_de_obra_grafico2.presupuesto_detalle'),   
    url(r'^eliminar_id_presupuesto/$', views.eliminar_id_presupuesto, name='avance_de_obra_grafico2.eliminar_id_presupuesto'),
    url(r'^eliminar_id_reformado/$', views.eliminar_id_reformado, name='avance_de_obra_grafico2.eliminar_id_reformado'),
    url(r'^eliminar_id_reportetrabajo/$', views.eliminar_id_reportetrabajo, name='avance_de_obra_grafico2.eliminar_id_reportetrabajo'),
    url(r'^descargar_plantilla_presupuesto/$', views.descargar_plantilla_presupuesto, name='avance_de_obra_grafico2.descargar_plantilla_presupuesto'),
    url(r'^guardar_presupuesto_archivo/$', views.guardar_presupuesto_archivo, name='avance_de_obra_grafico2.guardar_presupuesto_archivo'),
    url(r'^actualizar_cantidad/$', views.actualizar_cantidad, name='avance_de_obra_grafico2.actualizar_cantidad'),
    url(r'^cierre_presupuesto/$', views.cierre_presupuesto, name='avance_de_obra_grafico2.cierre_presupuesto'),
    url(r'^programacion/(?P<id_cronograma>[0-9]+)/$', views.programacion, name='avance_de_obra_grafico2.programacion'),
    url(r'^eliminar_diagrama/$', views.eliminar_diagrama, name='avance_de_obra_grafico2.eliminar_diagrama'),
    url(r'^informe_diagrama/$', views.informe_diagrama, name='avance_de_obra_grafico2.informe_diagrama'),
    url(r'^apoyo_con_gps/(?P<id_presupuesto>[0-9]+)/$', views.apoyo_con_gps, name='avance_de_obra_grafico2.apoyo_con_gps'),
    url(r'^apoyo_sin_gps/(?P<id_presupuesto>[0-9]+)/$', views.apoyo_sin_gps, name='avance_de_obra_grafico2.apoyo_sin_gps'),
    url(r'^descargar_plantilla_apoyo/$', views.descargar_plantilla_apoyo, name='avance_de_obra_grafico2.descargar_plantilla_apoyo'),
    url(r'^guardar_apoyo_archivo/$', views.guardar_apoyo_archivo, name='avance_de_obra_grafico2.guardar_apoyo_archivo'),
    url(r'^eliminar_apoyos/$', views.eliminar_apoyos, name='avance_de_obra_grafico2.eliminar_apoyos'),
    url(r'^descargar_plantilla_apoyo_sinposicion/$', views.descargar_plantilla_apoyo_sinposicion, name='avance_de_obra_grafico2.descargar_plantilla_apoyo_sinposicion'),
    url(r'^guardar_apoyo_archivo_sinposicion/$', views.guardar_apoyo_archivo_sinposicion, name='avance_de_obra_grafico2.guardar_apoyo_archivo_sinposicion'),
    url(r'^cantidad_apoyo/(?P<id_presupuesto>[0-9]+)/$', views.cantidad_apoyo, name='avance_de_obra_grafico2.cantidad_apoyo'),
    url(r'^descargar_plantilla_cantidadApoyo/$', views.descargar_plantilla_cantidadApoyo, name='avance_de_obra_grafico2.descargar_plantilla_cantidadApoyo'),
    url(r'^guardar_cantidadApoyo_archivo/$', views.guardar_cantidadApoyo_archivo, name='avance_de_obra_grafico2.guardar_cantidadApoyo_archivo'),
    url(r'^informe_cantidad_apoyo/$', views.informe_cantidad_apoyo, name='avance_de_obra_grafico2.informe_cantidad_apoyo'),
    url(r'^cantidad_apoyo_id/(?P<id_presupuesto>[0-9]+)/(?P<id_detalle>[0-9]+)/$', views.cantidad_apoyo_id, name='avance_de_obra_grafico2.cantidad_apoyo_id'),
    url(r'^guardar_cantidad_apoyo/$', views.guardar_cantidad_apoyo, name='avance_de_obra_grafico2.guardar_cantidad_apoyo'),
    url(r'^reporte_trabajo/(?P<id_presupuesto>[0-9]+)/$', views.reporte_trabajo, name='avance_de_obra_grafico2.reporte_trabajo'),
    url(r'^reformado/(?P<id_presupuesto>[0-9]+)/$', views.reformado, name='avance_de_obra_grafico2.reformado'),
    url(r'^reformadoDetalle/(?P<id_reformado>[0-9]+)/$', views.reformadoDetalle, name='avance_de_obra_grafico2.reformadoDetalle'),    
    url(r'^avance_con_gps/(?P<id_reporte>[0-9]+)/$', views.avance_con_gps, name='avance_de_obra_grafico2.avance_con_gps'),
    url(r'^consultar_avance_obra/$', views.consultar_avance_obra, name='avance_de_obra_grafico2.consultar_avance_obra'),
    url(r'^cambios/$', views.cambios, name='avance_de_obra_grafico2.cambios'),
    url(r'^consultar_ingresos_datos/$', views.consultar_ingresos_datos, name='avance_de_obra_grafico2.consultar_ingresos_datos'),
    url(r'^guardar_cambio_cantidades/$', views.guardar_cambio_cantidades, name='avance_de_obra_grafico2.guardar_cambio_cantidades'),
    url(r'^guardar_cambio_detalle/$', views.guardar_cambio_detalle, name='avance_de_obra_grafico2.guardar_cambio_detalle'),
    url(r'^eliminar_id_nodo_destino/$', views.eliminar_id_nodo_destino, name='avance_de_obra_grafico2.eliminar_id_nodo_destino'),
    url(r'^avance_sin_gps/(?P<id_reporte>[0-9]+)/$', views.avance_sin_gps, name='avance_de_obra_grafico2.avance_sin_gps'),
    url(r'^cierre_programacion/$', views.cierre_programacion, name='avance_de_obra_grafico2.cierre_programacion'),
    url(r'^informe_detallepresupuesto/$', views.informe_detallepresupuesto, name='avance_de_obra_grafico2.informe_detallepresupuesto'),
    url(r'^menu_gps/(?P<id_presupuesto>[0-9]+)/$', views.menu_gps, name='avance_de_obra_grafico2.menu_gps'),
    url(r'^guardar_reporte_trabajo/(?P<id_reporte>[0-9]+)/$', views.guardar_reporte_trabajo, name='avance_de_obra_grafico2.guardar_reporte_trabajo'),
    url(r'^aprobacion/$', views.aprobacion, name='avance_de_obra_grafico2.aprobacion'),
    url(r'^corregido/$', views.corregido, name='avance_de_obra_grafico2.corregido'),
    url(r'^registrado/$', views.registrado, name='avance_de_obra_grafico2.registrado'),
    url(r'^reporte_trabajo_registrado/(?P<id_proyecto>[0-9]+)/$', views.reporte_trabajo_registrado, name='avance_de_obra_grafico2.reporte_trabajo_registrado'),
    url(r'^detalle_registrado/(?P<id_reporte>[0-9]+)/$', views.detalle_registrado, name='avance_de_obra_grafico2.detalle_registrado'),
    url(r'^guardar_archivo_aprobacion/$', views.guardar_archivo_aprobacion, name='avance_de_obra_grafico2.guardar_archivo_aprobacion'),
    url(r'^guardar_rechazo_reporte/$', views.guardar_rechazo_reporte, name='avance_de_obra_grafico2.guardar_rechazo_reporte'),
    url(r'^reporte_trabajo_corregido/(?P<id_proyecto>[0-9]+)/$', views.reporte_trabajo_corregido, name='avance_de_obra_grafico2.reporte_trabajo_corregido'),
    url(r'^detalle_corregido/(?P<id_reporte>[0-9]+)/$', views.detalle_corregido, name='avance_de_obra_grafico2.detalle_corregido'),
    url(r'^grafico/(?P<id_presupuesto>[0-9]+)/$', views.grafico, name='avance_de_obra_grafico2.grafico'),
    url(r'^consultar_graficos/$', views.consultar_graficos, name='avance_de_obra_grafico2.consultar_graficos'),
    url(r'^rechazados/$', views.rechazados, name='avance_de_obra_grafico2.rechazados'),
    url(r'^reporte_trabajo_rechazados/(?P<id_proyecto>[0-9]+)/$', views.reporte_trabajo_rechazados, name='avance_de_obra_grafico2.reporte_trabajo_rechazados'),
    url(r'^consultar_cantidad_reportes/$', views.consultar_cantidad_reportes, name='avance_de_obra_grafico2.consultar_cantidad_reportes'),
    url(r'^index_cambio/(?P<id_presupuesto>[0-9]+)/$', views.index_cambio, name='avance_de_obra_grafico2.index_cambio'),
    url(r'^actualizar_cancelado/$', views.actualizar_cancelado, name='avance_de_obra_grafico2.actualizar_cancelado'),
    url(r'^detalle_cambio/(?P<id_cambio>[0-9]+)/$', views.detalle_cambio, name='avance_de_obra_grafico2.detalle_cambio'),
    url(r'^agregar_detalle/(?P<id_cambio>[0-9]+)/$', views.agregar_detalle, name='avance_de_obra_grafico2.agregar_detalle'),
    url(r'^aprobacion_cambio/$', views.aprobacion_cambio, name='avance_de_obra_grafico2.aprobacion_cambio'),
    url(r'^autorizacion_cambio/$', views.autorizacion_cambio, name='avance_de_obra_grafico2.autorizacion_cambio'),
    url(r'^reportar_sin_poste/$', views.reportar_sin_poste, name='avance_de_obra_grafico2.reportar_sin_poste'),
    url(r'^apu/(?P<idUnidadConstructiva>[0-9]+)/$', views.get_apuUnidadConstructiva, name='avance_de_obra_grafico2.apu'),
    url(r'^cantidadesnodo/(?P<nodo_id>[0-9]+)/(?P<presupuesto_id>[0-9]+)/$', 
        views.get_cantidadesDeNodo, name='avance_de_obra_grafico2.cantidadesNodo'),
    url(r'^verfoto/$', views.verFoto, name='VerSoporte'),
    url(r'^graficacronograma/(?P<id>[0-9]+)/$', views.graficaCronograma, 
        name='avance_de_obra_grafico2.graficacronograma'),
    url(r'^tablero/(?P<id_mcontrato>[0-9]+)/$', views.tablero_contrato,
     name='avance_de_obra_grafico2.tablero_contrato'),
    url(r'^graficatablero/(?P<id>[0-9]+)/$', views.graficasTablero, 
        name='avance_de_obra_grafico2.graficasTablero'),
    url(r'^consultarcantidadesaliquidar/(?P<id>[0-9]+)/$', 
        views.cantidadesAliquidar, 
        name='avance_de_obra_grafico2.cantidadesAliquidar'), 
    url(r'^seguimientocantidades/(?P<id_presupuesto>[0-9]+)/$', views.seguimientoCantidades,
     name='avance_de_obra_grafico2.seguimientoCantidades'),
    url(r'^ver-liquidacionuucc/(?P<id_presupuesto>[0-9]+)/$', views.liquidacionuucc, name='avance_de_obra_grafico2.liquidacionuucc'),
    url(r'^consultar_uucc_ejecutados/$', views.consultar_uucc_ejecutados, name='avance_de_obra_grafico2.consultar_uucc_ejecutados'),
    url(r'^guardar_liquidacionuucc/$', views.guardar_liquidacionuucc, name='avance_de_obra_grafico2.guardar_liquidacionuucc'),
    url(r'^cerrar_liquidacionuucc/$', views.cerrar_liquidacionuucc, name='avance_de_obra_grafico2.cerrar_liquidacionuucc'),
    url(r'^consultar_detallereporte_liquidacion/$', views.consultar_detallereporte_liquidacion, name='avance_de_obra_grafico2.consultar_detallereporte_liquidacion'),
    url(r'^consultarcantidadesaliquidarlite/$', 
        views.cantidadesAliquidarlite, 
        name='avance_de_obra_grafico2.cantidadesAliquidarlite'),
    url(r'^exportReporteLiquidacion/$', 
        views.exportReporteLiquidacion, 
        name='avance_de_obra_grafico2.exportReporteLiquidacion'),
    url(r'^anularReporteLiquidacion/$', 
        views.anularReporteLiquidacion, 
        name='avance_de_obra_grafico2.anularReporteLiquidacion'),
    url(r'^consultarmotivoanulacion/$', 
        views.consultarmotivoanulacion, 
        name='avance_de_obra_grafico2.consultarmotivoanulacion'),
    url(r'^exportCronograma/$', 
        views.exportCronograma, 
        name='avance_de_obra_grafico2.exportCronograma'),
    url(r'^seguimientomateriales/(?P<id_presupuesto>[0-9]+)/$', 
        views.seguimientoMateriales,
     name='avance_de_obra_grafico2.seguimientoMateriales'),
    url(r'^consultarmaterialesaliquidarlite/(?P<id>[0-9]+)/$',
        views.materialesAliquidarlite, 
        name='avance_de_obra_grafico2.materialesAliquidarlite'),
    url(r'^exportarmaterialesaliquidar/$',
        views.exportarMaterialesaLiquidar, 
        name='avance_de_obra_grafico2.exportarmaterialesaliquidar'),
    url(r'^exportarcantidadesaliquidar/$',
        views.exportarCantidadesaLiquidar, 
        name='avance_de_obra_grafico2.exportarCantidadesaLiquidar'),

    url(r'^descargar-plantilla-programacion/$', 
        views.descargar_plantilla_programacion, 
        name='avance_de_obra_grafico2.descargar_plantilla_programacion'),

     url(r'^guardar-programacion-archivo/$', 
        views.guardar_programacion_archivo, 
        name='avance_de_obra_grafico2.guardar_programacion_archivo'),
    
    url(r'^catalogo/$', views.catalogo, name='avance_de_obra_grafico2.catalogos'),    
    url(r'^inactivar-catalogo/$', views.inactivar_catalogo, name='avance_de_obra_grafico2.inactivar_catalogo'),    
    url(r'^activar-catalogo/$', views.activar_catalogo, name='avance_de_obra_grafico2.activar_catalogo'),    
    url(r'^excel_catalogo/$', views.excel_catalogo, name='avance_de_obra_grafico2.excel_catalogo'),    

    url(r'^uucc/(?P<catalogo_id>[0-9]+)/$', views.uucc, name='avance_de_obra_grafico2.uucc'),        
    url(r'^eliminar_id_uucc/$', views.eliminar_id_uucc, name='avance_de_obra_grafico2.eliminar_id_uucc'), 
    url(r'^excel_uucc/$', views.excel_uucc, name='avance_de_obra_grafico2.excel_uucc'),    

    url(r'^materiales/(?P<catalogo_id>[0-9]+)/$', views.materiales, name='avance_de_obra_grafico2.materiales'),                   
    url(r'^eliminar_id_materiales/$', views.eliminar_id_materiales, name='avance_de_obra_grafico2.eliminar_id_materiales'), 
    url(r'^excel_mat/$', views.excel_mat, name='avance_de_obra_grafico2.excel_mat'),    

    url(r'^mano_obra/(?P<catalogo_id>[0-9]+)/$', views.mano_obra, name='avance_de_obra_grafico2.manoObra'),                   
    url(r'^eliminar_id_mano_obra/$', views.eliminar_id_mano_obra, name='avance_de_obra_grafico2.eliminar_id_mano_obra'),     
    url(r'^excel_mo/$', views.excel_mo, name='avance_de_obra_grafico2.excel_mo'),    

    url(r'^desgl_mat/(?P<uucc_id>[0-9]+)/$', views.desgloce_mat, name='avance_de_obra_grafico2.desgl_mat'),  
    url(r'^eliminar_id_desgl_mat/$', views.eliminar_id_desgl_mat, name='avance_de_obra_grafico2.eliminar_id_mano_obra'),     
    url(r'^excel_desgl_mat/$', views.excel_desgl_mat, name='avance_de_obra_grafico2.excel_desgl_mat'),    

    url(r'^desgl_mo/(?P<uucc_id>[0-9]+)/$', views.desgloce_mo, name='avance_de_obra_grafico2.desgl_mo'),  
    url(r'^eliminar_id_desgl_mo/$', views.eliminar_id_desgl_mo, name='avance_de_obra_grafico2.eliminar_id_desgl_mo'),         
    url(r'^excel_desgl_mo/$', views.excel_desgl_mo, name='avance_de_obra_grafico2.excel_desgl_mo'),    

    url(r'^descargar_plantilla_masiva/$', views.descargar_plantilla_masiva, name='avance_de_obra_grafico2.descargar_plantilla_masiva'),
    url(r'^carga_masiva_catalogo/$', views.cargar_excel_catalogo_masivo, name='avance_de_obra_grafico2.carga_masiva_catalogo'),        
]