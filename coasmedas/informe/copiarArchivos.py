
lista=[
{'nodo':2002501,'fotoinicial':'DSC01452','fotofinal':'DSC01462'},
{'nodo':2002624,'fotoinicial':'DSC02938','fotofinal':'DSC02948'},
{'nodo':2002625,'fotoinicial':'DSC02949','fotofinal':'DSC02958'},
{'nodo':2002626,'fotoinicial':'DSC02959','fotofinal':'DSC02976'},
{'nodo':2002627,'fotoinicial':'DSC02977','fotofinal':'DSC02981'},
{'nodo':2002628,'fotoinicial':'DSC02982','fotofinal':'DSC02993'}]

from django.http import HttpResponse,JsonResponse
import os

def copiarArchivos(request):
	
	data = []
	i = 0
	for item in lista:
		# print item
		fotoinicial = item['fotoinicial']	
		fotofinal = item['fotofinal']
		nodo 	= item['nodo']	
		inicio 	= int(''.join([i for i in fotoinicial if i.isdigit()]))
		fin 	= int(''.join([i for i in fotofinal if i.isdigit()]))
		letter 	= ''.join([i for i in fotoinicial if not i.isdigit()])
		
		for num in range(inicio, fin + 1):
			ceros = ''
			for i in range(len(str(inicio)), 5):
				ceros = ceros + '0'

			a = '{}{}{}.jpg'.format(letter, ceros, num)	
			if os.path.exists('D:/proyectos_totalwork/migracion survey 072019/Cartagenea del chaira/fotos/{}'.format(a)):
				data.append({'nodo': nodo, 'foto': a})


	return JsonResponse({'message':'','success':'ok','data': data})	

lista3 =[
	{'id':20395,'nodo':161846},
	{'id':20396,'nodo':161846},
	{'id':20397,'nodo':161846},
	{'id':20398,'nodo':161846},
	{'id':20399,'nodo':161846},
	{'id':20400,'nodo':161846},
	{'id':20401,'nodo':161846},
	{'id':20402,'nodo':161846},
	{'id':20403,'nodo':161846},
	{'id':20404,'nodo':161846},
	{'id':20405,'nodo':161845},
	{'id':20406,'nodo':161844},
	{'id':20407,'nodo':161843},
	{'id':20408,'nodo':161847}
]
def crearLineasInfoTecnicaEQ(request):
	lista2 = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 74, 50]	
	i = 0
	data = []
	for item in lista3:
		j = 0
		k = 0
		f = [55,188,186,187]
		for n in lista2:
			it = item.copy()			
			it['infotec'] = n
			it['valor'] = ''
			if n == 40:
				it['valor'] = f[j]
				j = j + 1
			if n == 41:
				it['valor'] = 'ND'
			if n == 42:
				it['valor'] = 1	
			if n == 43:
				it['valor'] = 1
			if n == 44:
				it['valor'] = 108	
			if n == 45:
				it['valor'] = it['nodo']
			if n == 46:
				it['valor'] = 'ND'	
			if n == 50:
				it['valor'] = 5
			if n == 74:
				it['valor'] = it['nodo']

			data.append(it)
			
	return JsonResponse({'message':'','success':'ok','data': data})		

lista4 = [
{'id':14497,'nodo':164501},
{'id':14498,'nodo':164502},
{'id':14499,'nodo':164503},
{'id':14500,'nodo':164504},
{'id':14501,'nodo':164505},
{'id':14502,'nodo':164506},
{'id':14503,'nodo':164507},
{'id':14504,'nodo':164508},
{'id':14505,'nodo':164509},
{'id':14506,'nodo':164510}
]
def crearLineasInfoTecnicaAT(request):
	lista2 = [53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73]	
	i = 0
	data = []
	for item in lista4:
		j = 0
		k = 0
		# f = [55,188,186,187]
		for n in lista2:
			it = item.copy()			
			it['infotec'] = n
			it['valor'] = ''
			# if n == 40:
			# 	it['valor'] = f[j]
			# 	j = j + 1
			# if n == 41:
			# 	it['valor'] = 'ND'
			# if n == 42:
			# 	it['valor'] = 1	
			# if n == 43:
			# 	it['valor'] = 1
			# if n == 44:
			# 	it['valor'] = 108	
			# if n == 45:
			# 	it['valor'] = it['nodo']
			# if n == 46:
			# 	it['valor'] = 'ND'	
			# if n == 50:
			# 	it['valor'] = 5
			# if n == 74:
			# 	it['valor'] = it['nodo']

			data.append(it)
			
	return JsonResponse({'message':'','success':'ok','data': data})			