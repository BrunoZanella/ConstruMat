from django import forms
from .models import Empresa, Produto

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            'nome_fantasia', 'razao_social', 'cnpj', 'tipo',
            'endereco', 'latitude', 'longitude',
            'hora_abertura', 'hora_fechamento', 'foto'
        ]
        widgets = {
            'hora_abertura': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fechamento': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'quantidade', 'foto', 'disponivel']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'preco': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['disponivel'].widget.attrs['class'] = 'form-check-input'