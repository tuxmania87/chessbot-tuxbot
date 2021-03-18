from board import Board
from board2 import Board2
from chessutil import ChessUtils, HashEntry, Piece_Square_Tables
import random
import time
import chess
import chess.polyglot
import threading


class MovementGenerator:

    cu = ChessUtils()

    hashes = {}

    def __init__(self):

        self.cu = ChessUtils()
        self.saved_moved = ""
        self.results = []
        self.nodes = 0
        self.pv_table = {}
        self.killers = {0: {}, 1: {}}

        for i in range(0, 400):
            self.killers[0][i] = None
            self.killers[1][i] = None

        self.search_history = {}

        for i in range(0, 64):
            self.search_history[i] = {}
            for ii in range(0, 64):
                self.search_history[i][ii] = 0

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

        with chess.polyglot.open_reader("Performance.bin") as reader:
            for entry in reader.find_all(board):
                if entry.weight > max_weight:
                    max_weight = entry.weight
                    max_move = entry.move
        return max_move

    @staticmethod
    def min_max_eval_pychess(board):


        #_tstart = time.time_ns()
        sum = 0

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

        if not position_hash in self.pv_table:
            self.pv_table[position_hash] = {chess.WHITE: None, chess.BLACK: None}

        self.pv_table[position_hash][turn] = move


    def get_pvline(self, position_hash, turn):
        if position_hash not in self.pv_table:
            return None

        return self.pv_table[position_hash][turn]


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

    def quiescence(self, board, a, b):
        old_a = a
        best_move = None

        h = self.cu.get_board_hash_pychess(board)
        pv_move = self.get_pvline(h, board.turn)

        self.nodes += 1

        if board.can_claim_draw():
            return 0

        score = self.min_max_eval_pychess(board)

        if score >= b:
            return b

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

        ordered_move_list = sorted(scored_moves, key=scored_moves.get)
        ordered_move_list.reverse()

        for move in ordered_move_list:

            board.push(move)
            move_score = -1 * self.quiescence(board, -b, -a)
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



        return a


    def alpha_beta(self, board, depth, a, b, maxd):
        move_score = -20000000

        old_a = a
        best_move = None

        # get hash of current position
        h = self.cu.get_board_hash_pychess(board)

        pv_move = self.get_pvline(h, board.turn)



        self.nodes += 1

        if depth == 0:
            #return MovementGenerator.min_max_eval_pychess(board)
            return self.quiescence(board, a, b)

        if board.can_claim_draw():
            return 0


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

        for move in ordered_move_list:
            board.push(move)
            move_score = -1 * self.alpha_beta(board, depth-1, -b, -a, maxd)
            board.pop()



            if move_score > a:
                if move_score >= b:

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

        return a


    def retrieve_pvline(self, board):

        pv_line = list()

        _b = board.copy()

        for _ in range(10000):
            h = self.cu.get_board_hash_pychess(_b)
            best_move = self.get_pvline(h, _b.turn)

            if best_move is not None:
                pv_line.append(best_move)
                _b.push(best_move)
            else:
                break

        return pv_line

    def get_next_move_alpha_beta_iterative_2(self, board, depth, max_time):

        best_move = None

        #clear
        self.saved_moved = None
        self.nodes = 0

        entry_time = time.time()

        for cd in range(depth):
            current_depth = cd + 1

            _start = time.time()

            best_score = self.alpha_beta(board, current_depth, -20000000, 200000000, current_depth)

            pv_moves = self.retrieve_pvline(board)
            best_move = pv_moves[0]

            print(f"Depth {current_depth} Nodes: {self.nodes} Move: {best_move} Time: {time.time() - _start} Score: {best_score}")
            print(pv_moves)

            if time.time() - entry_time > max_time:
                break

        return best_move