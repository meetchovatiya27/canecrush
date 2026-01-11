from django import forms
from .models import ContactMessage, Review

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['fname', 'lname', 'email','message']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review', 'product']
        widgets = {
            'product': forms.HiddenInput(),
        }


