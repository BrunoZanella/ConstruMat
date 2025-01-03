from django.urls import path
from . import views

urlpatterns = [
    path('pedido/<int:pedido_id>/', views.conversa_pedido, name='chat_pedido'),
]