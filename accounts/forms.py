from django import forms
from .models import AdminUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordResetForm, PasswordChangeForm as AuthPasswordChangeForm, UserChangeForm


class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        required=True,
        widget=forms.PasswordInput(
            render_value=True,
            attrs={'autocomplete': 'off'}
        )
    )

    class Meta:
        model = AdminUser
        fields = ['username', 'email', 'phone_number', 'address', 'role', 'is_active']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            self.existing_user = kwargs.get('instance')
        self.fields['is_active'].help_text = "Keep this blank if new user, otherwise user won't receive invite."

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        if self.cleaned_data.get("password") and not self.cleaned_data.get("password").startswith('pbkdf2_sha256'):
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserRegistration(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = AdminUser
        fields = ['username', 'email', 'phone_number', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mobile number', 'type': 'tel'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
        }
        labels = {
            'username': '',
            'email': '',
            'phone_number': '',
            'address': '',
        }

class LoginFormAuthentication(AuthenticationForm):
    username = UsernameField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'autofocus': True}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class PasswordReset(PasswordResetForm):
    email = forms.CharField(label='', max_length=254, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username or Email', "autocomplete": "email"}))

class PasswordChangeForm(AuthPasswordChangeForm):
    old_password = forms.CharField(label="", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Existing password', "autocomplete": "current-password", "autofocus": True}))
    new_password1 = forms.CharField(label="", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password', "autocomplete": "new-password"}))
    new_password2 = forms.CharField(label="", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password', "autocomplete": "new-password"}))

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = AdminUser
        fields = ['username', 'email', 'phone_number', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mobile number', 'type': 'tel'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
        }
        labels = {
            'username': '',
            'email': '',
            'phone_number': '',
            'address': '',
        }