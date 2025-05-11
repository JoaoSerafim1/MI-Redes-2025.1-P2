from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
@csrf_exempt
def send_request(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        print("Data recebida:", data)

        return JsonResponse({'status': 'sucesso', 'data': data})
    elif request.method == 'GET':
        return render(request, 'form.html')
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


def receive_request(request):
    print(request.path)
    print(request.method)
    print(request.GET)
    return HttpResponse('Requisição recebida')

def form_request(request):
    return render(request,'form.html')

    