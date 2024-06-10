from django.shortcuts import render
#, render_to_response
from django.shortcuts import redirect


def error_404(request, exception):
	return render(request,'error_404.html', status=404)

def error_500(request):
	return render(request,'error_500.html', context={})

def sitio_construccion(request):
	return render(request,'sitio_en_construccion.html')


def inicio(request):
	return redirect('/usuario/login/')