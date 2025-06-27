from django import forms
from .models import Comment, Order

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your email'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your comment', 'rows': 5}),
        }
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'country', 'state', 'city']