import board
import chessutil
import random
import movegen
import board2

b = board.Board()
c = chessutil.ChessUtils()


pos = 28




#b.board = [i for i in range(64)]
#b.renderBoard()

#b.board[pos] = 'N'

#moves = c.getAllPieceMoves(b.board, pos)
#moves = c.getAllPlayerMoves(b.board, True)
#b.renderBoard(highlights=moves)



import cProfile




pr = cProfile.Profile()
pr.enable()

b2 = board2.Board2()


mg = movegen.MovementGenerator()
print(mg.min_max_eval_board2(b2))


#best_move = mg.get_next_move_alpha_beta(b, True, 3)
best_move = mg.get_next_move_neg_max_board2(b2, True, 4)
print(best_move)

mmove = (chessutil.ChessUtils.ChessCoordinatesToPosition(best_move[:2]), chessutil.ChessUtils.ChessCoordinatesToPosition(best_move[2:]))

#b2.do_move(mmove)

#best_move = mg.get_next_move_neg_max_board2(b2, True, 3)
print(best_move)



pr.disable()
# after your program ends
pr.print_stats(sort="calls")

print(mg.saved_moved)











