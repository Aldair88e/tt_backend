from django import forms
from django.core.exceptions import ValidationError

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _

class MunicipioForm(forms.Form):
    municipio = forms.CharField(label=_("Municipio"))

    def clean_municipio(self):
        municipio = self.cleaned_data["municipio"]
        if municipio.isdigit():
            raise ValidationError(
                _("Please enter a valid value, only alphabetic characters are allowed"),
                params={"value": municipio},
            )
        return municipio

class CodigoEstadoForm(forms.Form):
    estado = forms.CharField(label=("Estado"))

    def clean_estado(self):
        estado = self.cleaned_data["estado"]
        if not estado.isdigit():
            raise ValidationError(
                _("Please enter a valid value, only numeric characters are allowed"),
                params={"value": estado},
            )
        return estado
    
class IdMypeForm(forms.Form):
    id = forms.IntegerField(label=("Id"))
    def clean_id(self):
        id = self.cleaned_data["id"]
        return id