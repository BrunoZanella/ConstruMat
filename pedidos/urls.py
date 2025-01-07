from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pedidos, name='pedidos'),
    path('novo/<int:empresa_id>/', views.novo_pedido, name='novo_pedido'),
    path('<int:pedido_id>/', views.detalhes_pedido, name='detalhes_pedido'),
    path('<int:pedido_id>/avaliar/', views.avaliar_pedido, name='avaliar_pedido'),
    path('motorista/', views.pedidos_motorista, name='pedidos_motorista'),
#    path('motorista/<int:pedido_id>/aceitar/', views.aceitar_pedido, name='aceitar_pedido'),

    path('atualizar-status-corrida/<int:pedido_id>/<str:novo_status>/', views.atualizar_status_corrida, name='atualizar_status_corrida'),

    path('<int:pedido_id>/recibo/', views.recibo_pedido, name='recibo_pedido'),
    path('<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
    path('<int:pedido_id>/aceitar/', views.aceitar_pedido, name='aceitar_pedido'),
    path('<int:pedido_id>/retirar/', views.retirar_pedido, name='retirar_pedido'),
    path('<int:pedido_id>/entregar/', views.entregar_pedido, name='entregar_pedido'),
    
]
