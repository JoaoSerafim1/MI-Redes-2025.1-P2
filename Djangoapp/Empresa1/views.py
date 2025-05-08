from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def receive_request(request):
    return HttpResponse('Requisição recebida')
