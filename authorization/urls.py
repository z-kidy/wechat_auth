
from django.conf.urls import url
from authorization import views

urlpatterns = [
    url(r'^code$', views.get_code, name='get_code'),
    url(r'^web_auth$', views.web_auth, name='web_auth'),        
]
