from django.urls import path
from . import views


urlpatterns = [
    path('test/',views.form_request),
    path('form/',views.send_request),
    path('sender/',views.http_request),
    path('listener/',views.http_listener)
]