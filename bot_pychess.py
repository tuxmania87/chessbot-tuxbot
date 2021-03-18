import requests
import json
import chess
from chessutil import ChessUtils
import threading
import random
from movegen import MovementGenerator




token = "T2VkC8Eru2c62x9f"
header = {"Authorization":"Bearer {}".format(token)}

#doMove = m.get_next_move_alpha_beta
#doMove = m.get_next_move_pv_search_board1


def playGame(id):
#def playGame(a,b,c,d,e,f,g,h):
    b = chess.Board()
    #print(a,b,c,d,e,f,g,h)

    requests.post("https://lichess.org/api/challenge/{}/accept".format(id), headers=header)

    r = requests.get("https://lichess.org/api/bot/game/stream/{}".format(id), headers=header, stream=True)
    # https://lichess.org/api/bot/game/stream/{gameId}

    c = ChessUtils()
    m = MovementGenerator()
    doMove = m.get_next_move_alpha_beta_iterative_2
    designated_depth = 100
    designated_time = 4

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
                    chessMove = doMove(b, designated_depth, designated_time)
                    if chessMove is None:
                        print("end of game")
                        exit(0)

                    print("First move: ", chessMove)


                    b.push(chessMove)

                    _r = requests.post("https://lichess.org/api/bot/game/{}/move/{}".format(id, chessMove),
                                       headers=header)
                    print(_r.json())

            if j["type"] == "gameState":

                moves = j["moves"]

                evenlist = len(moves.split(" ")) % 2 == 0

                if (not evenlist and not amIwhite) or (evenlist and amIwhite):

                    lastmove = moves.split(" ")[-1]

                    # decode
                    b.push(chess.Move.from_uci(lastmove))

                    print("received: ", lastmove)

                    # make own move
                    #chessMove = m.getRandomMove(b.board, amIwhite)


                    chessMove = doMove(b, designated_depth, designated_time)



                    if chessMove is None:
                        print("end of game")
                        exit(0)

                    # decode
                    b.push(chessMove)

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
