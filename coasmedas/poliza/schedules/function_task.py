# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from coasmedas.celery import app
from adminMail.models import Mensaje
from django.db import transaction, connection
import uuid
from django.conf import settings
import os
import xlsxwriter
from contrato.models import Contrato, EmpresaContrato
from coasmedas.functions import functions
from poliza.models import Poliza

class FunctionTask:

    @staticmethod   
    def PolizaPorVencer():
        cursor = connection.cursor()
        try:
            cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[9,])
            columns = cursor.description 
            personas_notificar = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
            
            for fun in personas_notificar:
                cursor.callproc('[dbo].[poliza_vigencia_poliza_por_vencer]',[fun['funcionario_id'],])
                columns = cursor.description 
                todasPolizas = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
                
                polizas = []
                for	pol in todasPolizas:
                    poliza = Poliza.objects.get(pk=pol['id'])
                    verificar = esSoloLectura(poliza.contrato, fun['empresa_id'])
                    if verificar == False:
                        polizas.append(pol)

                if polizas:
                    contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
                    contenido = contenido + "Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes  polizas estan <strong>por vencer</strong>:<br/><br/>"		
                    
                    contenido = contenido + '<table border=1>';							
                    contenido = contenido + '<tr bgcolor="#DED9D9"><td>Contrato macro</td><td>No. Contrato</td><td>Nombre</td><td>Contratista</td><td>Tipo poliza</td><td>Fecha Fin</td></tr>';	

                    for pol in polizas:
                        
                        contenido = contenido + '<tr>';							
                        contenido = contenido + '<td>{}</td>'.format(pol['mcontrato'])
                        contenido = contenido + '<td>{}</td>'.format(pol['numero'])
                        contenido = contenido + '<td>{}</td>'.format(pol['contrato'])
                        contenido = contenido + '<td>{}</td>'.format(pol['contratista'])
                        contenido = contenido + '<td>{}</td>'.format(pol['tipo_poliza'])
                        contenido = contenido + '<td>{}</td>'.format(pol['fecha_final'])
                        contenido = contenido + '</tr>';
                    
                    contenido=contenido + '</table><br/><br/>'
                                

                    contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
                    contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
                    
                    mail = Mensaje(
                                remitente=settings.REMITENTE,
                                destinatario=fun['correo'],
                                asunto='Vigencias polizas por vencer',
                                contenido=contenido,
                                appLabel='poliza',							
                                copia=''
                                )												
                    mail.simpleSend()

        except Exception as e:
            functions.toLog(e, 'poliza.task.PolizaPorVencer')
            print(e)	

    @staticmethod   
    def PolizaVencida():
        cursor = connection.cursor()
        try:
            cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[9,])
            columns = cursor.description 
            personas_notificar = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
            
            for fun in personas_notificar:
                cursor.callproc('[dbo].[poliza_vigencia_poliza_vencida]',[fun['funcionario_id'],])
                columns = cursor.description 
                todasPolizas = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
                
                polizas = []
                for	pol in todasPolizas:
                    poliza = Poliza.objects.get(pk=pol['id'])
                    verificar = esSoloLectura(poliza.contrato, fun['empresa_id'])
                    if verificar == False:
                        polizas.append(pol)
                        
                if polizas:
                    contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
                    contenido = contenido + "Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes polizas estan <strong>vencidas</strong>:<br/><br/>"		
                    
                    contenido = contenido + '<table border=1>';							
                    contenido = contenido + '<tr bgcolor="#DED9D9"><td>Contrato macro</td><td>No. Contrato</td><td>Nombre</td><td>Contratista</td><td>Tipo poliza</td><td>Fecha Fin</td></tr>';	

                    for pol in polizas:
                        
                        contenido = contenido + '<tr>';							
                        contenido = contenido + '<td>{}</td>'.format(pol['mcontrato'])
                        contenido = contenido + '<td>{}</td>'.format(pol['numero'])
                        contenido = contenido + '<td>{}</td>'.format(pol['contrato'])
                        contenido = contenido + '<td>{}</td>'.format(pol['contratista'])
                        contenido = contenido + '<td>{}</td>'.format(pol['tipo_poliza'])
                        contenido = contenido + '<td>{}</td>'.format(pol['fecha_final'])
                        contenido = contenido + '</tr>';
                    
                    contenido=contenido + '</table><br/><br/>'
                                

                    contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
                    contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
                    
                    mail = Mensaje(
                                remitente=settings.REMITENTE,
                                destinatario=fun['correo'],
                                asunto='Vigencias polizas vencida',
                                contenido=contenido,
                                appLabel='poliza',							
                                copia=''
                                )												
                    mail.simpleSend()

        except Exception as e:
            functions.toLog(e, 'poliza.task.PolizaVencida')
            print(e)				

    @staticmethod   
    def ActualizarEstadoPoliza():	
        cursor = connection.cursor()
        try:
            
            cursor.callproc('[dbo].[poliza_actualizar_estado]')		
            return True		
                    
        except Exception as e:
            functions.toLog(e, 'poliza.task.ActualizarEstadoPoliza')
            print(e)		


def esSoloLectura(contratoObj, empresa):
	if contratoObj.mcontrato:
		contrato = contratoObj.mcontrato.id
	else:
		contrato = contratoObj.id

	empresaContrato = EmpresaContrato.objects.filter(contrato__id=contrato, empresa__id=empresa).first()
	soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
	return soloLectura