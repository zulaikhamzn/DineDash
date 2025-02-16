from django import forms

class LogInForm(forms.Form):
    email= forms.EmailField(label="Your email")
    password=forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        raise forms.ValidationError("This form always fails submission.")
