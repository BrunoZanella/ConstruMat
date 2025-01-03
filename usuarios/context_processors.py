from django.db.models import Count, Q
from chat.models import Conversa

def notificacoes(request):
    if request.user.is_authenticated:
        conversas = Conversa.objects.filter(
            Q(pedido__cliente=request.user) |
            Q(pedido__empresa__usuario=request.user) |
            Q(pedido__motorista__usuario=request.user)
        ).annotate(
            mensagens_nao_lidas=Count(
                'mensagem',
                filter=Q(
                    mensagem__lida=False
                ) & ~Q(mensagem__remetente=request.user)
            )
        )
        mensagens_nao_lidas = sum(conversa.mensagens_nao_lidas for conversa in conversas)
    else:
        mensagens_nao_lidas = 0
    return {'mensagens_nao_lidas': mensagens_nao_lidas}
