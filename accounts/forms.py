from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'address', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full address',
                'rows': 3
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional except email
        for field_name, field in self.fields.items():
            if field_name != 'email':
                field.required = False
        
        # Add help text
        self.fields['first_name'].help_text = "Your first name"
        self.fields['last_name'].help_text = "Your last name"
        self.fields['email'].help_text = "This will be used for login and notifications"
        self.fields['address'].help_text = "Your complete address for delivery"
        self.fields['profile_image'].help_text = "Upload a profile picture (PNG, JPG, JPEG)"
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is already taken by another user
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    
    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            # Check file size (limit to 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large. Please keep it under 5MB.")
            
            # Check file format
            valid_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if hasattr(image, 'content_type') and image.content_type not in valid_formats:
                raise forms.ValidationError("Invalid image format. Please use PNG, JPG, JPEG, or GIF.")
                
        return image
