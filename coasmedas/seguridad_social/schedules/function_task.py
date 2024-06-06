# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from adminMail.models import Mensaje
from django.db import transaction, connection
# from usuario.models import Usuario
from seguridad_social.models import CorreoContratista
import uuid
from django.conf import settings
import os
import xlsxwriter
from coasmedas.functions import functions

class FunctionTask:
        
    @staticmethod
    def TrabajoEnAlturaPorVencer():
        cursor = connection.cursor()
        try:

            ruta = settings.STATICFILES_DIRS[0]
            rutaPapelera = ruta + '\papelera'
            cursor.callproc('[dbo].[seguridad_social_personal_trabajo_altura_por_vencer]')		
            columns = cursor.description 
            empleados = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
            
            if empleados:		
                cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[12,])#3 es el id de la notificacion 
                columns = cursor.description 
                personas_notificar = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
                correo_envio=None
                for p in personas_notificar:
                    #agrega el correo del destinatario
                    correo_envio=None
                    for e in empleados:
                        if p['empresa_id'] == e['empresa_id']:
                            correo_envio=p['correo']
                            break

                    if correo_envio:
                        contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
                        contenido = contenido + "Estimado usuario(a), <br/><br/>Adjunto envio, la relaci&oacute;n de empleados con el certificado en altura por vencer<br/><br/>"		
                        contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
                        contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
                        
                        unique_filename = uuid.uuid4()
                        nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
                        workbook = xlsxwriter.Workbook(nombre_archivo)
                        worksheet = workbook.add_worksheet()

                        format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
                        format2=workbook.add_format({'border':1})
                        format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})

                        worksheet.write('A1','Contratista', format1)	
                        worksheet.write('B1','Cedula', format1)	
                        worksheet.write('C1','Nombres', format1)
                        worksheet.write('D1','Apellidos', format1)
                        worksheet.write('E1','Vencimiento trabajo en altura', format1)

                        worksheet.set_column('A:A',30)
                        worksheet.set_column('B:B',15)
                        worksheet.set_column('C:C',30)
                        worksheet.set_column('D:D',30)
                        worksheet.set_column('E:E',20)
                        row=1
                        col=0
                        for e in empleados:
                            if p['empresa_id'] == e['empresa_id']:
                                worksheet.write(row,col,e['contratista'] ,format2)
                                worksheet.write(row,col+1,e['cedula'] ,format2)
                                worksheet.write(row,col+2,e['nombres'] ,format2)
                                worksheet.write(row,col+3,e['apellidos'] ,format2)
                                worksheet.write(row,col+4,e['fecha_tsa'] ,format_date)						
                                row +=1

                        workbook.close()
                        mail = Mensaje(
                                remitente=settings.REMITENTE,
                                destinatario=correo_envio,
                                asunto='Certificado de trabajo en altura por vencer',
                                contenido=contenido,
                                appLabel='seguridad_social',
                                tieneAdjunto=True,
                                adjunto=nombre_archivo,
                                copia=''
                                )												
                        mail.Send()
                        # if os.path.exists(nombre_archivo):
                        # 	os.remove(nombre_archivo)

        except Exception as e:
            functions.toLog(e, 'seguridad_social.task.TrabajoEnAlturaPorVencer')
            print(e)
    
    @staticmethod
    def TrabajoEnAlturaVencido():
        cursor = connection.cursor()
        try:

            ruta = settings.STATICFILES_DIRS[0]
            rutaPapelera = ruta + '\papelera'
            cursor.callproc('[dbo].[seguridad_social_personal_trabajo_altura_vencido]')		
            columns = cursor.description 
            empleados = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
            
            if empleados:		
                cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[12,])
                columns = cursor.description 
                personas_notificar = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

                for p in personas_notificar:
                    correo_envio=None
                    #agrega el correo del destinatario
                    for e in empleados:
                        if p['empresa_id'] == e['empresa_id']:
                            correo_envio=p['correo']
                            break

                    if correo_envio:
                        contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
                        contenido = contenido + "<p style='Color:#FF0404;'>Estimado usuario(a), <br/><br/>Adjunto envio, la relaci&oacute;n de empleados con el certificado en altura vencido</p><br/><br/>"		
                        contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
                        contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
                        unique_filename = uuid.uuid4()
                        nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
                        workbook = xlsxwriter.Workbook(nombre_archivo)
                        worksheet = workbook.add_worksheet()

                        format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
                        format2=workbook.add_format({'border':1})
                        format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})

                        worksheet.write('A1','Contratista', format1)	
                        worksheet.write('B1','Cedula', format1)	
                        worksheet.write('C1','Nombres', format1)
                        worksheet.write('D1','Apellidos', format1)
                        worksheet.write('E1','Vencimiento trabajo en altura', format1)

                        worksheet.set_column('A:A',30)
                        worksheet.set_column('B:B',15)
                        worksheet.set_column('C:C',30)
                        worksheet.set_column('D:D',30)
                        worksheet.set_column('E:E',20)
                        row=1
                        col=0
                        for e in empleados:
                            if p['empresa_id'] == e['empresa_id']:
                                worksheet.write(row,col,e['contratista'] ,format2)
                                worksheet.write(row,col+1,e['cedula'] ,format2)
                                worksheet.write(row,col+2,e['nombres'] ,format2)
                                worksheet.write(row,col+3,e['apellidos'] ,format2)
                                worksheet.write(row,col+4,e['fecha_tsa'] ,format_date)						
                                row +=1

                        workbook.close()
                        mail = Mensaje(
                                remitente=settings.REMITENTE,
                                destinatario=correo_envio,
                                asunto='Certificado de trabajo en altura vencido',
                                contenido=contenido,
                                appLabel='seguridad_social',
                                tieneAdjunto=True,
                                adjunto=nombre_archivo,
                                copia=''
                                )												
                        mail.Send()
                        # if os.path.exists(nombre_archivo):
                        # 	os.remove(nombre_archivo)

        except Exception as e:
            functions.toLog(e, 'seguridad_social.task.TrabajoEnAlturaVencido')
            print(e)		
    
    @staticmethod
    def SeguridadSocialVencida():
        cursor = connection.cursor()
        try:
            meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
            ruta = settings.STATICFILES_DIRS[0]
            rutaPapelera = ruta + '\papelera'
            cursor.callproc('[dbo].[seguridad_social_consultar_contratistas_con_ss_vencida]')		
            columns = cursor.description 
            contratistas = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
            
            for c in contratistas:
                cursor.callproc('[dbo].[seguridad_social_consultar_empleados_con_ss_vencida]', [c['planilla_id'],])		
                columns = cursor.description 
                empleados = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
                nombre_archivo=''
                if empleados:
                    unique_filename = uuid.uuid4()
                    nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
                    workbook = xlsxwriter.Workbook(nombre_archivo)
                    worksheet = workbook.add_worksheet()

                    format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
                    format2=workbook.add_format({'border':1})
                    format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
                    
                    worksheet.write('A1','Cedula', format1)	
                    worksheet.write('B1','Nombres', format1)
                    worksheet.write('C1','Apellidos', format1)
                    worksheet.write('D1','Escolaridad', format1)
                    worksheet.write('E1','Cargo', format1)	

                    worksheet.set_column('A:A',30)
                    worksheet.set_column('B:B',30)
                    worksheet.set_column('C:C',30)
                    worksheet.set_column('D:D',30)
                    worksheet.set_column('E:E',30)
                    row=1
                    col=0
                    for e in empleados:					
                        worksheet.write(row,col,e['cedula'] ,format2)
                        worksheet.write(row,col+1,e['nombres'] ,format2)
                        worksheet.write(row,col+2,e['apellidos'] ,format2)
                        worksheet.write(row,col+3,e['escolaridad'] ,format2)						
                        worksheet.write(row,col+4,e['cargo'] ,format2)
                        row +=1

                    workbook.close()
                
                    correo_contratista = CorreoContratista.objects.filter(contratista__id=c['contratista_id']).values()
                    correo_envio = ''	
                    con_copias = ''
                    if len(correo_contratista) > 0:
                        for cr in correo_contratista:
                            correo_envio = correo_envio + cr['correo'] + ';'

                    cursor.callproc('[dbo].[seguridad_social_responsable_proyecto_contratista]',[c['contratista_id'],7,c['empresa_id'] ])		
                    columns = cursor.description 
                    responsables_proyectos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]				
                    if len(responsables_proyectos) > 0:
                        for r in responsables_proyectos:
                            if len(correo_contratista) == 0:
                                correo_envio = correo_envio + r['correo']+';'
                            else:
                                con_copias = con_copias + r['correo']+';'	

                    if correo_envio != '':
                        correo_envio=correo_envio[:-1]	
                    if con_copias != '':
                        con_copias=con_copias[:-1]	

                    if correo_envio != '':
                        # cursor.callproc('[dbo].[seguridad_social_responsable_proyecto_contratista]',[c['contratista_id'],7,c['empresa_id'] ])		
                        # columns = cursor.description 
                        # responsables_proyectos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]					
                        # con_copias = ''
                        # for r in responsables_proyectos:
                        # 	con_copias=con_copias + r['correo']+';'

                        # correo_envio=correo_envio[:-1]	
                        # con_copias=con_copias[:-1]
                        contenido=''
                        # contenido='A quien se envia {} <br><br>'.format(correo_envio)
                        # contenido= contenido + 'Con copias {} <br><br>'.format(con_copias)					
                        asunto=''
                        interventora = unicode(c['interventora'])#str(c['interventora'].encode('utf-8')).decode('utf-8')
                        contratista = unicode(c['contratista'])#str(c['contratista'].encode('utf-8')).decode('utf-8')
                        if c['dias_vencidos']>=0:
                            asunto='Peticion: Pago y reporte de la seguridad social por vencer.'
                            contenido = contenido + '<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>';
                            contenido = contenido + 'Cordial Saludo<br/><br/> Se&ntilde;ores {0}'.format(contratista)					;
                            contenido = contenido + '<br/><br/>';
                            contenido = contenido + 'Me dirijo a ustedes con el fin de comunicarles que el d&iacute;a {} \
                                                    vence la seguridad social de la empresa, correspondiente al periodo {} - {}.<br><br>'.format(c['fecha_limite'],meses[int(c['mes'])-1],c['ano'])					
                                                
                            contenido = contenido + 'Por lo anterior se informa que el d&iacute;a {} \
                                                    deben presentar el pago de la planilla, debido a que esta informaci&oacute;n \
                                                    debe ser revisada y avalada. Si no recibimos a tiempo esta informaci&oacute;n, \
                                                    no tendran autorizaci&oacute;n por parte de la interventoria para continuar con las labores a partir del {} \
                                                    , se debe soportar planilla de seguridad social acompa&ntilde;ado del registro de personal en Excel.<br><br><br>'.format(c['dia_anterior'],c['dia_siguiente'])
                            
                            contenido = contenido + 'No siendo m&aacute;s la presente quedamos atentos.'
                            contenido = contenido + '<br><br><br>'
                            contenido = contenido + 'Favor no responder a esta direcci&oacute;n.'
                            contenido = contenido + '<br><br>'
                            contenido = contenido + 'Si presenta alguna inquietud, comunicarse con la firma interventora {}.'.format(interventora)
                            contenido = contenido + '<br><br><br>'
                            contenido = contenido +'Gracias,<br/><br/><br/></font>'
                            contenido = contenido +'Equipo SININ<br/>'
                            # contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
                        else:
                            asunto='Peticion: Pago y reporte de la seguridad social vencida.'
                            contenido= contenido + '<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>';
                            contenido = contenido + '<span style="color:#f80606">Cordial Saludo<br/><br/> Se&ntilde;ores {}'.format(contratista)
                            contenido = contenido + '<br/><br/>';
                            contenido = contenido + 'Me dirijo a ustedes con el fin de comunicarles que el d&iacute;a {} \
                                                    se vencio la seguridad social de la empresa, correspondiente al periodo {} - {}.<br><br>'.format(c['fecha_limite'], meses[int(c['mes'])-1],c['ano'])					
                                                
                            contenido = contenido + 'Por lo anterior se informa que a partir del d&iacute;a de hoy no est&aacute;n autorizados \
                                                    para continuar las actividades en campo, hasta que soporten el pago de la planilla con su respectivo registro de personal.'
                            
                            contenido = contenido + 'No siendo m&aacute;s la presente quedamos atentos.'
                            contenido = contenido + '<br><br><br>'
                            contenido = contenido + 'Favor no responder a esta direcci&oacute;n.'
                            contenido = contenido + '<br><br>'
                            contenido = contenido + 'Si presenta alguna inquietud, comunicarse con la firma interventora {}.'.format(interventora)
                            contenido = contenido + '<br><br><br>'
                            contenido = contenido +'Gracias,<br/><br/><br/></span></font>'
                            contenido = contenido +'Equipo SININ<br/>'

                            # contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'

                        mail = Mensaje(
                                remitente=settings.REMITENTE,
                                destinatario=correo_envio,
                                asunto=asunto,
                                contenido=contenido,
                                appLabel='seguridad_social',
                                tieneAdjunto=True,
                                adjunto=nombre_archivo,
                                copia=con_copias
                                )												
                        mail.Send()
                        
        except Exception as e:
            functions.toLog(e, 'seguridad_social.task.SeguridadSocialVencida')
            print(e)			
    
    @staticmethod
    def LicenciaPorVencer():
        cursor = connection.cursor()
        try:

            ruta = settings.STATICFILES_DIRS[0]
            rutaPapelera = ruta + '\papelera'
            cursor.callproc('[dbo].[seguridad_social_personal_licencia_por_vencer]')		
            columns = cursor.description 
            empleados = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
            
            if empleados:		
                cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[35,])#3 es el id de la notificacion 
                columns = cursor.description 
                personas_notificar = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
                correo_envio=None
                for p in personas_notificar:
                    correo_envio=None
                    #agrega el correo del destinatario
                    for e in empleados:
                        if p['empresa_id'] == e['empresa_id']:
                            correo_envio=p['correo']
                            break

                    if correo_envio:
                        contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
                        contenido = contenido + "Estimado usuario(a), <br/><br/>Adjunto envio, la relaci&oacute;n de empleados con la licencia de conducci&oacute;n por vencer<br/><br/>"		
                        contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
                        contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
                        
                        unique_filename = uuid.uuid4()
                        nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
                        workbook = xlsxwriter.Workbook(nombre_archivo)
                        worksheet = workbook.add_worksheet()

                        format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
                        format2=workbook.add_format({'border':1})
                        format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})

                        worksheet.write('A1','Contratista', format1)	
                        worksheet.write('B1','Cedula', format1)	
                        worksheet.write('C1','Nombres', format1)
                        worksheet.write('D1','Apellidos', format1)
                        worksheet.write('E1','Vencimiento de licencia', format1)

                        worksheet.set_column('A:A',30)
                        worksheet.set_column('B:B',15)
                        worksheet.set_column('C:C',30)
                        worksheet.set_column('D:D',30)
                        worksheet.set_column('E:E',20)
                        row=1
                        col=0
                        for e in empleados:
                            worksheet.write(row,col,e['contratista'] ,format2)
                            worksheet.write(row,col+1,e['cedula'] ,format2)
                            worksheet.write(row,col+2,e['nombres'] ,format2)
                            worksheet.write(row,col+3,e['apellidos'] ,format2)
                            worksheet.write(row,col+4,e['vencimiento_licencia'] ,format_date)						
                            row +=1

                        workbook.close()
                        mail = Mensaje(
                                remitente=settings.REMITENTE,
                                destinatario=correo_envio,
                                asunto='Licencia de conducción por vencer',
                                contenido=contenido,
                                appLabel='seguridad_social',
                                tieneAdjunto=True,
                                adjunto=nombre_archivo,
                                copia=''
                                )												
                        mail.Send()
                        # if os.path.exists(nombre_archivo):
                        # 	os.remove(nombre_archivo)

        except Exception as e:
            functions.toLog(e, 'seguridad_social.task.LicenciaPorVencer')
            print(e)
    
    @staticmethod
    def LicenciaVencida():
        cursor = connection.cursor()
        try:

            ruta = settings.STATICFILES_DIRS[0]
            rutaPapelera = ruta + '\papelera'
            cursor.callproc('[dbo].[seguridad_social_personal_licencia_vencida]')		
            columns = cursor.description 
            empleados = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
            
            if empleados:		
                cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[35,])
                columns = cursor.description 
                personas_notificar = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
            
                correo_envio=None
                for p in personas_notificar:
                    correo_envio=None
                    #agrega el correo del destinatario
                    for e in empleados:
                        if p['empresa_id'] == e['empresa_id']:
                            correo_envio=p['correo']
                            break

                    if correo_envio:
                        contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
                        contenido = contenido + "<p style='Color:#FF0404;'>Estimado usuario(a), <br/><br/>Adjunto envio, la relaci&oacute;n de empleados con la licencia de conducci&oacute;n vencida</p><br/><br/>"		
                        contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
                        contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
                        unique_filename = uuid.uuid4()
                        nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
                        workbook = xlsxwriter.Workbook(nombre_archivo)
                        worksheet = workbook.add_worksheet()

                        format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
                        format2=workbook.add_format({'border':1})
                        format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})

                        worksheet.write('A1','Contratista', format1)	
                        worksheet.write('B1','Cedula', format1)	
                        worksheet.write('C1','Nombres', format1)
                        worksheet.write('D1','Apellidos', format1)
                        worksheet.write('E1','Vencimiento de licencia', format1)

                        worksheet.set_column('A:A',30)
                        worksheet.set_column('B:B',15)
                        worksheet.set_column('C:C',30)
                        worksheet.set_column('D:D',30)
                        worksheet.set_column('E:E',20)
                        row=1
                        col=0
                        for e in empleados:
                            worksheet.write(row,col,e['contratista'] ,format2)
                            worksheet.write(row,col+1,e['cedula'] ,format2)
                            worksheet.write(row,col+2,e['nombres'] ,format2)
                            worksheet.write(row,col+3,e['apellidos'] ,format2)
                            worksheet.write(row,col+4,e['vencimiento_licencia'] ,format_date)						
                            row +=1

                        workbook.close()
                        mail = Mensaje(
                                remitente=settings.REMITENTE,
                                destinatario=correo_envio,
                                asunto='Licencia de conducción vencida',
                                contenido=contenido,
                                appLabel='seguridad_social',
                                tieneAdjunto=True,
                                adjunto=nombre_archivo,
                                copia=''
                                )												
                        mail.Send()
                        # if os.path.exists(nombre_archivo):
                        # 	os.remove(nombre_archivo)

        except Exception as e:
            functions.toLog(e, 'seguridad_social.task.LicenciaVencida')
            print(e)
    