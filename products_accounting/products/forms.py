from django import forms
from .models import Transfer

class CreateTransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['difference', 'comment']
        labels = {
            'difference': 'Изменить на',
            'comment': 'Комментарий',
        }
        widgets = {
            'difference': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите количество товара'}),
            'comment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите комментарий'}),
        }