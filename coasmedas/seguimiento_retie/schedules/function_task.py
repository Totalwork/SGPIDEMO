from adminMail.models import Mensaje
from django.db import transaction, connection
from django.conf import settings

class FunctionTask:

    @staticmethod
    def EnviarCorreoVisitasNoProgramadas():	
        cursor = connection.cursor()
        try:
            
            cursor.callproc('[dbo].[retie_funcionarios_proyecto]')		
            columns = cursor.description 
            funcionarios = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

            for f in funcionarios:	
                cursor.callproc('[dbo].[retie_consultar_visitas_sin_programar]',[f['funcionario_id'],])
                columns = cursor.description 
                visitas = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
                for v in visitas:
                    contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
                    contenido = contenido + 'Se&ntilde;or Usuario(a) {} {}<br/><br/>'.format(f['nombres'], f['apellidos'])																
                                                            
                    contenido = contenido + 'Los siguientes proyectos han alcanzado el porcentaje de avance de \
                                            obra minimo para iniciar el proceso de certificacion RETIE. por tal \
                                            razon Nos permitimos comunicarle que los siguientes estan en estado \
                                            <b>Pendiente por Programar la </b> visita RETIE: <br/>'
                    
                    contenido = contenido + '<br><br><br>';
                    contenido = contenido + '<table border="1" cellpadding="2" cellspacing="2">'
                    contenido = contenido + '<tr> \
                                                <th valign="top">Macro-contrato</th> \
                                                <th valign="top">Departamento</th> \
                                                <th valign="top">Municipio</th> \
                                                <th valign="top">Proyecto</th>\
                                            </tr>'
                    
                    contenido = contenido + '<tr>\
                                                <td>{}</td>\
                                                <td>{}</td>\
                                                <td>{}</td>\
                                                <td>{}</td>\
                                            </tr>'.format(v['numero'],
                                                            v['departamento'],
                                                            v['municipio'],
                                                            v['proyecto'])	
                    contenido = contenido + '</table>';	
                    contenido = contenido + '<br><br>No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
                    contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
                    
                    mail = Mensaje(
                                remitente=settings.REMITENTE,
                                destinatario=f['correo'],
                                asunto='Programacion de Visita RETIE',
                                contenido=contenido,
                                appLabel='seguimiento_retie',
                                )												
                    return mail.simpleSend()
                    
        except Exception as e:
            print(e)
       
    @staticmethod
    def GuardarVisitasRetie():	
        cursor = connection.cursor()
        try:
            
            cursor.callproc('[dbo].[retie_funcionarios_proyecto]')		
            return True		
                    
        except Exception as e:
            print(e)
