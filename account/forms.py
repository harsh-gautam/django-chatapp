from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import authenticate


from account.models import Account

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=120, help_text="Required: Add a valid email.")
    name = forms.CharField(max_length=120, help_text="Required: Name is required")

    class Meta:
        model = Account
        fields = ('email', 'username', 'name', 'password1', 'password2',)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError(f'Email {email} is already in use.')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError(f'Username {username} is already in use.')


class LoginForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ("email", "password")

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid Email/Password.")