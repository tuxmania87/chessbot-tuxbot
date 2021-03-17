import chess
import chessutil
import movegen
import cProfile
board = chess.Board()



print(board)


c = chessutil.ChessUtils()
mg = movegen.MovementGenerator()





board.set_fen("rn1q1rk1/pp3ppp/2pb1p2/8/3P2b1/2PB4/PP2NPPP/R1BQK2R w KQ - 5 9")
val = mg.min_max_eval_pychess(board)
print(val)

#pr = cProfile.Profile()
#pr.enable()




mg.get_next_move_MTDF(board, True, 4)



#pr.disable()
# after your program ends
#pr.print_stats(sort="calls")



#mg.get_next_move_pv_search_board1(board, False, 4)
print(mg.saved_moved, board.turn == chess.BLACK)





