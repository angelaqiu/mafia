#adapted from https://github.com/abourget/gevent-socketio/tree/master/examples/django_chat

from socketio import socketio_manage

from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render, redirect

from chat.models import ChatRoom, ChatUser
from chat.sockets import ChatNamespace

from django import forms
from django.views.generic import UpdateView

from chat.forms import *

def rooms(request, template="rooms.html"):
    """
    Homepage - lists all rooms.
    """
    context = {"rooms": ChatRoom.objects.all()}
    return render(request, template, context)


def room(request, slug, template="room.html"):
    """
    Show a room.
    """
    if request.method == 'POST':
        form = MafiaForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            target = cd ["target"]
            cr = ChatRoom.objects.get(name=slug)
            cr.target = ChatUser.objects.get(name=cd["target"])
            cr.save()
    else:
        form = MafiaForm()

    context = {"room": get_object_or_404(ChatRoom, slug=slug),
            "form": form}
    return render(request, template, context)

def create(request):
    """
    Handles post from the "Add room" form on the homepage, and
    redirects to the new room.
    """
    name = request.POST.get("name")
    if name:
        room, created = ChatRoom.objects.get_or_create(name=name)
        return redirect(room)
    return redirect(rooms)

