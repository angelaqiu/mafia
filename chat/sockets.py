#adapted from https://github.com/abourget/gevent-socketio/tree/master/examples/django_chat
import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace
from chat.models import ChatRoom, ChatUser

@namespace('/chat')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    nicknames = []

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

    def on_investigate(self, msg):
        self.log('investigated')
        # self.emit_to_room(self.room, 'msg_to_room',
        #     self.socket.session['nickname'], msg)
        self.broadcast_event('announcement', 'someone has been investigated')
        return True

    def on_vote(self, user):
        self.log('voted')
        # self.emit_to_room(self.room, 'msg_to_room',
        #     self.socket.session['nickname'], user)
        nickname = self.socket.session['nickname']
        self.broadcast_event('announcement', '%s has voted for %s' %(nickname, user))
        return True

    def startGame(self, room):
        ChatRoom.gameStarted = True
        self.log("game started boolean changed")
        self.log(ChatUser.objects.filter(room=ChatRoom.objects.get(id=room)))
        # self.log("mafia: " + str())
        counter = 0
        for user in ChatUser.objects.filter(room=ChatRoom.objects.get(id=room)):
            self.log(user.name)
            if counter == 0: user.role = 'MAFIA'
            elif counter == 1: user.role = 'COP'
            elif counter == 2: user.role = 'DETECTIVE'
            else: user.role = 'CITIZEN'
            self.log(user.role)
            counter += 1
        self.playGame(room)

    def on_start_game(self, room):
        self.log("Game has started! " + str(ChatRoom.objects.get(id=room)))
        self.broadcast_event('announcement', "Game is now starting")
        # ChatRoom.gameStarted = True
        
        self.startGame(room)

    def playGame(self, room):
        if ChatRoom.objects.get(id=room).phase == 'NIGHT':
            self.nightPhase(room)
        elif ChatRoom.objects.get(id=room).phase == 'DAY':
            self.dayPhase(room)

    def nightPhase(self, room):
        self.broadcast_event('announcement', 'Starting night phase...')

    def dayPhase(self, room):
        self.broadcast_event('announcement', 'Starting day phase...')

