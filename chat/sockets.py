#adapted from https://github.com/abourget/gevent-socketio/tree/master/examples/django_chat
import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace
from chat.models import ChatRoom, ChatUser

@namespace('/chat')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    nicknames = []
    votes = dict()

    def initialize(self):
        self.logger = logging.getLogger("socketio.chat")
        self.log("Socketio session started")
        
    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
    
    def on_join(self, room):
        self.room = room
        self.join(room)
        return True
        
    def on_nickname(self, nickname, room):
        self.log('Nickname: {0}'.format(nickname))
        user, created = ChatUser.objects.get_or_create(name=nickname, room=ChatRoom.objects.get(id=room))
        self.nicknames.append(nickname)
        self.socket.session['nickname'] = nickname
        self.broadcast_event('announcement', '%s has connected' % nickname)
        self.broadcast_event('nicknames', self.nicknames)
        return True, nickname

    def recv_disconnect(self):
        # Remove nickname from the list.
        self.log('Disconnected')
        # ChatUser.objects.
        nickname = self.socket.session['nickname']
        self.nicknames.remove(nickname)
        self.broadcast_event('announcement', '%s has disconnected' % nickname)
        self.broadcast_event('nicknames', self.nicknames)
        self.disconnect(silent=True)
        return True

    def on_user_message(self, msg):
        self.log('User message: {0}'.format(msg))
        self.emit_to_room(self.room, 'msg_to_room',
            self.socket.session['nickname'], msg)
        return True

    #### end code adapted from gevent-socketio #####

    def broadcast_event_only_self(self, event, *args):
        pkt = dict(type="event",
                   name=event,
                   args=args,
                   endpoint=self.ns_name)

        for sessid, socket in self.socket.server.sockets.iteritems():
            if socket is self.socket:
                socket.send_packet(pkt)

    def on_investigate(self, user):
        self.log('investigated' + user)
        # self.emit_to_room(self.room, 'msg_to_room',
        #     self.socket.session['nickname'], msg)
        self.broadcast_event('announcement', 'someone has been investigated')
        for sessid, socket in self.socket.server.sockets.iteritems():
            self.log(socket)
        self.log(ChatNamespace.objects.all())
        # self.log("socket: " + str(self.socket) + "mafia: " + str(ChatUser.objects.get(name="asdf").socket))
        return True

    def on_heal(self, user):
        self.log('healed')
        self.broadcast_event('announcement', 'someone has been healed')
        return True

    def on_vote(self, user):
        self.log('voted')
        # self.emit_to_room(self.room, 'msg_to_room',
        #     self.socket.session['nickname'], user)
        nickname = self.socket.session['nickname']
        self.broadcast_event('announcement', '%s has voted for %s' %(nickname, user))
        if ChatUser.objects.get(name=user) in self.votes:
            self.votes[ChatUser.objects.get(name=user)] += 1
        self.log(self.votes)
        return True

    def on_start_game(self, room):
        self.log("Game has started! " + str(ChatRoom.objects.get(id=room)))
        self.broadcast_event('announcement', "Game is now starting")
        self.startGame(room)

    def on_night_end(self, room):
        self.log("night phase is over!!")
        self.broadcast_event('announcement', "Night phase is over")
        cRoom = ChatRoom.objects.get(id=room)            
        # self.log(ChatUser.objects.get(name="asdf").dead)
        
        self.broadcast_event_only_self('announcement', 'You investigated ' 
            + cRoom.investigated + 
            ". They were " + str(ChatUser.objects.get(name=cRoom.investigated).role))
        # if ChatUser.objects.get(name=self.socket.session['nickname']).role == 'COP':
        #     self.broadcast_event_only_self('announcement', 'You investigated ' 
        #         + str(cRoom.investigated) + 
        #         ". They were " + str(ChatUser.objects.get(name=cRoom.investigated).role))
        mafTarget = ChatUser.objects.get(name=cRoom.target)
        docTarget = ChatUser.objects.get(name=cRoom.healed)
        if mafTarget != docTarget:
            mafTarget.dead = True
            mafTarget.save()
            self.broadcast_event('announcement', cRoom.target + " was killed")
        else:
            self.log("target was saved!!")

        end = self.checkEndGame(room)
        if end == "town" or end == "mafia":
            self.gameOver(end)
        else:
            self.dayPhase(room)

    def on_end_day(self, room):
        self.log("day phase is over!!")
        self.broadcast_event('announcement', "Day phase is over")
        lynched = None
        for player in self.votes:
            if lynched == None and self.votes[player] > 0:
                lynched = player
            elif lynched != None and self.votes[player] > self.votes[lynched]:
                lynched = player
        cRoom = ChatRoom.objects.get(id=room)
        player.dead = True
        player.save()
        self.broadcast_event('announcement', str(lynched) + " was lynched. They were " + lynched.role)
        self.nightPhase(room)

    def startGame(self, room):
        ChatRoom.gameStarted = True
        self.log("game started boolean changed")
        cRoom = ChatRoom.objects.get(id=room)
        self.log(ChatUser.objects.filter(room=cRoom))
        
        #TODO: reset variables

        counter = 0
        # TODO: randomize roles
        for user in ChatUser.objects.filter(room=cRoom):
            self.log(user.name)
            if counter == 0 or counter == 1: user.role = 'MAFIA'
            elif counter == 2: user.role = 'COP'
            elif counter == 3: user.role = 'DOCTOR'
            else: user.role = 'CITIZEN'
            user.save()
            self.log(user.role)
            counter += 1
        self.broadcast_event_only_self('announcement', 'You are ' + 
            ChatUser.objects.get(name=self.socket.session['nickname']).role)
        self.playGame(room)

    def playGame(self, room):
        if ChatRoom.objects.get(id=room).phase == 'NIGHT':
            self.nightPhase(room)
        elif ChatRoom.objects.get(id=room).phase == 'DAY':
            self.dayPhase(room)

    def nightPhase(self, room):
        self.broadcast_event('announcement', 'Starting night phase...')
        self.log(ChatRoom.objects.get(id=room).target)
        if ChatRoom.objects.get(id=room).target != "":
            ChatRoom.objects.get(id=room).phase == 'DAY'

    def dayPhase(self, room):
        self.broadcast_event('announcement', 'Starting day phase...')
        self.log("day starting!!!!")
        self.log("I am: " + str(ChatUser.objects.get(name=self.socket.session['nickname'])))
        for player in ChatUser.objects.all():
            self.votes[player] = 0
            self.log(player.dead)
        self.log(self.votes)

    #sees if the game is over
    #returns "mafia" if the mafia has won
    #returns "town" if the town has won
    #returns False if no one has won
    def checkEndGame(self, room):
        self.log("Checking if the game is over")
        mafiaDead = True
        townDead = True
        for player in ChatUser.objects.all():
            self.log(str(player) + ", " + str(player.role) + ", " + str(player.dead))
            if player.role == 'MAFIA' and not player.dead:
                mafiaDead = False
            if player.role != 'MAFIA' and not player.dead:
                townDead = False
        if mafiaDead: 
            return "mafia"
        elif townDead:
            return "town"
        else:
            return False

    def gameOver(self, room):
        self.broadcast_event('announcement', 'Game is over!')

