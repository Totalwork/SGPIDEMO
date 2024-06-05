from django.db import connection
from giros.models import DEncabezadoGiro,DetalleGiro
from adminMail.models import Mensaje
from django.conf import settings
from usuario.models import Persona
from django.db.models import Sum
import uuid
import xlsxwriter
import os

class FunctionTask:

    @staticmethod   
    def envioCorreoGiroPorContabilizar():
        try:
            ruta = settings.STATICFILES_DIRS[0]
            rutaPapelera = ruta + '\papelera'
            cursor = connection.cursor()
            cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[39,])
            columns = cursor.description 
            LisCorreos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

            correo_envio=''
            for p in LisCorreos:
                correo_envio=p['correo']

                encabezados=DEncabezadoGiro.objects.filter(disparar_flujo=True,referencia__exact='')

                contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
                contenido = contenido + "Estimado usuario(a),<br /><br /> Nos permitimos comunicarle que se encontraron "+str(len(encabezados))+" solicitud(es) de giro(s) pendiente(s) por contabilizar, Se adjunta el archivo para su informaci&oacute;n. Cualquier duda por favor comun&iacute;quese con la interventor&iacute;a correspondiente."		
                contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
                contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'


                unique_filename = uuid.uuid4()
                nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
                workbook = xlsxwriter.Workbook(nombre_archivo)
                worksheet = workbook.add_worksheet('Todos')
                format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
                format1.set_align('center')
                format1.set_align('vcenter')
                format2=workbook.add_format({'border':0})
                
                worksheet.set_column('A:AF', 30)
                
                row=1
                col=0

                worksheet.write('A1', 'Nombre contrato', format1)
                worksheet.write('B1', 'Nombre de giro', format1)
                worksheet.write('C1', 'Total giro', format1)
                worksheet.write('D1', 'No. radicado', format1)

                if len(encabezados)>0:
                    for item in encabezados:
                        worksheet.write(row,col, item.contrato.nombre,format2)
                        worksheet.write(row,col+1, item.nombre.nombre,format2)

                        sumatoria=DetalleGiro.objects.filter(encabezado_id=item.id).aggregate(suma_detalle=Sum('valor_girar'))		
                            
                        worksheet.write(row,col+2, sumatoria['suma_detalle'],format2)
                        worksheet.write(row,col+3, item.numero_radicado,format2)

                        row +=1			
                
                    workbook.close()
                    mail = Mensaje(
                                remitente=settings.REMITENTE,
                                destinatario=correo_envio,
                                asunto='Solicitudes de giro pendientes por contabilizar',
                                contenido=contenido,
                                appLabel='giros',
                                tieneAdjunto=True,
                                adjunto=nombre_archivo,
                                copia=''
                                )												
                    mail.Send()
                    if os.path.exists(nombre_archivo):
                        os.remove(nombre_archivo)

            #mail.simpleSend()

        except Exception as e:
            print(e)

        finally:
            cursor.close()

    @staticmethod
    def envioCorreoGiroPorContabilizarProcesar():
        try:
            ruta = settings.STATICFILES_DIRS[0]
            rutaPapelera = ruta + '\papelera'
            cursor = connection.cursor()
            cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[40,])
            columns = cursor.description 
            LisCorreos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

            correo_envio=''
            for p in LisCorreos:
                correo_envio=p['correo']

                encabezados=DEncabezadoGiro.objects.filter(disparar_flujo=True,referencia__exact='',flujo_test=False)

                contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
                contenido = contenido + "Estimado usuario(a),<br /><br /> Nos permitimos comunicarle que se encontraron "+str(len(encabezados))+" solicitud(es) de giro(s) pendiente(s) contabilizadas pendientes por procesar, Se adjunta el archivo para su informaci&oacute;n. Cualquier duda por favor comun&iacute;quese con la interventor&iacute;a correspondiente."		
                contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
                contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'


                unique_filename = uuid.uuid4()
                nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
                workbook = xlsxwriter.Workbook(nombre_archivo)
                worksheet = workbook.add_worksheet('Todos')
                format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
                format1.set_align('center')
                format1.set_align('vcenter')
                format2=workbook.add_format({'border':0})
                
                worksheet.set_column('A:AF', 30)
                
                row=1
                col=0

                worksheet.write('A1', 'Documento sap', format1)
                worksheet.write('B1', 'Macrocontrato', format1)
                worksheet.write('C1', 'Nombre contrato', format1)
                worksheet.write('D1', 'Numero de contrato',format1)
                worksheet.write('E1', 'Nombre de giro',format1)
                worksheet.write('F1', 'Total de giro',format1)

                if len(encabezados)>0:
                    for item in encabezados:
                        worksheet.write(row,col, item.referencia,format2)
                        worksheet.write(row,col+1, item.contrato.mcontrato,format2)
                        worksheet.write(row,col+2, item.contrato.nombre,format2)
                        worksheet.write(row,col+3, item.contrato.numero,format2)
                        worksheet.write(row,col+4, item.nombre.nombre,format2)

                        sumatoria=DetalleGiro.objects.filter(encabezado_id=item.id).aggregate(suma_detalle=Sum('valor_girar'))		
                            
                        worksheet.write(row,col+5, sumatoria['suma_detalle'],format2)

                        row +=1			
                
                    workbook.close()
                    mail = Mensaje(
                                remitente=settings.REMITENTE,
                                destinatario=correo_envio,
                                asunto='Solicitudes de giro contabilizadas pendientes por procesar',
                                contenido=contenido,
                                appLabel='giros',
                                tieneAdjunto=True,
                                adjunto=nombre_archivo,
                                copia=''
                                )												
                    mail.Send()
                    if os.path.exists(nombre_archivo):
                        os.remove(nombre_archivo)

            #mail.simpleSend()

        except Exception as e:
            print(e)

        finally:
            cursor.close()

    @staticmethod
    def envioCorreoOrdenPagoProcesar():
        try:
            ruta = settings.STATICFILES_DIRS[0]
            rutaPapelera = ruta + '\papelera'
            cursor = connection.cursor()
            cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[41,])
            columns = cursor.description 
            LisCorreos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

            correo_envio=''
            for p in LisCorreos:
                correo_envio=p['correo']

                encabezados=DEncabezadoGiro.objects.filter(disparar_flujo=True,referencia__exact='',flujo_test=False)

                contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
                contenido = contenido + "Estimado usuario(a),<br /><br /> Nos permitimos comunicarle que se encontraron ordenes de pago pendientes por procesar, Se adjunta el archivo para su informaci&oacute;n. Cualquier duda por favor comun&iacute;quese con la interventor&iacute;a correspondiente."		
                contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
                contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'


                unique_filename = uuid.uuid4()
                nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
                workbook = xlsxwriter.Workbook(nombre_archivo)
                worksheet = workbook.add_worksheet('Todos')
                format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
                format1.set_align('center')
                format1.set_align('vcenter')
                format2=workbook.add_format({'border':0})
                
                worksheet.set_column('A:AF', 30)
                
                row=1
                col=0

                worksheet.write('A1', 'Documento sap', format1)
                worksheet.write('B1', 'Macrocontrato', format1)
                worksheet.write('C1', 'Nombre contrato', format1)
                worksheet.write('D1', 'Numero de contrato',format1)
                worksheet.write('E1', 'Contratista',format1)
                worksheet.write('F1', 'Nombre de giro',format1)
                worksheet.write('G1', 'Total de giro',format1)

                sw=0

                if len(encabezados)>0:
                    for item in encabezados:
                        detalle=DetalleGiro.objects.filter(encabezado_id=item.id,test_op__exact='')

                        if len(detalle)>0:
                            sw=1

                            worksheet.write(row,col, item.referencia,format2)
                            worksheet.write(row,col+1, item.contrato.mcontrato,format2)
                            worksheet.write(row,col+2, item.contrato.nombre,format2)
                            worksheet.write(row,col+3, item.contrato.numero,format2)
                            worksheet.write(row,col+4, item.contrato.contratista.nombre,format2)
                            worksheet.write(row,col+5, item.nombre.nombre,format2)

                            sumatoria=DetalleGiro.objects.filter(encabezado_id=item.id).aggregate(suma_detalle=Sum('valor_girar'))		
                                
                            worksheet.write(row,col+6, sumatoria['suma_detalle'],format2)

                            row +=1	

                    if sw==1:
                        workbook.close()
                        mail = Mensaje(
                                    remitente=settings.REMITENTE,
                                    destinatario=correo_envio,
                                    asunto='Solicitudes de giro contabilizadas pendientes por procesar',
                                    contenido=contenido,
                                    appLabel='giros',
                                    tieneAdjunto=True,
                                    adjunto=nombre_archivo,
                                    copia=''
                                    )												
                        mail.Send()
                        if os.path.exists(nombre_archivo):
                            os.remove(nombre_archivo)

            #mail.simpleSend()

        except Exception as e:
            print(e)

        finally:
            cursor.close()
