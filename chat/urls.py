from django.urls import path
from . import views

urlpatterns = [
    path('lista_conversas/', views.lista_conversas, name='conversas'),
    path('pedido/<int:pedido_id>/', views.conversa_pedido, name='chat_pedido'),
    path('atualizar/<int:conversa_id>/', views.atualizar_mensagens, name='atualizar_mensagens'),
]