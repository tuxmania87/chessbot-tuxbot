from board import Board
from board2 import Board2
from chessutil import ChessUtils, HashEntry, Piece_Square_Tables
import random
import time
import chess
import chess.polyglot
import threading
import random

class MovementGenerator:

    cu = ChessUtils()

    hashes = {}

    INFINITY = 137000000

    INITIALIZED = False
    pv_table = {}

    USE_QUIESENCE = True


    def clear_search_params(self):
        self.nodes = 0
        #self.pv_table = {}
        self.killers = {0: {}, 1: {}}

        for i in range(0, 400):
            self.killers[0][i] = None
            self.killers[1][i] = None

        self.search_history = {}

        for i in range(0, 64):
            self.search_history[i] = {}
            for ii in range(0, 64):
                self.search_history[i][ii] = 0

    def __init__(self):

        self.cu = ChessUtils()
        self.saved_moved = ""
        self.results = []


        self.clear_search_params()


        self.Mvv_Lva_Victim_scores = {
            "p" : 100,
            "n" : 200,
            "b" : 300,
            "r" : 400,
            "q" : 500,
            "k" : 600
        }

        # init mvv lva
        self.Mvv_Lva_Scores = {}
        for attacker in self.Mvv_Lva_Victim_scores.keys():
            self.Mvv_Lva_Scores[attacker] = {}
            for victim in self.Mvv_Lva_Victim_scores.keys():
                self.Mvv_Lva_Scores[attacker][victim] = int(self.Mvv_Lva_Victim_scores[victim] + 6  - (self.Mvv_Lva_Victim_scores[attacker] / 100)) + 1000000



    def get_opening_move(self, board):

        max_weight = 0
        max_move = None

        found_moves = {}

        with chess.polyglot.open_reader("Performance.bin") as reader:
            for entry in reader.find_all(board):

                if not entry.weight in found_moves:
                    found_moves[entry.weight] = []

                found_moves[entry.weight].append(entry.move)

                if entry.weight > max_weight:
                    max_weight = entry.weight
                    max_move = entry.move

        # shuffle out of best moves

        if max_move is None:
            return None

        best_moves = found_moves[max_weight]

        random.shuffle(best_moves)

        return best_moves[0]

    @staticmethod
    def min_max_eval_pychess(board):
        return MovementGenerator.min_max_eval_pychess_gen1(board)

    @staticmethod
    def min_max_eval_pychess_gen2(board):

        if board.is_checkmate():
            #print(board.move_stack)
            return -1 * (MovementGenerator.INFINITY - board.ply())

        sum = 0
        val = {"k": 200, "q": 9, "r": 5, "b": 3, "n": 3, "p": 1}

        for pos, _piece in board.piece_map().items():
            piece = str(_piece)
            sum += val[piece.lower()] * (-1 if piece.islower() else 1)

            if piece == "p":
                sum -= Piece_Square_Tables.pawnEvalWhite[Piece_Square_Tables.mirror_table[pos]] / 10

            elif piece == "n":
                sum -= Piece_Square_Tables.knightEval[pos] / 10

            elif piece == "b":
                sum -= Piece_Square_Tables.bishopEvalWhite[Piece_Square_Tables.mirror_table[pos]] / 10

            elif piece == "q":
                sum -= Piece_Square_Tables.evalQueen[pos] / 10

            elif piece == "k":
                sum -= Piece_Square_Tables.kingEvalWhite[Piece_Square_Tables.mirror_table[pos]] / 10

            elif piece == "r":
                sum -= Piece_Square_Tables.rookEvalWhite[Piece_Square_Tables.mirror_table[pos]] / 10

            #white
            elif piece == "P":
                sum += Piece_Square_Tables.pawnEvalWhite[pos] / 10

            elif piece == "N":
                sum += Piece_Square_Tables.knightEval[pos] / 10

            elif piece == "B":
                sum += Piece_Square_Tables.bishopEvalWhite[pos] / 10

            elif piece == "Q":
                sum += Piece_Square_Tables.evalQueen[pos] / 10

            elif piece == "K":
                sum += Piece_Square_Tables.kingEvalWhite[pos] / 10

            elif piece == "R":
                sum += Piece_Square_Tables.rookEvalWhite[pos] / 10

        # add deviations of square maps


        # add mobility
        if board.turn == chess.WHITE:
            num_1 = board.legal_moves.count()
            board.push(chess.Move.null())
            num_2 = board.legal_moves.count()
            board.pop()
            mobility = num_1 - num_2
        else:
            num_2 = board.legal_moves.count()
            board.push(chess.Move.null())
            num_1 = board.legal_moves.count()
            board.pop()
            mobility = num_1 - num_2

            # if either side is in check, mobility is 0
        if board.is_check():
            mobility = 0

        sum += 0.1 * mobility


        return sum * (-1 if board.turn == chess.BLACK else 1)


    @staticmethod
    def min_max_eval_pychess_gen1(board):


        #_tstart = time.time_ns()
        sum = 0

        if board.is_checkmate():
            #print(board.move_stack)
            return -1 * (MovementGenerator.INFINITY - board.ply())

        val = {"k": 200, "q": 9, "r":5, "b": 3, "n":3, "p": 1}

        for pos, _piece in board.piece_map().items():
            piece = str(_piece)
            sum += val[piece.lower()] * (-1 if piece.islower() else 1)
            #sum += int(Piece_Square_Tables.get_piece_value(piece, pos) /10 ) * (-1 if piece.islower() else 1)

        if board.turn == chess.WHITE:
            num_1 = board.legal_moves.count()
            board.push(chess.Move.null())
            num_2 = board.legal_moves.count()
            board.pop()
            mobility = num_1 - num_2
        else:
            num_2 = board.legal_moves.count()
            board.push(chess.Move.null())
            num_1 = board.legal_moves.count()
            board.pop()
            mobility = num_1 - num_2

            # if either side is in check, mobility is 0
        if board.is_check():
            mobility = 0

        sum += 0.1 * mobility
        '''
        

        #_tende = time.time_ns()
        #print(_tende - _tstart)


        # doubled pawns
        pieces = board.piece_map()

        white_pawns = []
        black_pawns = []

        for k, v in pieces.items():
            if str(v) == 'P':
                white_pawns.append(k)
            elif str(v) == 'p':
                black_pawns.append(k)

        doubled_white = 0
        doubled_black = 0
        isolated_white = 0
        isolated_black = 0
        blocked_white = 0
        blocked_black = 0

        for pawn in white_pawns:
            # check for each pawn

            file_number = pawn % 8

            # is pawn blocked ( for white +8 for black -8)
            if pawn + 8 < 64 and board.piece_at(pawn + 8) is not None:
                blocked_white += 1

            has_left_neighbor = False
            has_right_neighbor = False

            if pawn % 8 == 0:
                has_left_neighbor = True

            if pawn % 8 == 7:
                has_right_neighbor = True

            # is it doubled, is another pawn on the file
            for other_pawn in white_pawns:
                if other_pawn != pawn and abs(pawn - other_pawn) % 8 == 0:
                    doubled_white += 1

                # isolation check left file ( if exists)

                other_file = other_pawn % 8
                if file_number - other_file == 1:
                    has_left_neighbor = True
                if file_number - other_file == -1:
                    has_right_neighbor = True

            if not has_left_neighbor and not has_right_neighbor:
                isolated_white += 1

        # check for black pawns

        for pawn in black_pawns:
            # check for each pawn

            file_number = pawn % 8

            # is pawn blocked ( for white +8 for black -8)
            if pawn - 8 >= 0 and board.piece_at(pawn - 8) is not None:
                blocked_black += 1

            has_left_neighbor = False
            has_right_neighbor = False

            if pawn % 8 == 0:
                has_left_neighbor = True

            if pawn % 8 == 7:
                has_right_neighbor = True

            # is it doubled, is another pawn on the file
            for other_pawn in black_pawns:
                if other_pawn != pawn and abs(pawn - other_pawn) % 8 == 0:
                    doubled_black += 1

                # isolation check left file ( if exists)

                other_file = other_pawn % 8
                if file_number - other_file == 1:
                    has_left_neighbor = True
                if file_number - other_file == -1:
                    has_right_neighbor = True

            if not has_left_neighbor and not has_right_neighbor:
                isolated_black += 1


        pawn_influence = ((doubled_white - doubled_black) + (isolated_white - isolated_black) + (blocked_white - blocked_black)) * 0.1
        #print(pawn_influence)
        sum -= pawn_influence
        '''
        # punish no castle right
        castle_factor = 0



        return sum * (-1 if board.turn == chess.BLACK else 1)


    def store_pvline(self, position_hash, move, turn):
        MovementGenerator.pv_table[position_hash] = move


    def get_pvline(self, position_hash, turn):
        if position_hash not in MovementGenerator.pv_table:
            return None

        return MovementGenerator.pv_table[position_hash]


    def pick_next_move(self, move_dict):
        best_key = None
        best_value = -1

        if len(move_dict.keys()) == 0:
            return None

        for k, v in move_dict.items():
            if v > best_value:
                best_value = v
                best_key = k

        move_dict.remove(best_key)

        return best_key

    def quiescence(self, board, a, b, qdepth = 0):
        #if qdepth > 0:
        #    print(qdepth)


        old_a = a
        best_move = None

        #h = self.cu.get_board_hash_pychess(board)
        h = board.fen()
        pv_move = self.get_pvline(h, board.turn)

        self.nodes += 1

        #if board.can_claim_draw():
        #    return 0


        #score = self.min_max_eval_pychess(board) if not board.is_check() else (-1 * (MovementGenerator.INFINITY - board.ply()))
        score = self.min_max_eval_pychess(board)

        if score >= b:
            return b

        # delta prun
        if score < a - 9:
            return a



        if score > a:
            a = score



        unscored_moves = board.legal_moves
        scored_moves = {}

        # score moves
        ## by capturing

        for move in unscored_moves:

            if pv_move is not None and move == pv_move:
                scored_moves[move] = 20000000
                continue


            ## all non captures are at the end of the list
            if board.is_capture(move):
                ## all captures have to be scored and thus sorted
                attacker = board.piece_at(move.from_square).symbol().lower()
                try:
                    victim = board.piece_at(move.to_square).symbol().lower()
                except:
                    victim = 'p'

                scored_moves[move] = self.Mvv_Lva_Scores[attacker][victim]

            #elif board.is_check():
#                scored_moves[move] = 0

        ordered_move_list = sorted(scored_moves, key=scored_moves.get)
        ordered_move_list.reverse()

        for move in ordered_move_list:

            board.push(move)
            move_score = -1 * self.quiescence(board, -b, -a, qdepth + 1)
            board.pop()

            if move_score > a:
                if move_score >= b:

                    return b
                a = move_score
                best_move = move


        if a != old_a:
            # debug
            # print(f"beat alpha on {depth} for move {str(move)} and score {move_score}")

            # self.pv_line[depth] = str(best_move)
            self.store_pvline(h, best_move, board.turn)

        #if board.is_check() and board.legal_moves.count() == 0:

         #   return -1 * (MovementGenerator.INFINITY - board.ply())

        return a


    def alpha_beta(self, board, depth, a, b, maxd, null_move):
        move_score = -MovementGenerator.INFINITY

        # check for null mive
        if null_move and not board.is_check() and board.ply() > 0 and depth >= 3: #and 1 == 2:
            board.push(chess.Move.null())
            move_score = -1 * self.alpha_beta(board, depth - 3, -b, -b + 1, maxd, False)
            board.pop()

            if move_score >= b:
                return b


        move_score = -MovementGenerator.INFINITY

        old_a = a
        best_move = None

        # get hash of current position
        #h = self.cu.get_board_hash_pychess(board)
        h = board.fen()

        pv_move = self.get_pvline(h, board.turn)



        self.nodes += 1

        if board.legal_moves.count() == 0:
            return MovementGenerator.min_max_eval_pychess(board)

        if depth <= 0:
            if MovementGenerator.USE_QUIESENCE:
                return self.quiescence(board, a, b)
            else:
                return MovementGenerator.min_max_eval_pychess(board)


        #if board.can_claim_draw():
        #    return 0


        unscored_moves = board.legal_moves
        scored_moves = {}

        # score moves
        ## by capturing

        for move in unscored_moves:

            if pv_move is not None and move == pv_move:
                scored_moves[move] = 20000000
                continue


            ## all non captures are at the end of the list
            if not board.is_capture(move):

                ### check if non capture is killer move 1st order
                if self.killers[0][board.ply()] == move:
                    scored_moves[move] = 900000
                elif self.killers[0][board.ply()] == move:
                    scored_moves[move] = 800000
                else:
                    scored_moves[move] = self.search_history[move.from_square][move.to_square]


            else:
                ## all captures have to be scored and thus sorted
                attacker = board.piece_at(move.from_square).symbol().lower()
                try:
                    victim = board.piece_at(move.to_square).symbol().lower()
                except:
                    victim = 'p'

                scored_moves[move] = self.Mvv_Lva_Scores[attacker][victim]


        ordered_move_list = sorted(scored_moves, key=scored_moves.get)
        ordered_move_list.reverse()

        legal = 0

        for move in ordered_move_list:
            board.push(move)

            legal += 1

            move_score = -1 * self.alpha_beta(board, depth-1, -b, -a, maxd, null_move)
            board.pop()



            if move_score > a:
                if move_score >= b:

                    if legal == 1:
                        self.fhf += 1

                    self.fh += 1

                    # killer moves
                    if not board.is_capture(move):
                        self.killers[1][board.ply()] = self.killers[1][board.ply()]
                        self.killers[0][board.ply()] = move

                    return b
                a = move_score
                best_move = move

                # killer moves
                if not board.is_capture(move):
                    self.search_history[best_move.from_square][best_move.to_square] += depth

                if depth == maxd:
                    self.saved_moved = move

        if a != old_a:
            # debug
            # print(f"beat alpha on {depth} for move {str(move)} and score {move_score}")

            #self.pv_line[depth] = str(best_move)
            self.store_pvline(h, best_move, board.turn)

            if (h != board.fen()):
                print("Ohoh")


        return a

    def retrieve_pvline(self, board):

        pv_line = list()

        _b = board.copy()

        for _ in range(10000):
            #h = self.cu.get_board_hash_pychess(_b)
            h = _b.fen()
            best_move = self.get_pvline(h, _b.turn)

            if best_move is not None:
                pv_line.append(best_move)
                _b.push(best_move)
            else:
                break

        return pv_line

    def retrieve_fenline(self, board):

        fen_line = list()

        _b = board.copy()

        for _ in range(10000):
            h = _b.fen()
            best_move = None
            try:
                best_move = MovementGenerator.fen_pv[h]
            except:
                pass

            if best_move is not None:
                fen_line.append(best_move)
                _b.push(best_move)
            else:
                break

        return fen_line

    def get_pv_line_san(self, board, line):
        san_list = list()
        b = board.copy()

        for move in line:
            san_list.append(b.san(move))
            b.push(move)

        return san_list

    def get_next_move_alpha_beta_iterative_2(self, board, depth, max_time):

        best_move = None

        #clear
        self.saved_moved = None
        self.clear_search_params()

        entry_time = time.time()

        for cd in range(1, depth):
            self.nodes = 0
            self.fh = 0
            self.fhf = 0
            current_depth = cd + 1

            _start = time.time()

            best_score = self.alpha_beta(board, current_depth, -MovementGenerator.INFINITY, MovementGenerator.INFINITY, current_depth, True)

            pv_moves = self.retrieve_pvline(board)
            if len(pv_moves) > 0:
                best_move = pv_moves[0]
            else:
                # make sure we run at least once more
                if cd == depth-1:
                    # we are at last iteration and need to run once more
                    print("extra run")
                    best_sore = self.alpha_beta(board, cd+1, -MovementGenerator.INFINITY, MovementGenerator.INFINITY,
                                    cd+1, True)

                    print(f"XTRA: Depth {cd+1} Nodes: {self.nodes} Move: {board.san(best_move)} Time: {time.time() - _start} Score: {best_score}")

            print(f"Depth {current_depth} Nodes: {self.nodes} Move: {board.san(best_move)} Time: {time.time() - _start} Score: {best_score}")
            print(f"Move Ordering {self.fhf /max(self.fh,1)}")
            print("PV LINE: ",self.get_pv_line_san(board,pv_moves))

            if time.time() - entry_time > max_time:
                break

            if best_score >= MovementGenerator.INFINITY - 100:
                # found checkmate
                return best_move

        return best_move


    def get_next_move_tuxfish(self, board, depth, max_time):

        opening_move = self.get_opening_move(board)

        if opening_move is not None:
            return opening_move

        return self.get_next_move_alpha_beta_iterative_2(board, depth, max_time)
