from chat.models import ChatRoom

def startGame():
    ChatRoom.gameStarted = True
    self.log("game started boolean changed")