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

class Game:

    def __init__(self, id, play_time, increment):
        self.id = id
        self.play_time = play_time
        self.increment = increment


        self.playGame()


    def playGame(self):

        b = chess.Board()
        #print(a,b,c,d,e,f,g,h)


        requests.post("https://lichess.org/api/challenge/{}/accept".format(self.id), headers=header)

        r = requests.get("https://lichess.org/api/bot/game/stream/{}".format(self.id), headers=header, stream=True)
        # https://lichess.org/api/bot/game/stream/{gameId}

        c = ChessUtils()
        m = MovementGenerator()
        doMove = m.get_next_move_tuxfish
        designated_depth = 6

        # calculate max time per move
        ## asuming we want to do 80 moves without be flagged



        time_per_move = int((80 * self.increment + self.play_time) / 80)


        #designated_time = 4

        amIwhite = False

        for line in r.iter_lines():
            decoded_line = line.decode('utf-8')
            if (decoded_line != ''):

                j = json.loads(decoded_line)
                print("XX ", j)

                if j["type"] == "gameFinish":
                    _game = j["game"]

                    if _game["id"] == self.id:
                        print("GAME FINISHED AND ABORTED")
                        blocked = False
                        return

                if j["type"] == "gameFull":

                    print("!!", j)
                    print(j["white"]["id"])

                    if j["white"]["id"] == "tuxbot9000":

                        amIwhite = True

                        #chessMove = m.getRandomMove(b.board, amIwhite)
                        chessMove = doMove(b, designated_depth, time_per_move)
                        if chessMove is None:
                            print("end of game")
                            exit(0)

                        print("First move: ", chessMove)


                        b.push(chessMove)

                        _r = requests.post("https://lichess.org/api/bot/game/{}/move/{}".format(self.id, chessMove),
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


                        chessMove = doMove(b, designated_depth, time_per_move)



                        if chessMove is None:
                            print("end of game")
                            exit(0)

                        # decode
                        b.push(chessMove)

                        print("sent: ", chessMove)
                        # b.renderBoard()

                        _r = requests.post("https://lichess.org/api/bot/game/{}/move/{}".format(self.id, chessMove),
                                           headers=header)
                        print(_r.json())


blocked = False

active_games = {}

if __name__ == "__main__":

    r = requests.get("https://lichess.org/api/stream/event", headers=header, stream=True)

    for line in r.iter_lines():
        decoded_line = line.decode('utf-8')
        if(decoded_line != ''):

            j = json.loads(decoded_line)
            print(j["type"], decoded_line)


            if j["type"] == "challenge":

                _id = j["challenge"]["id"]
                if blocked:
                    __r = requests.post(f"https://lichess.org/api/challenge/{_id}/decline", headers=header, data= '{ "reason" : "I am busy"}')


                try:
                    play_time = j["challenge"]["timeControl"]["limit"]
                except:
                    play_time = 30 * 60

                try:
                    increment = j["challenge"]["timeControl"]["increment"]
                except:
                    increment = 0


                t = threading.Thread(target=Game, args=(_id, play_time, increment))
                t.start()
