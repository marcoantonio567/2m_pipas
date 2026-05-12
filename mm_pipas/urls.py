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

from app.views import (
    client_create,
    client_delete,
    client_list,
    client_update,
    financial_category_create,
    financial_category_delete,
    financial_category_list,
    financial_category_update,
    product_create,
    product_delete,
    product_list,
    product_update,
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='menu.html'), name='menu'),
    path('produtos/', product_list, name='produtos'),
    path('produtos/novo/', product_create, name='produto_novo'),
    path('clientes/', client_list, name='clientes'),
    path('clientes/novo/', client_create, name='cliente_novo'),
    path('clientes/<int:client_id>/alterar/', client_update, name='cliente_alterar'),
    path('clientes/<int:client_id>/excluir/', client_delete, name='cliente_excluir'),
    path('produtos/<int:product_id>/alterar/', product_update, name='produto_alterar'),
    path('produtos/<int:product_id>/excluir/', product_delete, name='produto_excluir'),
    path('financeiro/categorias/', financial_category_list, name='financeiro_categorias'),
    path('financeiro/categorias/nova/', financial_category_create, name='financeiro_categoria_nova'),
    path('financeiro/categorias/<int:category_id>/alterar/', financial_category_update, name='financeiro_categoria_alterar'),
    path('financeiro/categorias/<int:category_id>/excluir/', financial_category_delete, name='financeiro_categoria_excluir'),
    path('admin/', admin.site.urls),
]
