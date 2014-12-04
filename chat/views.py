#adapted from https://github.com/abourget/gevent-socketio/tree/master/examples/django_chat

from socketio import socketio_manage

from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render, redirect

from chat.models import ChatRoom, ChatUser
from chat.sockets import ChatNamespace

from django import forms
from django.views.generic import UpdateView

from chat.forms import MafiaForm

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

    context = {"room": get_object_or_404(ChatRoom, slug=slug)}
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

#based very loosely on https://github.com/garmoncheg/ajax_form_example
#controls what to do when a mafia killing form is submitted
def mafia_form(request, template="room.html"):
    print ChatUser.objects.all()
    target = request.POST['target']
    room = request.POST['room']
    print room, target, "kill"
    cr = ChatRoom.objects.get(name=room)
    cr.target = target
    print "target: ", cr.target
    cr.save()

    return HttpResponse("");

#controls what to do when a voting form is submitted
def vote_form(request, template="room.html"):
    votedFor = request.POST['votedFor']
    room = request.POST['room']
    print room, votedFor, "vote"
    cr = ChatRoom.objects.get(name=room)
    cr.lastVotedFor = votedFor
    cr.save()

    return HttpResponse("");

#controls what to do when a cop investigating form is submitted
def cop_form(request, template="room.html"):
    investigated = request.POST['investigated']
    room = request.POST['room']
    print room, investigated, "investigate"
    cr = ChatRoom.objects.get(name=room)
    cr.investigated = investigated
    cr.save()

    return HttpResponse("");

#controls what to do when a doctor healing form is submitted
def doctor_form(request, template="room.html"):
    healed = request.POST['healed']
    room = request.POST['room']
    print room, healed, "doctor"
    cr = ChatRoom.objects.get(name=room)
    cr.healed = healed
    cr.save()

    return HttpResponse("");
