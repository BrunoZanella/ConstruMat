from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro_empresa, name='cadastro_empresa'),
#    path('<int:empresa_id>/', views.empresa_detalhes, name='empresa_detalhes'),
    path('<int:empresa_id>/editar/', views.editar_empresa, name='editar_empresa'),
    path('<int:empresa_id>/produtos/', views.gerenciar_produtos, name='gerenciar_produtos'),
    path('<int:empresa_id>/produtos/novo/', views.novo_produto, name='novo_produto'),
    path('<int:empresa_id>/produtos/<int:produto_id>/editar/', views.editar_produto, name='editar_produto'),
    path('empresas/<int:empresa_id>/', views.empresa_detalhes, name='empresa_detalhes'),
]