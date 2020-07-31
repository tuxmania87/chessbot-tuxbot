import board
import chessutil
import random

b = board.Board()
c = chessutil.ChessUtils()


pos = 1

b.board  = ['' for i in range(64)]
b.board[pos] = 'n'


moves = c.getAllPieceMoves(b.board, pos)



b.renderBoard(highlights=moves)







