#Lista de mcontratos por empresa
def listContrato(request):
	try:
		# queryset = super(ContratoViewSet ).get_queryset()
		queryset=None
		tipo = request.GET['tipo']
		# empresa = request.GET['empresa']
		empresa = request.user.usuario.empresa.id
		if (tipo or empresa):
			if tipo:
				qset = (
					Q(contrato__tipo_contrato=tipo)
					)
			if empresa:
				qset = qset &(
					#Q(empresa_contrato__empresa_id=empresa)
					Q(empresa=empresa) & Q(participa=1)
					)

			queryset = Empresa_contrato.objects.filter(qset)
			# queryset = model_c.objects.filter(qset)
		# queryset = model_c.objects.all()

		lista=[] 
		for item in list(queryset):
			valor={
				'id':item.contrato.id,
				'nombre':item.contrato.nombre,
				'numero':item.contrato.numero
				#'logo':unicode(item.logo)
			}
		print (json.dumps(valor))
		lista.append(valor)
			
		# serializer = get_serializer(queryset,many=True)			
		return JsonResponse({'message':'','success':'ok','data':lista})
	except Exception as e:
		print(e)
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)