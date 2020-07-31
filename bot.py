import requests
import json
from board import Board
from chessutil import ChessUtils
import threading
import random

b = Board()
c = ChessUtils()

token = "Ad48N2ugS3X9ONo8"
header = {"Authorization":"Bearer {}".format(token)}



#def playGame(id):
def playGame(a,b,c,d,e,f,g,h):

    print(a,b,c,d,e,f,g,h)

    requests.post("https://lichess.org/api/challenge/{}/accept".format(id), headers=header)

    r = requests.get("https://lichess.org/api/bot/game/stream/{}".format(id), headers=header, stream=True)
    # https://lichess.org/api/bot/game/stream/{gameId}


    b = Board()
    c = ChessUtils()

    amIwhite = False

    for line in r.iter_lines():
        decoded_line = line.decode('utf-8')
        if (decoded_line != ''):

            j = json.loads(decoded_line)
            print("XX ", j)

            if j["type"] == "gameFull":

                print("!!", j)
                print(j["white"]["id"])

                if j["white"]["id"] == "tuxbot":

                    amIwhite = True

                    chessMove = c.getRandomMove(b.board, amIwhite)
                    if chessMove is None:
                        print("end of game")
                        exit(0)

                    print("First move: ", chessMove)

                    # decode
                    fr = b.ChessCoordinatesToPosition(chessMove[0:2])
                    to = b.ChessCoordinatesToPosition(chessMove[2:4])

                    print("First Move Position ", fr, to)

                    piece = b.board[fr]
                    b.board[fr] = ''
                    b.board[to] = piece

                    _r = requests.post("https://lichess.org/api/bot/game/{}/move/{}".format(id, chessMove),
                                       headers=header)
                    _r.json()

            if j["type"] == "gameState":

                moves = j["moves"]

                evenlist = len(moves.split(" ")) % 2 == 0

                if (not evenlist and not amIwhite) or (evenlist and amIwhite):

                    lastmove = moves.split(" ")[-1]

                    # decode
                    fr = b.ChessCoordinatesToPosition(lastmove[0:2])
                    to = b.ChessCoordinatesToPosition(lastmove[2:4])

                    piece = b.board[fr]
                    b.board[fr] = ''
                    b.board[to] = piece

                    print("received: ", lastmove)

                    # make own move
                    chessMove = c.getRandomMove(b.board, amIwhite)
                    if chessMove is None:
                        print("end of game")
                        exit(0)

                    # decode
                    fr = b.ChessCoordinatesToPosition(chessMove[0:2])
                    to = b.ChessCoordinatesToPosition(chessMove[2:4])

                    piece = b.board[fr]
                    b.board[fr] = ''
                    b.board[to] = piece

                    print("sent: ", chessMove)
                    # b.renderBoard()

                    _r = requests.post("https://lichess.org/api/bot/game/{}/move/{}".format(id, chessMove),
                                       headers=header)
                    _r.json()



if __name__ == "__main__":

    r = requests.get("https://lichess.org/api/stream/event", headers=header, stream=True)

    for line in r.iter_lines():
        decoded_line = line.decode('utf-8')
        if(decoded_line != ''):

            j = json.loads(decoded_line)
            print(j["type"], decoded_line)

            if j["type"] == "challenge":
                id = j["challenge"]["id"]

                t = threading.Thread(target=playGame, args=(id))
                t.start()
