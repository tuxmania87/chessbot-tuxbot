import chess
import chessutil
import movegen
import cProfile
board = chess.Board()



print(board)


c = chessutil.ChessUtils()
mg = movegen.MovementGenerator()





board.set_fen("rn1qkb1r/ppp1pppp/8/3p1b1n/3P4/2N2PB1/PPP1P1PP/R2QKBNR b KQkq - 2 5")
val = mg.min_max_eval_pychess(board)
print(val)



#pr = cProfile.Profile()
#pr.enable()




themove = mg.get_next_move_alpha_beta_iterative_2(board, 5, 10)



#pr.disable()
# after your program ends
#pr.print_stats(sort="calls")



#mg.get_next_move_pv_search_board1(board, False, 4)
print(themove, board.turn == chess.BLACK)





