"""
URL configuration for mm_pipas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from app.views import client_create, client_list, product_delete, product_list, product_update

urlpatterns = [
    path('', TemplateView.as_view(template_name='menu.html'), name='menu'),
    path('produtos/', product_list, name='produtos'),
    path('clientes/', client_list, name='clientes'),
    path('clientes/novo/', client_create, name='cliente_novo'),
    path('produtos/<int:product_id>/alterar/', product_update, name='produto_alterar'),
    path('produtos/<int:product_id>/excluir/', product_delete, name='produto_excluir'),
    path('admin/', admin.site.urls),
]
