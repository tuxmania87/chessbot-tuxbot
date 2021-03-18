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

        return self.pv_table[position_hash]


    def alpha_beta(self, board, depth, a, b, maxd):
        move_score = -20000000

        old_a = a
        best_move = None

        # get hash of current position
        h = self.cu.get_board_hash_pychess(board)

        self.nodes += 1

        if depth == 0:
            return MovementGenerator.min_max_eval_pychess(board)

        if board.can_claim_draw():
            return 0

        for move in board.legal_moves:
            board.push(move)
            move_score = -1 * self.alpha_beta(board, depth-1, -b, -a, maxd)
            board.pop()



            if move_score > a:
                if move_score >= b:
                    return b
                a = move_score
                best_move = move

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





    def get_next_move_alpha_beta(self, board, depth):
        self.saved_moved = None
        self.nodes = 0
        _start = time.time()

        self.alpha_beta(board, depth, -20000000, 200000000, depth)

        print(f"Search with depth {depth} ended searching {self.nodes} Nodes. Move: {self.saved_moved} Time: {time.time()-_start}")

        print(self.retrieve_pvline(board))

        return self.saved_moved


    def get_next_move_alpha_beta_iterative(self, board, depth):

        first_guess = None
        for d in range(depth):
            first_guess = self.get_next_move_alpha_beta(board, d)

        return first_guess

