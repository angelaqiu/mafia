#adapted from https://github.com/abourget/gevent-socketio/tree/master/examples/django_chat
from django.db import models
from django.template.defaultfilters import slugify


class ChatRoom(models.Model):

    name = models.CharField(max_length=20)
    slug = models.SlugField(blank=True)
    gameStarted = models.BooleanField(default=False)
    gameOver = models.BooleanField(default=False)
    PHASE_CHOICES = (
        ('DAY', 'Day'),
        ('NIGHT', 'Night'),
        )
    phase = models.CharField(max_length=100, choices=PHASE_CHOICES)
    
    #mafia's target
    target = models.CharField(max_length=20)

    #cop's investigations
    investigated = models.CharField(max_length=20)

    #doctor's heal 
    healed = models.CharField(max_length=20)

    #day's lynch
    lynched = models.CharField(max_length=20)
    lastVotedFor = models.CharField(max_length=20)

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("room", (self.slug,))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(ChatRoom, self).save(*args, **kwargs)

class ChatUser(models.Model):

    name = models.CharField(max_length=20)
    session = models.CharField(max_length=20)
    room = models.ForeignKey("chat.ChatRoom", related_name="users")
    ROLE_CHOICES = (
        ('MAFIA', 'Mafia'),
        ('COP', 'Cop'),
        ('DOCTOR', 'Doctor'),
        ('CITIZEN', 'Citizen'),
    )
    role = models.CharField(max_length=100, choices = ROLE_CHOICES, 
        default='CITIZEN')
    votedFor = models.CharField(max_length=20)
    dead = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name

