
from django.conf.urls.defaults import patterns, include, url
import socketio.sdjango

socketio.sdjango.autodiscover()

urlpatterns = patterns("chat.views",
    url("^socket\.io", include(socketio.sdjango.urls)),
    url("^$", "rooms", name="rooms"),
    url("^create/$", "create", name="create"),
    url(r'^mafia_form$', 'mafia_form', name="mafia_form"),
    url(r'^vote_form$', 'vote_form', name="vote_form"),
    url(r'^cop_form$', 'cop_form', name="cop_form"),
    url(r'^doctor_form$', 'doctor_form', name="doctor_form"),
    url("^(?P<slug>.*)$", "room", name="room"),
)
