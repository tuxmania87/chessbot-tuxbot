from board import Board
from chessutil import ChessUtils
import random

class MovementGenerator:


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
