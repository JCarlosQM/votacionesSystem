from django import forms
from django.contrib.auth import authenticate
from .models import Campaña, Lista, Votante

class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Usuario o contraseña incorrectos")
            self.user = user
        return cleaned_data

    def get_user(self):
        return self.user



class CampañaForm(forms.ModelForm):
    activa = forms.TypedChoiceField(
        label="¿Está activa?",
        choices=((True, 'Sí'), (False, 'No')),
        coerce=lambda x: x == 'True',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Campaña
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'activa']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class ListaForm(forms.ModelForm):
    class Meta:
        model = Lista
        fields = ['nombre', 'logo', 'mensaje', 'campaña']
        widgets = {
            'campaña': forms.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'mensaje': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class VotanteForm(forms.ModelForm):
    class Meta:
        model = Votante
        fields = ['dni', 'ha_votado']

    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if len(dni) != 8:
            raise forms.ValidationError("El DNI debe tener exactamente 8 caracteres.")
        return dni