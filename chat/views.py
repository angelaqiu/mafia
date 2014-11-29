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
def mafia_form(request, template="room.html"):
    # errors_dict = {}
    # if form.errors:
    #     for error in form.errors:
    #         e = form.errors[error]
    #         errors_dict[error] = unicode(e)
    print ChatUser.objects.all()
    target = request.POST['target']
    room = request.POST['room']
    print room, target
    cr = ChatRoom.objects.get(name=room)
    cr.target = ChatUser.objects.get(name=target)
    print "target: ", cr.target
    cr.save()
    targ = ChatUser.objects.get(name=target)
    targ.dead = True
    targ.save()
    # ChatNamespace.dayPhase()
    print "HELLO"
    # print str(ChatRoom.objects.get(id=room).target))
    # return HttpResponseBadRequest(json.dumps(errors_dict))

    # context = {"form": form}
    return HttpResponse("");

def vote_form(request, template="room.html"):
    print ChatUser.objects.all()
    votedFor = request.POST['votedFor']
    room = request.POST['room']
    print room, votedFor
    cr = ChatRoom.objects.get(name=room)
    cr.lastVotedFor = ChatUser.objects.get(name=votedFor)
    print "votedFor: ", cr.lastVotedFor
    cr.save()
    # # ChatNamespace.dayPhase()
    print "HELLO"
    # print str(ChatRoom.objects.get(id=room).target))

    # context = {"form": form}
    return HttpResponse("");

# def mafia_form(request):
#     if request.POST:
#         form = MafiaForm(request.POST)
#         if form.is_valid():
#             # Imaginable form purpose. Post to admins.
#             target = form.cleaned_data["target"]

#             # Only executed with jQuery form request
#             if request.is_ajax():
#                 return HttpResponse('OK')
#             else:
#                 # render() a form with data (No AJAX)
#                 # redirect to results ok, or similar may go here 
#                 pass
#         else:
#             if request.is_ajax():
#                 # Prepare JSON for parsing
#                 errors_dict = {}
#                 if form.errors:
#                     for error in form.errors:
#                         e = form.errors[error]
#                         errors_dict[error] = unicode(e)

#                 return HttpResponseBadRequest(json.dumps(errors_dict))
#             else:
#                 # render() form with errors (No AJAX)
#                 pass
#     else:
#         form = MafiaForm()

#     return render(request, 'room.html', {'form':form})

# def create_post(request):
#     if request.method == 'POST':
#         post_text = request.POST.get('the_post')
#         response_data = {}

#         post = Post(text=post_text, author=request.user)
#         post.save()

#         response_data['result'] = 'Create post successful!'
#         response_data['postpk'] = post.pk
#         response_data['text'] = post.text
#         response_data['created'] = post.created.strftime('%B %d, %Y %I:%M %p')
#         response_data['author'] = post.author.username

#         return HttpResponse(
#             json.dumps(response_data),
#             content_type="application/json"
#         )
#     else:
#         return HttpResponse(
#             json.dumps({"nothing to see": "this isn't happening"}),
#             content_type="application/json"
#         )
