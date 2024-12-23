from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer 
from rest_framework.permissions import AllowAny 
# Create your views here.

class MyindexView(APIView): 
    permission_classes = [AllowAny] 
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'fronthtml/index.html'
  
    def get(self, request):
          return render(request, 'fronthtml/index.html') 
      
      
class login_signup_view(APIView): 
    permission_classes = [AllowAny] 
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'fronthtml/Login_Sign.Html'
  
    def get(self, request):
          return render(request, 'fronthtml/Login_Sign.Html')     
 