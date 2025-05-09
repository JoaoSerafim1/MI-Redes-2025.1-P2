from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def send_request(request):
    return HttpResponse('Requisição enviada')

def receive_request(request):
    print(request.path)
    print(request.method)
    print(request.GET)
    return HttpResponse('Requisição recebida')

def form_request(request):
    return render(request,'form.html')