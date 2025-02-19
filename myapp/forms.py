from .models import EmployeeCertifications
from django import forms

class CertificationForm(forms.ModelForm):
    class Meta:
        model=EmployeeCertifications
        fields='__all__'