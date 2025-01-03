from django.db import models
from usuarios.models import Usuario

class TipoEmpresa(models.Model):
    nome = models.CharField(max_length=100)
    icone = models.FileField(upload_to='icones/')
    
    class Meta:
        verbose_name = 'Tipo de Empresa'
        verbose_name_plural = 'Tipos de Empresa'
    
    def __str__(self):
        return self.nome

class Empresa(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nome_fantasia = models.CharField(max_length=100)
    razao_social = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=14, unique=True)
    tipo = models.ForeignKey(TipoEmpresa, on_delete=models.PROTECT)
    endereco = models.CharField('Endereço', max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    hora_abertura = models.TimeField('Horário de Abertura')
    hora_fechamento = models.TimeField('Horário de Fechamento')
    foto = models.ImageField(upload_to='empresas/')
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
    
    def __str__(self):
        return self.nome_fantasia

class Produto(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField('Descrição')
    preco = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField('Quantidade em Estoque', default=0)
    foto = models.ImageField(upload_to='produtos/')
    disponivel = models.BooleanField('Disponível', default=True)
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
    
    def __str__(self):
        return f"{self.nome} - {self.empresa.nome_fantasia}"