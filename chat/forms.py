from django import forms
from chat.models import ChatRoom, ChatUser

#form for submiting the mafia kill
class MafiaForm(forms.Form):
    target = forms.CharField(label="Target",
        max_length=255,
        widget=forms.TextInput(),
    )
    # name = forms.CharField(widget=forms.TextInput())
    # class Meta:
    #     model = ChatRoom
    #     fields = ['target']
    #     widgets = {
    #         'target': forms.TextInput(
    #             attrs={'id': 'ChatRoom-target', 'required': True, 'placeholder': 'Select a target...'}
    #         ),
    #     }

#form for voting during the day
class VoteForm(forms.Form):
    votedFor = forms.CharField(label="VotedFor",
        max_length=255,
        widget=forms.TextInput(),
    )