import board
import chessutil
import random
import movegen

b = board.Board()
c = chessutil.ChessUtils()


pos = 28




#b.board = [i for i in range(64)]
#b.renderBoard()

#b.board[pos] = 'N'
#moves = c.getAllPieceMoves(b.board, pos)
#moves = c.getAllPlayerMoves(b.board, True)
#b.renderBoard(highlights=moves)


print(movegen.MovementGenerator.min_max_eval(b))

mg = movegen.MovementGenerator()

best_move = mg.get_next_move_min_max(b, True)

b.board = ['' for i in range(64)]
b.board[60] = 'K'

b.board[28] = 'r'

print(movegen.MovementGenerator.min_max_eval(b))

print(c.isPlayerInCheck(b.board, False))

b.renderBoard()






