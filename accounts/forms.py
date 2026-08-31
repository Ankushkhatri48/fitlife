from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
        'placeholder': 'Enter your password'
    }))
    password_confirm = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
        'placeholder': 'Confirm your password'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
        'placeholder': 'Enter your email'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
        'placeholder': 'Choose a username'
    }))

    class Meta:
        model = CustomUser
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    # Form specific fields for imperial height input
    height_feet = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=8,
        label="Feet",
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'ft'
        })
    )
    height_inches = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=11,
        label="Inches",
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'in'
        })
    )

    class Meta:
        model = UserProfile
        fields = [
            'name', 'age', 'gender', 'weight', 'height', 'weight_unit', 
            'height_unit', 'goal', 'activity_level', 
            'daily_calorie_target_override', 'protein_target_override',
            'carbs_target_override', 'fat_target_override', 'timezone'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'Your name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'Your age',
                'min': '0'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'Your weight',
                'step': '0.1',
                'min': '0.1'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'Height in cm',
                'step': '0.1',
                'min': '1'
            }),
            'weight_unit': forms.Select(attrs={
                'id': 'id_weight_unit',
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'height_unit': forms.Select(attrs={
                'id': 'id_height_unit',
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'onchange': 'toggleHeightInputs()'
            }),
            'goal': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'activity_level': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'daily_calorie_target_override': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'Leave empty for auto estimation'
            }),
            'protein_target_override': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'Leave empty for auto'
            }),
            'carbs_target_override': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'Leave empty for auto'
            }),
            'fat_target_override': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'Leave empty for auto'
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'e.g. UTC, Asia/Kolkata, US/Eastern'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        height_unit = cleaned_data.get('height_unit')
        
        if height_unit == 'ft_in':
            feet = cleaned_data.get('height_feet')
            if feet is None:
                self.add_error('height_feet', "Please specify feet when choosing ft/in unit.")
        else:
            height = cleaned_data.get('height')
            if height is None:
                self.add_error('height', "Please specify height in cm.")
                
        # Age validation
        age = cleaned_data.get('age')
        if age is not None and age <= 0:
            self.add_error('age', "Age must be greater than zero.")
            
        # Weight validation
        weight = cleaned_data.get('weight')
        if weight is not None and weight <= 0:
            self.add_error('weight', "Weight must be greater than zero.")
            
        return cleaned_data
