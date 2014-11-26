from django import forms
from chat.models import ChatRoom, ChatUser

class MafiaForm(forms.Form):
    target = forms.CharField(label="Target",
        max_length=255,
        widget=forms.TextInput(),
    )
    # class Meta:
    #     model = ChatRoom
    #     fields = ['target']
    #     widgets = {
    #         'target': forms.TextInput(
    #             attrs={'id': 'ChatRoom-target', 'required': True, 'placeholder': 'Select a target...'}
    #         ),
    #     }