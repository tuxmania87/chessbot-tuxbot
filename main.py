import chess
import chessutil
import movegen
import cProfile
board = chess.Board()



print(board)


c = chessutil.ChessUtils()
mg = movegen.MovementGenerator()





#board.set_fen("rn1qkb1r/ppp1pppp/8/3p1b1n/3P4/2N2PB1/PPP1P1PP/R2QKBNR b KQkq - 2 5")
#board.set_fen("r5rk/5p1p/5R2/4B3/8/8/7P/7K w") # mate in 3
#
# board.set_fen("8/8/8/qn6/kn6/1n6/1KP5/8 w - -") # mate in 1
#board.set_fen("k1K5/1q6/2P3qq/q7/8/8/8/8 w - -") # mate in 3

#board.set_fen("2k3q1/7P/2K5/8/5q1q/8/8/5q2 w - -") # mate in 10

#board.set_fen("r2r1n2/pp2bk2/2p1p2p/3q4/3PN1QP/2P3R1/P4PP1/5RK1 w - - 0 1") # mate in 4


#board.set_fen("8/6Q1/3pp3/3k1p2/B4b2/2P2P2/PPK2P1P/8 w - - 3 29") # heab mate in 1


# mistake by gen 2
#board.set_fen("rnb1kb1r/pppqpp1p/5np1/8/3P4/2N1BQ2/PPP3PP/2KR1BNR b kq - 3 7")

board.set_fen("rn2kb1r/pp2p2p/2p1pnp1/q7/3P4/2N1BQ1P/PPP3P1/2KR2NR b kq - 1 10")

val = mg.min_max_eval_pychess_gen1(board)
print("gen 1", val)

val = mg.min_max_eval_pychess_gen2(board)
print("gen 2", val)


## DEBUG
'''
__b = board.copy()
__b.push_san("Ra6")
__b.push_san("f6")
__b.push_san("Bxf6")
__b.push_san("Rg7")

print("Hash ",c.get_board_hash_pychess(__b))
'''

## EO DEBUG


#pr = cProfile.Profile()
#pr.enable()


pr = cProfile.Profile()
pr.enable()

themove = mg.get_next_move_tuxfish(board, 10, 5)


pr.disable()
# after your program ends
pr.print_stats(sort="calls")

#board.push_san("cxb7+")
#themove = mg.get_next_move_tuxfish(board, 6, 10000)



#themove = mg.get_next_move_alpha_beta_static_2(board, 6, 100)





#pr.disable()
# after your program ends
#pr.print_stats(sort="calls")



#mg.get_next_move_pv_search_board1(board, False, 4)






