from django import forms
from nutrition.models import DailyNutritionEntry

class DailyNutritionForm(forms.ModelForm):
    class Meta:
        model = DailyNutritionEntry
        fields = [
            'date', 'calories', 'protein', 'carbohydrates', 
            'fat', 'calories_burned', 'fiber', 'sugar', 'sodium', 'water', 'notes'
        ]
        widgets = {
            'calories_burned': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'kcal (optional)',
                'min': '0'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'kcal',
                'min': '0'
            }),
            'protein': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'grams',
                'min': '0'
            }),
            'carbohydrates': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'grams (optional)',
                'min': '0'
            }),
            'fat': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'grams (optional)',
                'min': '0'
            }),
            'fiber': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'grams (optional)',
                'min': '0'
            }),
            'sugar': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'grams (optional)',
                'min': '0'
            }),
            'sodium': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'mg (optional)',
                'min': '0'
            }),
            'water': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'ml (optional)',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'What did you eat? Write notes here...',
                'rows': 4
            }),
        }

    def clean_calories(self):
        val = self.cleaned_data.get('calories')
        if val is not None and val < 0:
            raise forms.ValidationError("Calories cannot be negative.")
        return val

    def clean_protein(self):
        val = self.cleaned_data.get('protein')
        if val is not None and val < 0:
            raise forms.ValidationError("Protein cannot be negative.")
        return val
