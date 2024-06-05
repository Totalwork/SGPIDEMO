from django.db.models import Q
from django.conf import settings
from contrato.models import Contrato, VigenciaContrato, EmpresaContrato
from contrato.enumeration import estadoC, tipoV, notificacion #, tipoC
from proyecto.models import Proyecto
from parametrizacion.models import Notificacion, Funcionario
from adminMail.models import Mensaje
from sinin4.functions import functions
import xlsxwriter
import uuid
import os
from datetime import *

class FunctionTask:

    @staticmethod
    def cambioEstadoContrato():
        try:
            estados = []
            estados.append(estadoC.porVencer)
            estados.append(estadoC.vigente)
            estados.append(estadoC.vencido)

            queryset = Contrato.objects.filter(estado_id__in=estados)

            for cont in queryset:

                # if cont.id == 1564: # Para eliminar

                fecha_fin = ''
                formato_fecha = "%Y-%m-%d"

                hoy = date.today()
                hoy = datetime.strptime(str(hoy), formato_fecha)

                # print "id::"+str(cont.id)

                fecha_fin = fechaFin(cont.id)
                # fecha_fin = datetime.strptime(str(fecha_fin), formato_fecha)
                # print ("fec fin:",fecha_fin)

                if fecha_fin:

                    diferencias = fecha_fin - hoy
                    # print ("dias:",diferencias.days)
                    # print "----------------------------------"

                    if diferencias.days <= 0:
                        cont.estado_id = estadoC.vencido
                        # print "estd:"+str(cont.estado_id)
                        # print "vencido"
                    if diferencias.days > 0 and diferencias.days <= 90:
                        cont.estado_id = estadoC.porVencer
                        # print "Por Vencer"
                    if diferencias.days > 90:
                        cont.estado_id = estadoC.vigente
                        # print "Vigente"

                    cont.save()
            # return JsonResponse({'message':'Ok','success':'ok','data':''}) # Para eliminar
        except Exception as e:
            functions.toLog(e,'Tasks Cambiar Estado Contrato')

    @staticmethod
    def contratoDeObraPorVencidos():
        try:
            # estado_c=estadoC()
            # estados = []
            # estados.append(estadoC.porVencer)
            # estados.append(estadoC.vigente)

            # queryset = Contrato.objects.filter(estado_id=estadoC.porVencer)
            # queryset_proy = Proyecto.objects.all()
            
            queryset_func = Funcionario.objects.filter(notificaciones=notificacion.cod, activo=1)

            for func in queryset_func:
                # if func.id == 224:
                # print "si estoy"
                if func.persona.correo:
                    correo_envio = ''
                    contenido = ''

                    # Consultar los contratos Por Vencer
                    qset = Q(funcionario_id = func.id)
                    qset = qset & ( Q( proyecto__contrato__estado__id = estadoC.porVencer) )
                    qset =  qset & ( Q( proyecto__contrato__activo = 1) )

                    # queryset_proy_func = Proyecto.funcionario.through.objects.filter(qset).values(
                    # 	'proyecto__id',
                    # 	'proyecto__mcontrato__nombre',
                    # 	'proyecto__contrato__id', 
                    # 	'proyecto__contrato__numero', 
                    # 	'proyecto__contrato__tipo_contrato__nombre',
                    # 	'proyecto__contrato__contratista__nombre',
                    # 	'proyecto__mcontrato__nombre')

                    todosContratos = Contrato.objects.filter(
                        id__in=Proyecto.funcionario.through.objects.filter(qset).values(
                        'proyecto__contrato__id')).values(
                        'numero','mcontrato__nombre','tipo_contrato__nombre',
                        'contratista__nombre','id','nombre').order_by('mcontrato__nombre','tipo_contrato__nombre')
                    # print "Num:"+str(queryset_proy_func.count())

                    # filtramos lo contratos solo lectura
                    contratos = []
                    for	cont in todosContratos:
                        contrato = Contrato.objects.get(pk=cont['id'])
                        verificar = esSoloLectura(contrato, func.empresa.id)
                        if verificar == False:
                            contratos.append(cont)

                    # print("notif:: ", func.persona.correo)
                    if contratos:
                        correo_envio = correo_envio+func.persona.correo+';'

                        # INICIO - Crear el Excel
                        # response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
                        # response['Content-Disposition'] = 'attachment; filename="Reporte_contrato.xls"'

                        # workbook = xlsxwriter.Workbook(response, {'in_memory': True})

                        unique_filename = uuid.uuid4()
                        nombre_archivo = '{}.xlsx'.format(unique_filename)
                        workbook = xlsxwriter.Workbook(nombre_archivo)
                        worksheet = workbook.add_worksheet('Contratos')

                        worksheet.set_column('A:A', 40)
                        worksheet.set_column('B:B', 18)
                        worksheet.set_column('C:D', 12)
                        worksheet.set_column('E:G', 35)

                        format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
                        format1.set_align('center')
                        format1.set_align('vcenter')
                        format2=workbook.add_format({'border':0})
                        format5=workbook.add_format()
                        format5.set_num_format('yyyy-mm-dd')

                        row=1
                        col=0

                        worksheet.write('A1', 'M-Contrato', format1)
                        worksheet.write('B1', 'Numero Contrato', format1)
                        worksheet.write('C1', 'Nombre Contrato', format1)
                        worksheet.write('D1', 'Fecha Inicio', format1)
                        worksheet.write('E1', 'Fecha Fin', format1)
                        worksheet.write('F1', 'Tipo', format1)
                        worksheet.write('G1', 'Contratista', format1)

                        # FIN - Crear el Excel

                        for cont in contratos:

                            fecha_fin = ''
                            fecha_inicio = ''
                            mcontrato = ''

                            # fecha_fin = fechaFin(cont.id)
                            fecha_fin = fechaFin(cont['id'])
                            # print("Fecha fin: ", fecha_fin)

                            # fecha_inicio = fechaInicio(cont.id)
                            fecha_inicio = fechaInicio(cont['id'])
                            # print("Fecha inicio: ", fecha_inicio)

                            # if cont.mcontrato:
                            # 	mcontrato = cont.mcontrato.nombre
                            # else:
                            # 	mcontrato = 'No Aplica'

                            # worksheet.write(row, col,mcontrato,format2)
                            worksheet.write(row, col,cont['mcontrato__nombre'],format2)
                            worksheet.write(row, col+1,cont['numero'],format2)
                            worksheet.write(row, col+2,cont['nombre'],format2)
                            worksheet.write(row, col+3,fecha_inicio,format5)
                            worksheet.write(row, col+4,fecha_fin,format5)
                            worksheet.write(row, col+5,cont['tipo_contrato__nombre'],format2)
                            worksheet.write(row, col+6,cont['contratista__nombre'],format2)
                            row +=1
                        workbook.close()

                        contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
                        contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que los siguientes contratos estan por vencer<br/><br/>'
                        contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
                        contenido+='Gracias,<br/><br/><br/>'
                        contenido+='Equipo SININ<br/>'
                        contenido+=settings.EMAIL_HOST_USER+'<br/>'
                        contenido+='<a href="'+settings.SERVER_URL2+'/usuario/">SININ</a><br/>'

                        mail = Mensaje(
                            remitente=settings.REMITENTE,
                            destinatario=correo_envio,
                            asunto='Contratos por vencer',
                            contenido=contenido,
                            appLabel='contrato',
                            tieneAdjunto=True,
                            adjunto=nombre_archivo,
                            copia=''
                        )
                        mail.Send()
                        # mail.simpleSend()
                        if os.path.exists(nombre_archivo):
                            os.remove(nombre_archivo)

        except Exception as e:
            functions.toLog(e,'Tasks Contratos por vencer')

    @staticmethod
    def contratoDeObraVencidos():
        try:
            queryset_func = Funcionario.objects.filter(notificaciones=notificacion.cod, activo=1)

            for func in queryset_func:
                # if func.id == 224:
                if func.persona.correo:
                    correo_envio = ''
                    contenido = ''

                    # Consultar los contratos Por Vencer
                    qset = Q(funcionario_id = func.id)
                    qset = qset & ( Q( proyecto__contrato__estado__id = estadoC.vencido) )
                    qset =  qset & ( Q( proyecto__contrato__activo = 1) )

                    # queryset_proy_func = Proyecto.funcionario.through.objects.filter(qset).values(
                    # 	'proyecto__id',
                    # 	'proyecto__mcontrato__nombre',
                    # 	'proyecto__contrato__id', 
                    # 	'proyecto__contrato__numero', 
                    # 	'proyecto__contrato__tipo_contrato__nombre',
                    # 	'proyecto__contrato__contratista__nombre',
                    # 	'proyecto__mcontrato__nombre')

                    todosContratos = Contrato.objects.filter(
                        id__in=Proyecto.funcionario.through.objects.filter(qset).values(
                        'proyecto__contrato__id')).values(
                        'numero','mcontrato__nombre','tipo_contrato__nombre',
                        'contratista__nombre','id','nombre').order_by('mcontrato__nombre','tipo_contrato__nombre')

                    # filtramos lo contratos solo lectura
                    contratos = []
                    for	cont in todosContratos:
                        contrato = Contrato.objects.get(pk=cont['id'])
                        verificar = esSoloLectura(contrato, func.empresa.id)
                        if verificar == False:
                            contratos.append(cont)

                    # print("notif:: ", func.persona.correo)
                    if contratos:
                        correo_envio = correo_envio+func.persona.correo+';'

                        # INICIO - Crear el Excel
                        # response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
                        # response['Content-Disposition'] = 'attachment; filename="Reporte_contrato.xls"'

                        # workbook = xlsxwriter.Workbook(response, {'in_memory': True})

                        unique_filename = uuid.uuid4()
                        nombre_archivo = '{}.xlsx'.format(unique_filename)
                        workbook = xlsxwriter.Workbook(nombre_archivo)
                        worksheet = workbook.add_worksheet('Contratos')

                        worksheet.set_column('A:A', 40)
                        worksheet.set_column('B:B', 18)
                        worksheet.set_column('C:D', 12)
                        worksheet.set_column('E:G', 35)

                        format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
                        format1.set_align('center')
                        format1.set_align('vcenter')
                        format2=workbook.add_format({'border':0})
                        format5=workbook.add_format()
                        format5.set_num_format('yyyy-mm-dd')

                        row=1
                        col=0

                        worksheet.write('A1', 'M-Contrato', format1)
                        worksheet.write('B1', 'Numero Contrato', format1)
                        worksheet.write('C1', 'Nombre Contrato', format1)
                        worksheet.write('D1', 'Fecha Inicio', format1)
                        worksheet.write('E1', 'Fecha Fin', format1)
                        worksheet.write('F1', 'Tipo', format1)
                        worksheet.write('G1', 'Contratista', format1)

                        for cont in contratos:

                            fecha_fin = ''
                            fecha_inicio = ''
                            mcontrato = ''

                            fecha_fin = fechaFin(cont['id'])

                            fecha_inicio = fechaInicio(cont['id'])

                            worksheet.write(row, col,cont['mcontrato__nombre'],format2)
                            worksheet.write(row, col+1,cont['numero'],format2)
                            worksheet.write(row, col+2,cont['nombre'],format2)
                            worksheet.write(row, col+3,fecha_inicio,format5)
                            worksheet.write(row, col+4,fecha_fin,format5)
                            worksheet.write(row, col+5,cont['tipo_contrato__nombre'],format2)
                            worksheet.write(row, col+6,cont['contratista__nombre'],format2)
                            row +=1
                        workbook.close()
                        # FIN - Crear el Excel

                        contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
                        contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que los siguientes contratos estan vencidos<br/><br/>'
                        contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
                        contenido+='Gracias,<br/><br/><br/>'
                        contenido+='Equipo SININ<br/>'
                        contenido+=settings.EMAIL_HOST_USER+'<br/>'
                        contenido+='<a href="'+settings.SERVER_URL2+'/usuario/">SININ</a><br/>'

                        mail = Mensaje(
                            remitente=settings.REMITENTE,
                            destinatario=correo_envio,
                            asunto='Contratos vencidos',
                            contenido=contenido,
                            appLabel='contrato',
                            tieneAdjunto=True,
                            adjunto=nombre_archivo,
                            copia=''
                        )
                        mail.Send()
                        # mail.simpleSend()
                        if os.path.exists(nombre_archivo):
                            os.remove(nombre_archivo)

        except Exception as e:
            functions.toLog(e,'Tasks Contratos vencidos')

    @staticmethod
    def contratoAuxiliarPorVencer():
        try:
            queryset_func = Funcionario.objects.filter(notificaciones=notificacion.aux, activo=1)		
            for func in queryset_func:
                # if func.id == 224:
                if func.persona.correo:
                    correo_envio = ''
                    contenido = ''
                    # Consultar los contratos 2019
                    qset = (Q(contrato__tipo_contrato=12))& (Q(edita=1)) &(Q(empresa=4) & Q(participa=1))
                    ListMacro = EmpresaContrato.objects.filter(qset).values('contrato_id').order_by("contrato_id")
                    # Consultar los contratos 2019 asociados a proyectos
                    qset = Q(funcionario_id = func.id)
                    qset =  qset & ( Q( proyecto__contrato__mcontrato__in = ListMacro) )
                    qset =  qset & ( Q( proyecto__contrato__activo = 1) )
                    noauxiliares = Proyecto.funcionario.through.objects.filter(qset).values('proyecto__contrato__id')
                    # Consultar los contratos 2019 auxiliares por Vencer
                    qset2 = ~Q(id__in=noauxiliares)
                    qset2 = qset2 & ( Q( mcontrato__id__in = ListMacro) )
                    qset2 = qset2 & ( Q( estado__id = estadoC.porVencer) )				
                    auxiliaresPorVencer = Contrato.objects.filter(qset2).values('id')					
                    # filtramos lo contratos solo lectura					
                    contratos = []
                    for	cont in auxiliaresPorVencer:
                        contrato = Contrato.objects.get(pk=cont['id'])
                        verificar = esSoloLectura(contrato, func.empresa.id)
                        if verificar == False :
                            contratos.append(contrato)				
                    if contratos:					
                        correo_envio = correo_envio+func.persona.correo+';'				
                        #correo_envio ='jsamper@totalwork.co;johansamperg@gmail.com;'
                        # INICIO - Crear el Excel						
                        unique_filename = uuid.uuid4()
                        nombre_archivo = '{}.xlsx'.format(unique_filename)
                        workbook = xlsxwriter.Workbook(nombre_archivo)
                        worksheet = workbook.add_worksheet('Contratos')
                        worksheet.set_column('A:A', 40)
                        worksheet.set_column('B:B', 18)
                        worksheet.set_column('C:D', 12)
                        worksheet.set_column('E:G', 35)
                        format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
                        format1.set_align('center')
                        format1.set_align('vcenter')
                        format2=workbook.add_format({'border':0})
                        format5=workbook.add_format()
                        format5.set_num_format('yyyy-mm-dd')
                        row=1
                        col=0
                        worksheet.write('A1', 'M-Contrato', format1)
                        worksheet.write('B1', 'Numero Contrato', format1)
                        worksheet.write('C1', 'Nombre Contrato', format1)
                        worksheet.write('D1', 'Fecha Inicio', format1)
                        worksheet.write('E1', 'Fecha Fin', format1)
                        worksheet.write('F1', 'Tipo', format1)
                        worksheet.write('G1', 'Contratista', format1)
                        for cont in contratos:
                            fecha_fin = ''
                            fecha_inicio = ''
                            mcontrato = ''
                            fecha_fin = fechaFin(cont.id)
                            fecha_inicio = fechaInicio(cont.id)
                            worksheet.write(row, col,cont.mcontrato.nombre,format2)
                            worksheet.write(row, col+1,cont.numero,format2)
                            worksheet.write(row, col+2,cont.nombre,format2)
                            worksheet.write(row, col+3,fecha_inicio,format5)
                            worksheet.write(row, col+4,fecha_fin,format5)
                            worksheet.write(row, col+5,cont.tipo_contrato.nombre,format2)
                            worksheet.write(row, col+6,cont.contratista.nombre,format2)
                            row +=1
                        workbook.close()
                        # FIN - Crear el Excel
                        contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
                        contenido+='Estimado usuario(a), <br/><br/>Nos permitimos comunicarle que los siguientes contratos auxiliares estan por vencer<br/><br/>'
                        contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
                        contenido+='Gracias,<br/><br/><br/>'
                        contenido+='Equipo SININ<br/>'
                        contenido+=settings.EMAIL_HOST_USER+'<br/>'
                        contenido+='<a href="'+settings.SERVER_URL2+'/usuario/">SININ</a><br/>'
                        mail = Mensaje(
                            remitente=settings.REMITENTE,
                            destinatario=correo_envio,
                            asunto='Contratos Auxiliares por Vencer',
                            contenido=contenido,
                            appLabel='contrato',
                            tieneAdjunto=True,
                            adjunto=nombre_archivo,
                            copia=''
                        )					
                        mail.Send()	
                        # mail.simpleSend()
                        if os.path.exists(nombre_archivo):
                            os.remove(nombre_archivo)
        except Exception as e:
            functions.toLog(e,'Tasks Contratos auxiliares por vencer')

    @staticmethod
    def contratoAuxiliaresVencidos():
        try:
            queryset_func = Funcionario.objects.filter(notificaciones=notificacion.aux, activo=1)		
            for func in queryset_func:
                # if func.id == 224:
                if func.persona.correo:
                    correo_envio = ''
                    contenido = ''
                    # Consultar los contratos 2019
                    qset = (Q(contrato__tipo_contrato=12))& (Q(edita=1)) &(Q(empresa=4) & Q(participa=1))
                    ListMacro = EmpresaContrato.objects.filter(qset).values('contrato_id').order_by("contrato_id")
                    # Consultar los contratos 2019 asociados a proyectos
                    qset = Q(funcionario_id = func.id)
                    qset =  qset & ( Q( proyecto__contrato__mcontrato__in = ListMacro) )
                    qset =  qset & ( Q( proyecto__contrato__activo = 1) )
                    noauxiliares = Proyecto.funcionario.through.objects.filter(qset).values('proyecto__contrato__id')
                    # Consultar los contratos 2019 auxiliares vencidos
                    qset2 = ~Q(id__in=noauxiliares)
                    qset2 = qset2 & ( Q( mcontrato__id__in = ListMacro) )
                    qset2 = qset2 & ( Q( estado__id = estadoC.vencido) )
                    #auxiliaresvencidos = Contrato.objects.filter(qset2).values('id','nombre','estado__nombre')
                    auxiliaresvencidos = Contrato.objects.filter(qset2).values('id')					
                    # filtramos lo contratos solo lectura					
                    contratos = []
                    for	cont in auxiliaresvencidos:
                        contrato = Contrato.objects.get(pk=cont['id'])
                        verificar = esSoloLectura(contrato, func.empresa.id)
                        if verificar == False :
                            contratos.append(contrato)				
                    if contratos:
                        #correo_envio ='jsamper@totalwork.co;johansamperg@gmail.com;'
                        correo_envio = correo_envio+func.persona.correo+';'				

                        # INICIO - Crear el Excel						
                        unique_filename = uuid.uuid4()
                        nombre_archivo = '{}.xlsx'.format(unique_filename)
                        workbook = xlsxwriter.Workbook(nombre_archivo)
                        worksheet = workbook.add_worksheet('Contratos')
                        worksheet.set_column('A:A', 40)
                        worksheet.set_column('B:B', 18)
                        worksheet.set_column('C:D', 12)
                        worksheet.set_column('E:G', 35)
                        format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
                        format1.set_align('center')
                        format1.set_align('vcenter')
                        format2=workbook.add_format({'border':0})
                        format5=workbook.add_format()
                        format5.set_num_format('yyyy-mm-dd')
                        row=1
                        col=0
                        worksheet.write('A1', 'M-Contrato', format1)
                        worksheet.write('B1', 'Numero Contrato', format1)
                        worksheet.write('C1', 'Nombre Contrato', format1)
                        worksheet.write('D1', 'Fecha Inicio', format1)
                        worksheet.write('E1', 'Fecha Fin', format1)
                        worksheet.write('F1', 'Tipo', format1)
                        worksheet.write('G1', 'Contratista', format1)
                        for cont in contratos:
                            fecha_fin = ''
                            fecha_inicio = ''
                            mcontrato = ''
                            fecha_fin = fechaFin(cont.id)
                            fecha_inicio = fechaInicio(cont.id)
                            worksheet.write(row, col,cont.mcontrato.nombre,format2)
                            worksheet.write(row, col+1,cont.numero,format2)
                            worksheet.write(row, col+2,cont.nombre,format2)
                            worksheet.write(row, col+3,fecha_inicio,format5)
                            worksheet.write(row, col+4,fecha_fin,format5)
                            worksheet.write(row, col+5,cont.tipo_contrato.nombre,format2)
                            worksheet.write(row, col+6,cont.contratista.nombre,format2)
                            row +=1
                        workbook.close()
                        # FIN - Crear el Excel
                        contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
                        contenido+='Estimado usuario(a), <br/><br/>Nos permitimos comunicarle que los siguientes contratos auxiliares estan vencidos<br/><br/>'
                        contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
                        contenido+='Gracias,<br/><br/><br/>'
                        contenido+='Equipo SININ<br/>'
                        contenido+=settings.EMAIL_HOST_USER+'<br/>'
                        contenido+='<a href="'+settings.SERVER_URL2+'/usuario/">SININ</a><br/>'
                        mail = Mensaje(
                            remitente=settings.REMITENTE,
                            destinatario=correo_envio,
                            asunto='Contratos auxiliares vencidos',
                            contenido=contenido,
                            appLabel='contrato',
                            tieneAdjunto=True,
                            adjunto=nombre_archivo,
                            copia=''
                        )					
                        mail.Send()	
                        # mail.simpleSend()
                        if os.path.exists(nombre_archivo):
                            os.remove(nombre_archivo)
        except Exception as e:
            functions.toLog(e,'Tasks Contratos auxiliares vencidos')

    @staticmethod    
    def notificacionMcontrato(mcontrato,usuario):	
        #import pdb; pdb.set_trace()
        mcontrato_numero = str(mcontrato['numero'])
        mcontrato_nombre = str(mcontrato['nombre'])		
        usuario_nombre = str(usuario.persona.nombres + ' ' + usuario.persona.apellidos)
        usuario_empresa = str(usuario.empresa.nombre)

        #queryset_func = Funcionario.objects.filter(notificaciones=notificacion.mcontrato, activo=1)	
        #arrayNotiInternoTemp = ['yassera@totalwork.co','dacosta@totalwork.co','jsamper@totalwork.co']
        arrayNotiInternoTemp = ['jsamper@totalwork.co']
        for func in arrayNotiInternoTemp:	
            if func:
                #correo_envio = ''
                correo_envio = func+';'
                contenido = ''			
                # if correo_envio != '':
                # 	correo_envio = correo_envio+func+';'
                # else:
                # 	correo_envio = func.persona.correo+';'
                
                contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/>'
                contenido+='Se ha registrado satifactoriamente un Contrato Administrador de Recursos, se relaciona la informacion ingresada al sistema:<br/><br/>'
                contenido+='''
                    <style type="text/css">
                        table, td, th {  
                            border: 1px solid #ddd;
                            text-align: left;
                        }
                        table {
                            border-collapse: collapse;
                            width: 100%;
                        }
                        th, td {
                            padding: 15px;
                        }
                    </style>			
                    <table>
                    <thead>
                    <tr>
                        <th>Nro. Contrato</th>									
                        <th>Contrato</th>					
                        <th>Usuario</th>
                        <th>Empresa</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td>'''+mcontrato_numero+'''</td>
                        <td>'''+mcontrato_nombre+'''</td>					
                        <td>'''+usuario_nombre+'''</td>
                        <td>'''+usuario_empresa+'''</td>
                    </tr>
                    </tbody>
                    </table>	
                    <br/><br/>		
                '''
                contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
                contenido+='Gracias,<br/><br/><br/>'
                contenido+='Equipo SININ<br/>'					
                contenido+=settings.EMAIL_HOST_USER+'<br/>'
                # contenido+='<a href= "'+settings.SERVER_URL+':'+settings.PORT_SERVER+'/usuario/">SININ</a><br/>'
                contenido+='<a href= "https://http://conpes.sinin.co/">SININ</a><br/>'
                mail = Mensaje(
                    remitente=settings.REMITENTE,
                    destinatario=correo_envio,
                    asunto=' Nuevo Contrato Administrador de Recursos Registrado',
                    contenido=contenido,
                    appLabel='mcontrato',
                    tieneAdjunto=False,			
                    copia=''
                )
                
                mail.Send()
					

def fechaFin(id_contrato):
	try:
		fecha_fin = '' # Fecha fin vigencia de contrato, replante y otroSi
		fecha_f = ''
		fecha_f1 = ''
		fecha_f_rei = ''
		a_inicio = None
		a_reinicio = None
		formato_fecha = "%Y-%m-%d"
		cont = 0
		cont2 = 0

		result = VigenciaContrato.objects.filter(contrato_id=id_contrato)

		if result:
			for vigencia in result:
				if vigencia.tipo.id == tipoV.contrato:
					fecha_fin = vigencia.fecha_fin

			for vigencia in result:
				if vigencia.tipo.id == tipoV.replanteo and vigencia.fecha_fin:
					fecha_fin = vigencia.fecha_fin

			for vigencia in result:
				if vigencia.tipo.id == tipoV.otrosi or vigencia.tipo.id == tipoV.actaAmpliacion:
					if vigencia.fecha_fin:

						if fecha_fin < vigencia.fecha_fin:
							fecha_fin = vigencia.fecha_fin

			# print("FechaFinVig::",fecha_fin)
			fecha_f1 = datetime.strptime(str(fecha_fin), formato_fecha)

			# Para sacar los dias que duro suspendidos
			for vigencia in result:

				if vigencia.tipo.id == tipoV.actaSuspension:
					a_inicio = vigencia.fecha_inicio

				if vigencia.tipo.id == tipoV.actaReinicio:
					a_reinicio = vigencia.fecha_inicio
					cont += 1

				if a_reinicio != None and a_inicio != None:
					# print("a_inicio",a_inicio)
					# print("a_reinicio",a_reinicio)

					a_inicio = datetime.strptime(str(a_inicio), formato_fecha)
					a_reinicio = datetime.strptime(str(a_reinicio), formato_fecha)
					
					dias = a_reinicio - a_inicio
					# print "dias:"+str(dias.days)

					if dias.days > 0:
						fecha_fin = fecha_fin + timedelta(days=dias.days)
						# print("FechaFinActas::",fecha_fin)

					a_inicio = None
					a_reinicio = None

				fecha_f = datetime.strptime(str(fecha_fin), formato_fecha)

			# Para sacar la fecha fin del acta de reinicio
			if cont > 0:
				for vigencia in result:

					if vigencia.tipo.id == tipoV.actaReinicio:
						cont2 = cont2+1
						if ((vigencia.fecha_fin) and (cont2 == cont)):
							fecha_f_rei = datetime.strptime(str(vigencia.fecha_fin), formato_fecha)

			# Sacar la fecha fin mayor
			if fecha_f_rei != '':
				if fecha_f1 > fecha_f_rei:
					return fecha_f1
				else:
					return fecha_f_rei
			else:
				return fecha_f
		else:
			return None
	except Exception as e:
		functions.toLog(e,'Tasks FechaFin')

def fechaInicio(id_contrato):
	fecha_inicio = ''
	fecha_i= ''
	formato_fecha = "%Y-%m-%d"

	result = VigenciaContrato.objects.filter(contrato_id=id_contrato)

	if result:
		for vigencia in result:
			if vigencia.tipo.id == tipoV.contrato:
				fecha_inicio = vigencia.fecha_inicio

		for vigencia in result:
			if vigencia.tipo.id == tipoV.replanteo and vigencia.fecha_inicio:
				fecha_inicio = vigencia.fecha_inicio

		# print fecha_inicio
		fecha_i = datetime.strptime(str(fecha_inicio), formato_fecha)

		return fecha_i
	else:
		return None

def esSoloLectura(contratoObj, empresa):
		if contratoObj.mcontrato:
			contrato = contratoObj.mcontrato.id
		else:
			contrato = contratoObj.id

		empresaContrato = EmpresaContrato.objects.filter(contrato__id=contrato, empresa__id=empresa).first()
		soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
		return soloLectura
