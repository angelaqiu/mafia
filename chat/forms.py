from django import forms

class MafiaForm(forms.Form):
    target = forms.CharField(label="Target",
        max_length=255,
        widget=forms.TextInput,
    )