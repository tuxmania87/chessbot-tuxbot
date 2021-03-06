from board import Board
from chessutil import ChessUtils, HashEntry
import random
import time

class MovementGenerator:

    cu = ChessUtils()


    def __init__(self):

        self.cu = ChessUtils()
        self.saved_moved = ""
        self.hashes = {}


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
        if h in self.hashes and self.hashes[h].depth >= depth:
            if self.hashes[h].flag == HashEntry.EXACT:
                return self.hashes[h].value
            elif self.hashes[h].flag == HashEntry.LOWERBOUND:
                a = max(a, self.hashes[h].value)
            else:
                b = min(b, self.hashes[h].value)

            if a >= b:
                return self.hashes[h].value

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
        self.hashes[h] = _e

        return val




