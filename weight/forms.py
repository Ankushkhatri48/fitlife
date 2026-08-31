from django import forms
from weight.models import WeightLog

class WeightLogForm(forms.ModelForm):
    class Meta:
        model = WeightLog
        fields = ['date', 'weight', 'unit']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'e.g. 70.5',
                'step': '0.01',
                'min': '0.1'
            }),
            'unit': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
        }

    def clean_weight(self):
        val = self.cleaned_data.get('weight')
        if val is not None and val <= 0:
            raise forms.ValidationError("Weight must be greater than zero.")
        return val
