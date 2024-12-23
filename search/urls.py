from django.urls import path ,re_path
from .views import *  
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)  


urlpatterns = [
      path('', MyindexView.as_view(), name='index'), 
      path('loginpage/', login_signup_view.as_view(), name='login_signup'),
      

] 

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)