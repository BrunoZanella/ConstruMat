# Generated by Django 5.0.1 on 2025-01-06 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0003_pedido_finalizado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='finalizado',
        ),
    ]
