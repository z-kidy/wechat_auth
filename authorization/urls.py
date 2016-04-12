
from django.conf.urls import url
from authorization import views

urlpatterns = [
    url(r'^code/$', views.get_code),        
]
