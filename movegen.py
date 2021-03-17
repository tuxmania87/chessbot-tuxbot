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


    def getRandomMove(self, board, iswhite):

        _board = Board()
        _c = ChessUtils()

        allmoves = _c.getAllPlayerMoves(board, iswhite)

        if len(allmoves) == 0:
            return None

        mymove = random.randint(0, len(allmoves) - 1)
        f, t = allmoves[mymove]
        print("move generator ", f,t)
        return "{}{}".format(_board.positionToChessCoordinates(f), _board.positionToChessCoordinates(t))

    def candidateMoves(self, board, iswhite):


        _board = Board()
        _c = ChessUtils()

        allmoves = _c.getAllPlayerMoves(board, iswhite)

        if len(allmoves) == 0:
            return None


        # if in check do randmom move that is putting you out of check

        if _c.isPlayerInCheck(board, iswhite):
            return self.getRandomMove(board, iswhite)


        # check all moves

        ## collect all check moves

        checkmoves = []

        for move in allmoves:
            temp_board = board.copy()

            f,t = move

            piece = temp_board[f]
            temp_board[f] = ''
            temp_board[t] = piece

            if _c.isPlayerInCheck(temp_board, not iswhite):
                checkmoves.append(move)


        if len(checkmoves) > 0:
            print("ALL checkmoves: ", checkmoves)
            f, t = checkmoves[random.randint(0, len(checkmoves) - 1)]
            print("move generator - checkmove", f, t)
            return "{}{}".format(_board.positionToChessCoordinates(f), _board.positionToChessCoordinates(t))



        ## collect all take moves

        takemoves = []

        print("!DEBUG? All Moves ", allmoves)

        for move in allmoves:
            _,t = move

            if board[t] != '' and board[t].islower() and not iswhite:
                takemoves.append(move)

            if board[t] != '' and not board[t].islower() and iswhite:
                takemoves.append(move)

        if len(takemoves) > 0:
            print("ALL takemoves: ", takemoves)
            f, t = takemoves[random.randint(0, len(takemoves)-1)]
            print("move generator - take move", f, t)
            return "{}{}".format(_board.positionToChessCoordinates(f), _board.positionToChessCoordinates(t))


        ## collect threat moves
        threatmoves = []

        for move in allmoves:
            f,t = move

            temp_board = board.copy()
            piece = temp_board[f]
            temp_board[f] = ''
            temp_board[t] = piece

            # check if move is threatning anything

            threats = _c.getPieceThreats(temp_board, t)

            if len(threats) > 0:
                threatmoves.append(move)

        if len(threatmoves) > 0:
            print("ALL threatmoves: ", threatmoves)
            f, t = threatmoves[random.randint(0, len(threatmoves)-1)]
            print("move generator - threat move", f, t)
            return "{}{}".format(_board.positionToChessCoordinates(f), _board.positionToChessCoordinates(t))

        return self.getRandomMove(board, iswhite)

    def get_next_move_min_max(self, board, iswhite, depth):
        if iswhite:
            a, b = self.min_max_maxi(board, iswhite, depth)
            f, t = b[-1]
            _board = Board()
            return "{}{}".format(_board.positionToChessCoordinates(f), _board.positionToChessCoordinates(t))
        else:
            a, b = self.min_max_mini(board, not iswhite, depth)
            f, t = b[-1]
            _board = Board()
            return "{}{}".format(_board.positionToChessCoordinates(f), _board.positionToChessCoordinates(t))

    def min_max_maxi(self, board, iswhite, depth):
        if depth == 0:
            return MovementGenerator.min_max_eval(board), []

        int_max = -20000000
        move_max = ""
        move_stack = []
        all_moves = self.cu.getAllPlayerMoves(board.board, iswhite)

        for move in all_moves:
            b2 = board.copy()
            b2.do_move(move)
            score, bmove = self.min_max_mini(b2, not iswhite, depth -1)
            if score > int_max:
                int_max = score
                move_max = move
                move_stack = bmove
        move_stack.append(move_max)
        return int_max, move_stack



    def get_opening_move(self, board):

        max_weight = 0
        max_move = None

        with chess.polyglot.open_reader("Performance.bin") as reader:
            for entry in reader.find_all(board):
                if entry.weight > max_weight:
                    max_weight = entry.weight
                    max_move = entry.move
        return max_move



    def min_max_mini(self, board, iswhite, depth):
        if depth == 0:
            return -1 * MovementGenerator.min_max_eval(board), []

        int_min = 20000000
        move_min = ""
        move_stack = []
        all_moves = self.cu.getAllPlayerMoves(board.board, iswhite)

        for move in all_moves:
            b2 = board.copy()
            b2.do_move(move)
            score, bmove = self.min_max_maxi(b2, not iswhite, depth -1)
            if score < int_min:
                int_min = score
                move_min = move
                move_stack = bmove

        move_stack.append(move_min)
        return int_min, move_stack


    @staticmethod
    def min_max_eval_pychess(board):


        #_tstart = time.time_ns()
        sum = 0

        #val = {"k": 200, "q": 9, "r":5, "b": 3, "n":3, "p": 1}

        for pos, _piece in board.piece_map().items():
            piece = str(_piece)
            #sum += val[piece.lower()] * (-1 if piece.islower() else 1)
            sum += int(Piece_Square_Tables.get_piece_value(piece, pos) /10 ) * (-1 if piece.islower() else 1)

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

        #sum += 0.1 * mobility
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

    @staticmethod
    def min_max_eval(board):


        #_tstart = time.time_ns()
        sum = 0

        val = {"k": 200, "q": 9, "r":5, "b": 3, "n":3, "p": 1}

        for piece in board.board:
            if piece == "":
                continue
            sum += val[piece.lower()] * (-1 if piece.isupper() else 1)

        mobility = len(MovementGenerator.cu.getAllPlayerMoves(board.board, True)) \
                   - len(MovementGenerator.cu.getAllPlayerMoves(board.board , False))

        sum += 0.1 * mobility

        #_tende = time.time_ns()
        #print(_tende - _tstart)

        return sum

    @staticmethod
    def min_max_eval_board2(board):

        # _tstart = time.time_ns()
        sum = 0

        val = {Board2.KING: 200, Board2.QUEEN: 9, Board2.ROOK: 5, Board2.BISHOP: 3, Board2.KNIGHT: 3, Board2.PAWN: 1}

        for i in range(64):
            if board.piece[i] == Board2.EMPTY:
                continue

            sum += val[board.piece[i]] * (-1 if board.color[i] == Board2.DARK else 1)


        mobility = len(board.move_gen_pseudo_legal(Board2.LIGHT, Board2.DARK)) - len(board.move_gen_pseudo_legal(Board2.DARK,Board2.LIGHT))

        sum += 0.1 * mobility

        # _tende = time.time_ns()
        # print(_tende - _tstart)

        return sum


    def alpha_beta_max(self, board, iswhite, depth, a, b, maxd):
        if depth == 0:
            return MovementGenerator.min_max_eval(board), []
        max_val = a
        move_max = ""
        move_stack = []
        #_t = time.time_ns()
        all_moves = self.cu.getAllPlayerMoves(board.board, iswhite)
        #print("MV ", depth, " " * (maxd - depth), time.time_ns() - _t)
        for move in all_moves:
            b2 = board.copy()
            b2.do_move(move)

            score, bmove = self.alpha_beta_min(b2, not iswhite, depth - 1, max_val, b, maxd)

            if score > max_val:
                max_val = score
                move_max = move
                move_stack = bmove

                if depth == maxd:
                    self.saved_moved = move

                if max_val >= b:
                    break


        move_stack.append(move_max)
        return max_val, move_stack

    def alpha_beta_min(self, board, iswhite, depth, a, b, maxd):
        if depth == 0:
            return MovementGenerator.min_max_eval(board), []
        min_val = b
        min_move = ""
        move_stack = []
        #_t = time.time_ns()
        all_moves = self.cu.getAllPlayerMoves(board.board, iswhite)
        #print("MV ",depth, " " * (maxd - depth), time.time_ns()-_t)
        for move in all_moves:
            b2 = board.copy()
            b2.do_move(move)

            score, bmove = self.alpha_beta_max(b2, not iswhite, depth - 1, a, min_val, maxd)

            if score < min_val:
                min_val = score
                min_move = move
                move_stack = bmove

                if depth == maxd:
                    self.saved_moved = move

                if min_val >= b:
                    break


        move_stack.append(min_move)
        return min_val, move_stack

    def get_next_move_alpha_beta(self, board, iswhite, depth):
        self.saved_moved = None
        if iswhite:
            _s = time.time()
            self.alpha_beta_max(board, iswhite, depth, -2000000, 2000000, depth)
            f, t = self.saved_moved
            _board = Board()
            print("gesamt ", time.time() - _s)
            return "{}{}".format(_board.positionToChessCoordinates(f), _board.positionToChessCoordinates(t))
        else:
            self.alpha_beta_min(board, iswhite, depth, -2000000, 2000000, depth)
            f, t = self.saved_moved
            _board = Board()
            return "{}{}".format(_board.positionToChessCoordinates(f), _board.positionToChessCoordinates(t))


    def get_next_move_neg_max(self, board, iswhite, depth):
        #negamax(rootNode, depth, −∞, +∞, 1)
        print(self.neg_max( board, iswhite, depth, -20000000, 20000000, depth))
        f, t = self.saved_moved
        _board = Board()
        return "{}{}".format(_board.positionToChessCoordinates(f), _board.positionToChessCoordinates(t))


    def neg_max(self, board, iswhite, depth, a, b, maxd):
        a_orig = a

        h = self.cu.get_board_hash(board.board)
        if h in MovementGenerator.hashes and MovementGenerator.hashes[h].depth >= depth:
            if MovementGenerator.hashes[h].flag == HashEntry.EXACT:
                return MovementGenerator.hashes[h].value
            elif MovementGenerator.hashes[h].flag == HashEntry.LOWERBOUND:
                a = max(a, MovementGenerator.hashes[h].value)
            else:
                b = min(b, MovementGenerator.hashes[h].value)

            if a >= b:
                return MovementGenerator.hashes[h].value

        if depth == 0:
            return MovementGenerator.min_max_eval(board)

        all_moves = self.cu.getAllPlayerMoves(board.board, iswhite)
        val = -2000000
        for move in all_moves:
            b2 = board.copy()
            b2.do_move(move)
            val = max(val, -1 * self.neg_max(b2, not iswhite, depth -1 ,-b, -a, maxd))

            if val > a and depth == maxd:
                self.saved_moved = move


            a = max(a, val)


            if a>= b:
                break



        _e = HashEntry()
        _e.value = val
        if val <= a_orig:
            _e.flag = HashEntry.UPPERBOUND
        elif val >= b:
            _e.flag = HashEntry.LOWERBOUND
        else:
            _e.flag = HashEntry.EXACT
        _e.depth = depth
        MovementGenerator.hashes[h] = _e

        return val


    def neg_max_board2(self, board, iswhite, depth, a, b, maxd):
        a_orig = a

        h = self.cu.get_board_hash_board2(board)
        if h in MovementGenerator.hashes and MovementGenerator.hashes[h].depth >= depth:
            if MovementGenerator.hashes[h].flag == HashEntry.EXACT:
                return MovementGenerator.hashes[h].value
            elif MovementGenerator.hashes[h].flag == HashEntry.LOWERBOUND:
                a = max(a, MovementGenerator.hashes[h].value)
            else:
                b = min(b, MovementGenerator.hashes[h].value)

            if a >= b:
                return MovementGenerator.hashes[h].value

        if depth == 0:
            return MovementGenerator.min_max_eval_board2(board)

        all_moves = board.move_gen_legal(Board2.LIGHT if iswhite else Board2.DARK, Board2.DARK if iswhite else Board2.LIGHT)
        val = -2000000
        for move in all_moves:
            b2 = board.copy()
            b2.do_move(move)
            val = max(val, -1 * self.neg_max_board2(b2, not iswhite, depth -1 ,-b, -a, maxd))

            if val > a and depth == maxd:
                self.saved_moved = move


            a = max(a, val)


            if a>= b:
                break



        _e = HashEntry()
        _e.value = val
        if val <= a_orig:
            _e.flag = HashEntry.UPPERBOUND
        elif val >= b:
            _e.flag = HashEntry.LOWERBOUND
        else:
            _e.flag = HashEntry.EXACT
        _e.depth = depth
        MovementGenerator.hashes[h] = _e

        return val

    def get_next_move_neg_max_board2(self, board, iswhite, depth):
        #negamax(rootNode, depth, −∞, +∞, 1)
        print(self.neg_max_board2( board, iswhite, depth, -20000000, 20000000, depth))
        f, t, _ = self.saved_moved
        _board = Board()

        return "{}{}".format(ChessUtils.positionToChessCoordinates(f), ChessUtils.positionToChessCoordinates(t))

    def quiesce_2(self, a, b, board, iswhite):
        stand_pat = MovementGenerator.min_max_eval_board2(board)
        if stand_pat >= b:
            return b
        if a < stand_pat:
            a = stand_pat

        # get all moves
        all_moves = board.move_gen_legal(Board2.LIGHT if iswhite else Board2.DARK,
                                         Board2.DARK if iswhite else Board2.LIGHT)

        # filter caputre moves
        #print("Debug")
        #print(all_moves)
        capture_moves = [x for x in all_moves if x[2] == 1]

        for cm in capture_moves:
            _b = board.copy()
            _b.do_move(cm)
            score = 1 * self.quiesce_2(-b, -a, _b, not iswhite)

            if score >= b:
                return b
            if score > a:
                a = score

        return a


    def pv_search_b2(self, board, iswhite, depth, a, b, maxd):
        if depth == 0:
            return self.quiesce_2(a, b, board, iswhite)

        b_search_pv = True

        all_moves = board.move_gen_legal(Board2.LIGHT if iswhite else Board2.DARK,
                                         Board2.DARK if iswhite else Board2.LIGHT)
        for move in all_moves:
            # make move
            b2 = board.copy()
            b2.do_move(move)

            if b_search_pv:
                score = -1 * self.pv_search_b2(b2, not iswhite, depth-1, -b, -a, maxd)
            else:
                score = -1 * self.pv_search_b2(b2, not iswhite, depth -1, -a -1, -a, maxd)
                if score > a:
                    score = -1 * self.pv_search_b2(b2, not iswhite, depth -1 ,-b, -a, maxd)

            #unmake

            if score >= b:
                return b
            elif score > a:
                a = score
                b_search_pv = False
                if depth == maxd:
                    self.saved_moved = move

        return a


    def get_next_move_pv_search_board2(self, board, iswhite, depth):
        self.pv_search_b2(board, iswhite, depth, -20000000, 20000000, depth)
        f, t, _ = self.saved_moved


        return "{}{}".format(ChessUtils.positionToChessCoordinates(f), ChessUtils.positionToChessCoordinates(t))


    def get_next_move_pv_search_board1(self, board, iswhite, depth):
        self.pv_search_b1(board, iswhite, depth, -2000000, 2000000, depth)

        return self.saved_moved

    def get_next_move_pv_search_board1_zws(self, board, iswhite, depth):
        self.pv_search_b1_ZWS(board, iswhite, depth, -2000000, 2000000, depth)

        return self.saved_moved

    def pv_search_b1(self, board, iswhite, depth, a, b, maxd):
        if depth == 0:
            return self.quiesce_1(a, b, board, iswhite)

        b_search_pv = True

        _moves = board.legal_moves
        all_moves = [] + [x for x in _moves if board.is_capture(x)] + [x for x in _moves if not board.is_capture(x)]

        for move in all_moves:
            # make move
            board.push(move)

            if b_search_pv:
                score = -1 * self.pv_search_b1(board, not iswhite, depth-1, -b, -a, maxd)
            else:
                score = -1 * self.pv_search_b1(board, not iswhite, depth -1, -a -1, -a, maxd)
                if score > a:
                    score = -1 * self.pv_search_b1(board, not iswhite, depth -1 ,-b, -a, maxd)

            #unmake
            board.pop()

            if score >= b:
                return b
            elif score > a:
                a = score
                b_search_pv = False
                if depth == maxd:
                    self.saved_moved = move

        return a

    def quiesce_1(self, a, b, board, iswhite):
        stand_pat = MovementGenerator.min_max_eval_pychess(board)
        if stand_pat >= b:
            return b
        if a < stand_pat:
            a = stand_pat



        # filter caputre moves
        #print("Debug")
        #print(all_moves)

        capture_moves = [x for x in board.legal_moves if board.is_capture(x)]



        for cm in capture_moves:
            board.push(cm)

            score = -1 * self.quiesce_1(-b, -a, board, not iswhite)

            board.pop()

            if score >= b:
                return b
            if score > a:
                a = score

        return a


    def pv_search_b1_ZWS(self, board, iswhite, depth, a, b, maxd):
        if depth == 0:
            return self.quiesce_1(a, b, board, iswhite)

        b_search_pv = True



        for move in board.legal_moves:
            # make move
            board.push(move)

            if b_search_pv:
                score = -1 * self.pv_search_b1_ZWS(board, not iswhite, depth-1, -b, -a, maxd)
            else:
                score = -1 * self.zw_search_b1(-a, depth - 1 ,board, not iswhite)
                if score > a:
                    score = -1 * self.pv_search_b1_ZWS(board, not iswhite, depth -1 ,-b, -a, maxd)

            #unmake
            board.pop()

            if score >= b:
                return b
            elif score > a:
                a = score
                b_search_pv = False
                if depth == maxd:
                    self.saved_moved = move

        return a

    def zw_search_b1(self, b, depth, board, iswhite):
        if depth == 0:
            return self.quiesce_1(b-1, b, board, iswhite)

        for move in board.legal_moves:
            board.push(move)
            score = -1 * self.zw_search_b1(1-b, depth - 1, board, not iswhite)
            board.pop()
            if score >= b:
                return b
        return b-1


    def get_next_move_neg_max_WITHMEMORY(self, board, iswhite, depth):
        #negamax(rootNode, depth, −∞, +∞, 1)
        print(self.neg_max_WITHMEMORY( board, iswhite, depth, -20000000, 20000000, depth))
        f, t = self.saved_moved
        _board = Board()
        return "{}{}".format(_board.positionToChessCoordinates(f), _board.positionToChessCoordinates(t))


    def neg_max_WITHMEMORY(self, board, iswhite, depth, a, b, maxd):
        a_orig = a

        h = self.cu.get_board_hash_pychess(board)
        if h in MovementGenerator.hashes and iswhite in MovementGenerator.hashes[h] and MovementGenerator.hashes[h][iswhite].depth >= depth:
            if MovementGenerator.hashes[h][iswhite].flag == HashEntry.EXACT:
                return MovementGenerator.hashes[h][iswhite].value
            elif MovementGenerator.hashes[h][iswhite].flag == HashEntry.LOWERBOUND:
                a = max(a, MovementGenerator.hashes[h][iswhite].value)
            else:
                b = min(b, MovementGenerator.hashes[h][iswhite].value)

            if a >= b:
                return MovementGenerator.hashes[h][iswhite].value

        if depth == 0:
            return MovementGenerator.min_max_eval_pychess(board)
            #return self.quiesce_1(a, b, board, iswhite)


        val = -2000000

        _moves  = board.legal_moves

        all_moves = [] + [x for x in _moves if board.is_capture(x)] + [x for x in _moves if not board.is_capture(x)]

        #for move in board.legal_moves:
        for move in all_moves:
            board.push(move)
            val = max(val, -1 * self.neg_max_WITHMEMORY(board, not iswhite, depth -1 ,-b, -a, maxd))
            board.pop()

            if val > a and depth == maxd:
                self.saved_moved = move


            a = max(a, val)


            if a>= b:
                break



        _e = HashEntry()
        _e.value = val
        if val <= a_orig:
            _e.flag = HashEntry.UPPERBOUND
        elif val >= b:
            _e.flag = HashEntry.LOWERBOUND
        else:
            _e.flag = HashEntry.EXACT
        _e.depth = depth
        if h not in MovementGenerator.hashes:
            MovementGenerator.hashes[h] = {}
        MovementGenerator.hashes[h][iswhite] = _e

        return val

    def MTDF(self, board, iswhite, f, depth, maxd):

        g = f
        upper = 20000000
        lower = -2000000

        while lower < upper:
            if g == lower:
                beta = g+1
            else:
                beta = g

            g = self.neg_max_WITHMEMORY(board, iswhite, depth, beta - 1, beta, maxd)

            if g < beta:
                upper = g
            else:
                lower = g
        return g

    def iterative_MTDF(self, board, iswhite, depth, max_seconds):
        first_guess = 0

        _start = time.time()

        if depth < 2:
            min_depth = depth
        else:
            min_depth = 2

        for d in range(min_depth, depth+1):
            first_guess = self.MTDF(board, iswhite, first_guess, d, d)
            print(d, self.saved_moved, min_depth, depth, time.time() - _start)
            if time.time() - _start > max_seconds:
                break
        return first_guess

    def get_next_move_MTDF(self, board, iswhite, depth):

        # check for openings
        open_move = self.get_opening_move(board)
        if open_move is not None:
            return open_move

        self.iterative_MTDF( board, iswhite, depth, 3)
        return self.saved_moved


