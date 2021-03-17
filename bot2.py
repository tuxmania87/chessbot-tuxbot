import requests
import json
from board2 import Board2
from chessutil import ChessUtils
import threading
import random
from movegen import MovementGenerator

b = Board2()
c = ChessUtils()
m = MovementGenerator()

token = "T2VkC8Eru2c62x9f"
header = {"Authorization":"Bearer {}".format(token)}

#doMove = m.get_next_move_alpha_beta
doMove = m.get_next_move_neg_max_board2
designated_depth = 3

def playGame(id):
#def playGame(a,b,c,d,e,f,g,h):

    #print(a,b,c,d,e,f,g,h)

    requests.post("https://lichess.org/api/challenge/{}/accept".format(id), headers=header)

    r = requests.get("https://lichess.org/api/bot/game/stream/{}".format(id), headers=header, stream=True)
    # https://lichess.org/api/bot/game/stream/{gameId}


    b = Board2()
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

                if j["white"]["id"] == "tuxbot9000":

                    amIwhite = True

                    #chessMove = m.getRandomMove(b.board, amIwhite)
                    chessMove = doMove(b, amIwhite, designated_depth)
                    if chessMove is None:
                        print("end of game")
                        exit(0)

                    print("First move: ", chessMove)

                    # decode
                    fr = ChessUtils.ChessCoordinatesToPosition(chessMove[0:2])
                    to = ChessUtils.ChessCoordinatesToPosition(chessMove[2:4])

                    print("First Move Position ", fr, to)

                    b.do_move((fr, to, 0))

                    _r = requests.post("https://lichess.org/api/bot/game/{}/move/{}".format(id, chessMove),
                                       headers=header)
                    print(_r.json())

            if j["type"] == "gameState":

                moves = j["moves"]

                evenlist = len(moves.split(" ")) % 2 == 0

                if (not evenlist and not amIwhite) or (evenlist and amIwhite):

                    lastmove = moves.split(" ")[-1]

                    # decode
                    fr = ChessUtils.ChessCoordinatesToPosition(lastmove[0:2])
                    to = ChessUtils.ChessCoordinatesToPosition(lastmove[2:4])

                    b.do_move((fr, to, 0))

                    print("received: ", lastmove)

                    # make own move
                    #chessMove = m.getRandomMove(b.board, amIwhite)


                    chessMove = doMove(b, amIwhite, designated_depth)



                    if chessMove is None:
                        print("end of game")
                        exit(0)

                    # decode
                    fr = ChessUtils.ChessCoordinatesToPosition(chessMove[0:2])
                    to = ChessUtils.ChessCoordinatesToPosition(chessMove[2:4])

                    b.do_move((fr, to, 0))

                    print("sent: ", chessMove)
                    # b.renderBoard()

                    _r = requests.post("https://lichess.org/api/bot/game/{}/move/{}".format(id, chessMove),
                                       headers=header)
                    print(_r.json())



if __name__ == "__main__":

    r = requests.get("https://lichess.org/api/stream/event", headers=header, stream=True)

    for line in r.iter_lines():
        decoded_line = line.decode('utf-8')
        if(decoded_line != ''):

            j = json.loads(decoded_line)
            print(j["type"], decoded_line)

            if j["type"] == "challenge":
                _id = j["challenge"]["id"]

                t = threading.Thread(target=playGame, args=(_id,))
                t.start()
