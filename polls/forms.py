from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone


class CampoDataNascimento(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', forms.DateInput(attrs={'type': 'date'}))
        # formato retornado pelo input type="date"
        kwargs.setdefault('input_formats', ['%Y-%m-%d'])
        super().__init__(*args, **kwargs)


class CampoTelefone(forms.CharField):
    def to_python(self, numero):
        numero = super().to_python(numero)
        if numero:
            import re
            numero_limpo = re.sub(r'[^\d]', '', numero)

            if len(numero_limpo) == 11:
                return f'({numero_limpo[:2]}) {numero_limpo[2:7]}-{numero_limpo[7:]}'
            elif len(numero_limpo) == 10:
                return f'({numero_limpo[:2]}) {numero_limpo[2:6]}-{numero_limpo[6:]}'

            return numero_limpo
        return numero


class RegistroForm(forms.Form):
    username = forms.CharField(label="Seu nome de usuário", max_length=100)
    email = forms.EmailField(label="Seu email")
    password = forms.CharField(
        label="Sua senha",
        widget=forms.PasswordInput
    )
    password_confirm = forms.CharField(
        label="Confirme a sua senha",
        widget=forms.PasswordInput
    )
    telefone = CampoTelefone(
        max_length=20,
        help_text='Ex: (11) 99999-9999',
        widget=forms.TextInput(attrs={'maxlength': '20'})
    )
    data_nascimento = CampoDataNascimento(
        label="Sua data de nascimento",
        help_text="Ex: 11/11/2011"
    )

    def clean_password_confirm(self):
        dado_limpo = super().clean()
        password = dado_limpo.get('password')
        password_confirm = dado_limpo.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError("As senhas não são iguais!")

        if password and len(password) < 6:
            raise ValidationError(
                "A senha tem que ter no minimo 6 caracteres!")

        return dado_limpo

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nome de usuário já existe!")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email já esta cadastrado!")
        return email

    def calculo_idade(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        hoje = timezone.now().date()
        idade = hoje.year - data_nascimento.year
        if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
            idade -= 1
        return idade
