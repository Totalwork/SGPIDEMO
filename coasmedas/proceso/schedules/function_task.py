from adminMail.models import Mensaje
from proceso.models import INotificacionVencimiento, BItem, GProcesoRelacionDato
from parametrizacion.models import Funcionario
from proyecto.models import Proyecto
from contrato.models import Contrato
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.conf import settings

class FunctionTask:

    @staticmethod
    def vencimientoItems():
        #import pdb; pdb.set_trace()

        qset=((Q(estado=2) | Q(estado=3)) & 
            (Q(item__notificacionCumplimiento=2) | Q(item__notificacionCumplimiento=3)))
        itemsConVigencia = GProcesoRelacionDato.objects.filter(qset).values('id','procesoRelacion__id',
            'procesoRelacion__proceso__nombre','item__descripcion','fechaVencimiento','estado',
            'item__notificacionCumplimiento','procesoRelacion__proceso__apuntador',
            'procesoRelacion__idApuntador','procesoRelacion__idTablaReferencia',
            'procesoRelacion__proceso__etiqueta','procesoRelacion__proceso__tablaForanea__id',
            'procesoRelacion__proceso__campoEnlaceTablaForanea')
        excluye=[]
        funcionarios=[]
        retorno=''
        #detectar funcionarios a los que se van a notificar, permite conocer la cantidad de correos a enviar
        for it in itemsConVigencia:
            funcionariosAnotificar=[]
            if it['item__notificacionCumplimiento']=='3':
                #buscar los funcionarios de las notificaciones configuradas
                funcionariosAnotificar = INotificacionVencimiento.objects.filter(procesoRelacionDato__id=it['id'],funcionario__activo=1).values(
                    'funcionario__id','funcionario__persona__correo','funcionario__persona__nombres',
                    'funcionario__persona__apellidos')
            else:
                #buscar los responsables del proyecto/contrato	
                qset=None
                qset = (~Q(id=0))
                if it['procesoRelacion__proceso__apuntador']=='1':
                    #proceso apuntado en funcion de un proyecto
                    qset= qset & (Q(id=it['procesoRelacion__idApuntador']))
                elif it['procesoRelacion__proceso__apuntador']=='2':	
                    #proceso auntado en funcion de un contrato
                    qset = qset & (Q(contrato__id=it['procesoRelacion__idApuntador']))
                #print qset
                qset = qset & (Q(funcionario__activo=1))	
                queryset=Proyecto.objects.filter(qset)
                funcionariosAnotificar = queryset.values('funcionario__id',
                    'funcionario__persona__correo', 'funcionario__persona__nombres',
                    'funcionario__persona__apellidos')
                
            for fun in funcionariosAnotificar:
                encontrado=False
                for x in funcionarios:
                    if x['id']==fun['funcionario__id']:
                        x['notificacion'].append(it)
                        encontrado=True
                if not encontrado:
                    funcionarios.append({'id':fun['funcionario__id'],'funcionario':fun,'notificacion':[it]})
                    
            #retorno = retorno + fun['funcionario__persona__nombres'] + ' ' +fun['funcionario__persona__apellidos']+' - '+fun['funcionario__persona__correo'] + '\n'
        #iniciar secuencias de envio de correos
        total=''
        for funcionario in funcionarios:
            contenido=''
            contenido='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
            contenido = contenido + 'Sr(a). ' + funcionario['funcionario']['funcionario__persona__nombres']
            contenido = contenido + ' ' + funcionario['funcionario']['funcionario__persona__apellidos'] + '.<br/><br/>'
            contenido = contenido + 'Nos permitimos notificarle que tiene items por vencer y/o vencidos sobre los siguientes seguimientos:<br/><br/>'
            contenido = contenido + '<table border=1>'
            contenido = contenido + '<tr><th>Departamento</th><th>Municipio</th><th>Proyecto</th><th>No. contrato</th><th>Nombre contrato</th><th>Seguimiento</th><th>Item</th><th>Elemento analizado</th><th>Estado</th><th>Fecha vencimiento</th></tr>'
            contenido = contenido + '<tr>'
            for notificacion in funcionario['notificacion']:
                if notificacion['procesoRelacion__proceso__apuntador']=='1':
                    proyecto = Proyecto.objects.filter(id=notificacion['procesoRelacion__idApuntador']).values(
                        'municipio__departamento__nombre','municipio__nombre','nombre')
                    contenido= contenido + '<td>'+proyecto[0]['municipio__departamento__nombre']+'</td>'
                    contenido= contenido + '<td>'+proyecto[0]['municipio__nombre']+'</td>'
                    contenido= contenido + '<td>'+proyecto[0]['nombre']+'</td>'
                    contenido = contenido + '<td>No aplica</td>'
                    contenido = contenido + '<td>No aplica</td>'
                else:
                    contrato = Contrato.objects.filter(id=notificacion['procesoRelacion__idApuntador']).values(
                        'numero','nombre')
                    contenido = contenido + '<td>No aplica</td>'
                    contenido = contenido + '<td>No aplica</td>'
                    contenido = contenido + '<td>No aplica</td>'
                    contenido = contenido + '<td>'+contrato[0]['numero']+'</td>'
                    contenido = contenido + '<td>'+contrato[0]['nombre']+'</td>'				
                contenido = contenido + '<td>' + notificacion['procesoRelacion__proceso__nombre']+'</td>'
                contenido = contenido + '<td>' + notificacion['item__descripcion']+'</td>'
                if notificacion['procesoRelacion__proceso__tablaForanea__id']:
                    modeloReferencia = ContentType.objects.get(pk=notificacion['procesoRelacion__proceso__tablaForanea__id']).model_class()
                    elemento = modeloReferencia.objects.filter(id=notificacion['procesoRelacion__idTablaReferencia']).values(
                        notificacion['procesoRelacion__proceso__etiqueta'])
                    contenido = contenido + '<td>'
                    contenido = contenido + elemento[0][notificacion['procesoRelacion__proceso__etiqueta']]
                    contenido = contenido + '</td>'
                else:
                    contenido = contenido + '<td>No aplica</td>'
                estado = 'Vencido'	
                if 	notificacion['estado']=='2':
                    estado='Por vencer'
                contenido = contenido + '<td>' + estado + '</td>'
                contenido = contenido + '<td>' + notificacion['fechaVencimiento'].strftime('%m/%d/%Y') + '</td>'
                contenido = contenido + '</tr>'	
            contenido= contenido + '</table>'
            #Iniciar secuencia de envio de correo:
            mail = Mensaje(
                remitente=settings.REMITENTE,
                destinatario=funcionario['funcionario']['funcionario__persona__correo'],
                asunto='Notificacion de vencimiento en items de seguimientos',
                contenido=contenido,
                appLabel='Proceso',
            )
            mail.save()	
            # print funcionario['funcionario']['funcionario__persona__nombres'] + ' ' + funcionario['funcionario']['funcionario__persona__apellidos']
            # print  funcionario['funcionario']['funcionario__persona__correo']					
            # print mail.contenido
            res=mail.simpleSend()			
