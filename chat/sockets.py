#adapted from https://github.com/abourget/gevent-socketio/tree/master/examples/django_chat
import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace
from chat.models import ChatRoom, ChatUser
import random

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
        cRoom = ChatRoom.objects.get(id=room)
        if len(self.nicknames) == 0:
            ChatUser.objects.all().delete()
            cRoom.gameStarted = False
            cRoom.host = nickname
            cRoom.save()
        user, created = ChatUser.objects.get_or_create(name=nickname, 
            room = cRoom, session = self.socket.session)
        self.log("host is: " + cRoom.host + ", nicknames: "  + str(self.nicknames))
        self.nicknames.append(nickname)
        self.socket.session['nickname'] = nickname
        self.broadcast_event('announcement', '%s has connected' % nickname)
        self.broadcast_event('nicknames', self.nicknames, [])
        self.broadcast_event_only_self('show_self', nickname) 
        if len(self.nicknames) >= 5:  
            self.log("enough players to start the game")
            self.broadcast_event_only_user('show_host', "", cRoom.host)
        return True, nickname

    def recv_disconnect(self):
        # Remove nickname from the list.
        self.log('Disconnected')
        try:
            nickname = self.socket.session['nickname']
            self.nicknames.remove(nickname)
            # user = ChatUser.objects.get(name=self.socket.session['nickname'])
            # user.delete()
            #TODO: add user to list of dead??
            self.broadcast_event('announcement', '%s has disconnected' % nickname)
            self.broadcast_event('nicknames', self.nicknames, [])
            self.disconnect(silent=True)
            # self.log(str(user) + " has been deleted")
            return True
        except:
            return False

    #### end code adapted from gevent-socketio #####


    def on_user_message(self, msg, room):
        self.log('User message: {0}'.format(msg))
        cRoom = ChatRoom.objects.get(id=room)
        myself = ChatUser.objects.get(name=self.socket.session['nickname'])
        if myself.dead:
            return False
        self.log(str(cRoom.gameStarted) + ", " + cRoom.phase)   
        if (cRoom.gameStarted == True and cRoom.phase == "NIGHT" and 
            myself.role == "MAFIA"):
            self.broadcast_event_only_mafia('regmessage', 
                self.socket.session['nickname'], msg)
            self.log("i'm mafia")
        elif cRoom.gameStarted == False or cRoom.phase != "NIGHT":
            self.emit_to_room(self.room, 'msg_to_room',
                self.socket.session['nickname'], msg)
            self.log("general message" + str(cRoom.gameStarted) + ", " + cRoom.phase)
        return True

    def broadcast_event_only_self(self, event, *args):
        pkt = dict(type="event",
                   name=event,
                   args=args,
                   endpoint=self.ns_name)

        for sessid, socket in self.socket.server.sockets.iteritems():
            if socket is self.socket:
                socket.send_packet(pkt)

    def broadcast_event_reveal_role(self, event):

        for sessid, socket in self.socket.server.sockets.iteritems():
            try:
                socket.session["nickname"]
                player = ChatUser.objects.get(name=socket.session["nickname"])
                msg = "You are " + player.role
                if player.role == "MAFIA":
                    other = ChatUser.objects.filter(
                        role="MAFIA").exclude(name=socket.session["nickname"])
                    msg += ". Your team members are: " + str(other[0])
                pkt = dict(type="event",
                   name=event,
                   args=msg,
                   endpoint=self.ns_name)
                socket.send_packet(pkt)
            except:
                pass

    def broadcast_event_only_user(self, event, msg, user):
        self.log("Sending only to: " + user)
        for sessid, socket in self.socket.server.sockets.iteritems():
            try:
                nick = socket.session["nickname"]
                if user == socket.session["nickname"]:
                    pkt = dict(type="event",
                       name=event,
                       args=msg,
                       endpoint=self.ns_name)
                    socket.send_packet(pkt)
            except:
                pass
            
            
    def broadcast_event_elements(self):
        for sessid, socket in self.socket.server.sockets.iteritems():
            try:
                socket.session["nickname"]
                player = ChatUser.objects.get(name=socket.session["nickname"])
                msg = ""
                if player.role != "MAFIA":
                    event = 'hide_mafia'
                    pkt = dict(type="event",
                       name=event,
                       args=msg,
                       endpoint=self.ns_name)
                    socket.send_packet(pkt)
                if player.role != "COP":
                    event = 'hide_cop'
                    pkt = dict(type="event",
                       name=event,
                       args=msg,
                       endpoint=self.ns_name)
                    socket.send_packet(pkt)
                if player.role != "DOCTOR":
                    event = 'hide_doctor'
                    pkt = dict(type="event",
                       name=event,
                       args=msg,
                       endpoint=self.ns_name)
                    socket.send_packet(pkt)
            except:
                pass

    def broadcast_event_only_mafia(self, event, *args):
        pkt = dict(type="event",
                   name=event,
                   args=args,
                   endpoint=self.ns_name)

        for sessid, socket in self.socket.server.sockets.iteritems():
            try:
                socket.session["nickname"]
                player = ChatUser.objects.get(name=socket.session["nickname"])
                if player.role == "MAFIA" and socket != self.socket:
                    socket.send_packet(pkt)
            except:
                pass

    def on_investigate(self, user):
        self.log('investigated' + user)
        self.broadcast_event('announcement', 'someone has been investigated')
        for sessid, socket in self.socket.server.sockets.iteritems():
            self.log(socket)
        self.log(ChatNamespace.objects.all())
        return True

    def on_heal(self, user):
        self.log('healed')
        self.broadcast_event('announcement', 'someone has been healed')
        return True

    def on_vote(self, user):
        self.log('voted')
        nickname = self.socket.session['nickname']
        try:  
            if ChatUser.objects.get(name__iexact=user) in self.votes:
                self.votes[ChatUser.objects.get(name__iexact=user)] += 1
            self.log(self.votes)
            self.broadcast_event('announcement', '%s has voted for %s' %(nickname, user))
            return True
        except:
            self.broadcast_event_only_self('announcement', 
                'The user you voted for is invalid. Please vote again.')
            self.log("not legit!!")
            self.broadcast_event_only_self('show_vote', "")
            return False

    def on_start_game(self, room):
        self.log("Game has started! " + str(ChatRoom.objects.get(id=room)))
        self.broadcast_event('announcement', "Game is now starting")
        self.startGame(room)

    def on_night_end(self, room):
        self.log("night phase is over!!")
        self.broadcast_event('announcement', "Night phase is over")
        cRoom = ChatRoom.objects.get(id=room)
        #cop investigation
        if cRoom.investigated != "":
            self.log("reporting investigation")
            self.broadcast_event_only_user('announcement', 'You investigated ' 
                + str(cRoom.investigated) + 
                ". They are " + 
                str(ChatUser.objects.get(name__iexact=cRoom.investigated).role),
                str(ChatUser.objects.get(role='COP')))
        #mafia kill
        if cRoom.target != "":
            mafTarget = ChatUser.objects.get(name__iexact=cRoom.target)
            #doctor heal
            if cRoom.healed != "":
                docTarget = ChatUser.objects.get(name__iexact=cRoom.healed)
                #if not the same target, then mafia target dies
                if mafTarget != docTarget:
                    mafTarget.dead = True
                    mafTarget.save()
                    self.broadcast_event('announcement', cRoom.target 
                        + " was killed. They were " + mafTarget.role)
                    self.broadcast_event_only_user('announcement', 
                        "You have died.", str(mafTarget))
                    self.broadcast_event_only_user('hide_all', "", str(mafTarget))
                else:
                    self.log("target was saved!!")
            else: #no doctor heal, target dies
                mafTarget.dead = True
                mafTarget.save()
                self.broadcast_event('announcement', cRoom.target 
                    + " was killed. They were " + mafTarget.role)
                self.broadcast_event_only_user('announcement', 
                    "You have died.", str(mafTarget))
                self.broadcast_event_only_user('hide_all', "", str(mafTarget))
        self.update_players(room)

        end = self.checkEndGame(room)
        if end == "town" or end == "mafia":
            self.gameOver(room)
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
        self.log(str(lynched) + " will be lynched")
        if lynched != None:
            lynched.dead = True
            lynched.save()
        self.update_players(room)
        self.broadcast_event('announcement', str(lynched) + 
            " was lynched. They were " + lynched.role)
        self.broadcast_event_only_user('announcement', 
            "You have died.", str(lynched))
        self.broadcast_event_only_user('hide_all', "", str(lynched))

        end = self.checkEndGame(room)
        if end == "town" or end == "mafia":
            self.gameOver(room)
        else:
            self.nightPhase(room)

    def on_quit(self, room):
        self.log("Removing: " + self.socket.session['nickname'])
        user = ChatUser.objects.get(name=self.socket.session['nickname'])
        user.dead = True
        user.save()
        user.delete()

    def update_players(self, room):
        self.log("updating players")
        alive = []
        dead = []
        for name in self.nicknames:
            player = ChatUser.objects.get(name__iexact=name)
            if not player.dead:
                alive.append(name)
            else:
                dead.append(name)
        self.broadcast_event('nicknames', alive, dead)

    def startGame(self, room):
        cRoom = ChatRoom.objects.get(id=room)
        cRoom.gameStarted = True
        self.log("game started; host is: " + cRoom.host)
        self.log(ChatUser.objects.filter(room=cRoom))
        cRoom.target = ""
        cRoom.investigated = ""
        cRoom.healed = ""
        cRoom.phase = 'NIGHT'
        cRoom.save()

        self.assignRoles(room)

    def assignRoles(self, room):
        counter = 0
        cRoom = ChatRoom.objects.get(id=room)
        userids = range(1, ChatUser.objects.filter(room=cRoom).count() + 1)
        random.shuffle(userids)
        for idnum in userids:
            self.log(str(idnum))
            player = ChatUser.objects.get(id=idnum)
            self.log(player.name)
            if counter == 0 or counter == 1: player.role = 'MAFIA'
            elif counter == 2: player.role = 'COP'
            elif counter == 3: player.role = 'DOCTOR'
            else: player.role = 'CITIZEN'
            player.save()
            self.log(player.role)
            counter += 1
        self.broadcast_event_reveal_role('announcement')
        self.broadcast_event_reveal_role('show_role')
        self.playGame(room)

    def playGame(self, room):
        if ChatRoom.objects.get(id=room).phase == 'NIGHT':
            self.nightPhase(room)
        elif ChatRoom.objects.get(id=room).phase == 'DAY':
            self.dayPhase(room)

    def nightPhase(self, room):
        self.broadcast_event('announcement', 'Starting night phase...')
        cRoom = ChatRoom.objects.get(id=room)
        cRoom.phase = "NIGHT"
        cRoom.target = ""
        cRoom.healed = ""
        cRoom.investigated = ""
        cRoom.save()
        self.broadcast_event('hide_day')
        self.broadcast_event('show_night')
        myself = self.socket.session['nickname']
        self.broadcast_event_elements()

    def dayPhase(self, room):
        self.broadcast_event('announcement', 'Starting day phase...')
        self.log("day starting!!!!")
        cRoom = ChatRoom.objects.get(id=room)
        cRoom.phase = "DAY"
        cRoom.save()
        self.broadcast_event('hide_night')
        self.broadcast_event('show_day')
        self.broadcast_event('show_vote')
        self.log("I am: " + str(ChatUser.objects.get(name=self.socket.session['nickname'])))
        for player in ChatUser.objects.all():
            self.votes[player] = 0
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
            self.log(str(player) + ", " + str(player.role) + ", " + str(player.dead) + str(player.id))
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
        self.broadcast_event('announcement', 'Game is over! Please press Quit to exit the game.')
        cRoom = ChatRoom.objects.get(id=room)
        cRoom.phase = "DAY"
        # ChatUser.objects.filter(room=room).delete()


