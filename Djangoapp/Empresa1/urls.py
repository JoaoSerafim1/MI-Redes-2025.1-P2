from django.urls import path
from . import views


urlpatterns = [
    path('test/',views.form_request),
    path('form/',views.send_request)
]