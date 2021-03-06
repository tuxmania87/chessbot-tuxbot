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

cu = chessutil.ChessUtils()
print(movegen.MovementGenerator.min_max_eval(b))

import cProfile



mg = movegen.MovementGenerator()

pr = cProfile.Profile()
pr.enable()


#best_move = mg.get_next_move_alpha_beta(b, True, 3)
best_move = mg.get_next_move_neg_max(b, True, 3)


pr.disable()
# after your program ends
pr.print_stats(sort="calls")

print(mg.saved_moved)

print(best_move)


cu = chessutil.ChessUtils()
_b = board.Board()

print(cu.get_board_hash(_b.board))

_b.do_move((10,18))

print(cu.get_board_hash(_b.board))







