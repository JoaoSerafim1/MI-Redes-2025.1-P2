from django.urls import path
from . import views

urlpatterns = [
    path('test',views.receive_request)
]