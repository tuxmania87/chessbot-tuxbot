import board
import chessutil
import random

b = board.Board()
c = chessutil.ChessUtils()


pos = 28




#b.board = [i for i in range(64)]
#b.renderBoard()

#b.board[pos] = 'N'
#moves = c.getAllPieceMoves(b.board, pos)
#b.renderBoard(highlights=moves)


b.board = ['' for i in range(64)]
b.board[60] = 'K'

b.board[28] = 'r'


print(c.isPlayerInCheck(b.board, False))

#b.renderBoard()






