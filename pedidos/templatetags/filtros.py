from django import template

register = template.Library()

@register.filter
def sum_total(itens):
    """
    Calcula o total de um conjunto de itens.
    Cada item deve ter `quantidade` e `preco_unitario`.
    """
    return sum(item.quantidade * item.preco_unitario for item in itens)
