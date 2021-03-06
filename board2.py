import random


EMPTY = 0
LIGHT = 1
DARK = -1

PAWN = 0
KNIGHT = 1
BISHOP = 2
ROOK = 3
QUEEN = 4
KING = 5


color = [EMPTY for i in range(64)]
piece = [0 for i in range(64)]

for i in range(0,16):
    color[i] = LIGHT

for i in range (48,64):
    color[i] = DARK

piece[0] = ROOK
piece[1] = KNIGHT
piece[2] = BISHOP
piece[3] = QUEEN
piece[4] = KING
piece[5] = BISHOP
piece[6] = KNIGHT
piece[7] = ROOK

for i in range(8, 16):
    piece[i] = PAWN

# init black
piece[56] = ROOK
piece[57] = KNIGHT
piece[58] = BISHOP
piece[59] = QUEEN
piece[60] = KNIGHT
piece[61] = BISHOP
piece[62] = KNIGHT
piece[63] = ROOK

for i in range(48, 56):
    piece[i] = PAWN

piece[11] = EMPTY
color[11] = EMPTY

mailbox = [
     -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
     -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
     -1,  0,  1,  2,  3,  4,  5,  6,  7, -1,
     -1,  8,  9, 10, 11, 12, 13, 14, 15, -1,
     -1, 16, 17, 18, 19, 20, 21, 22, 23, -1,
     -1, 24, 25, 26, 27, 28, 29, 30, 31, -1,
     -1, 32, 33, 34, 35, 36, 37, 38, 39, -1,
     -1, 40, 41, 42, 43, 44, 45, 46, 47, -1,
     -1, 48, 49, 50, 51, 52, 53, 54, 55, -1,
     -1, 56, 57, 58, 59, 60, 61, 62, 63, -1,
     -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
     -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
]

mailbox64 = [
    21, 22, 23, 24, 25, 26, 27, 28,
    31, 32, 33, 34, 35, 36, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48,
    51, 52, 53, 54, 55, 56, 57, 58,
    61, 62, 63, 64, 65, 66, 67, 68,
    71, 72, 73, 74, 75, 76, 77, 78,
    81, 82, 83, 84, 85, 86, 87, 88,
    91, 92, 93, 94, 95, 96, 97, 98
]




def move_gen():
    side = 1
    xside = -1
    slide = [False, False, True, True, True, False]
    offsets = [0, 8, 4, 4, 8, 8]
    offset = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [-21, -19, -12, -8, 8, 12, 19, 21], #Knight
        [-11, -9, 9, 11, 0, 0, 0, 0], #Bishop
        [-10, -1, 1, 10, 0, 0, 0, 0], #Rook
        [-11, -10, -9, -1, 1, 9, 10, 11], #Queen
        [-11, -10, -9, -1, 1, 9, 10, 11], #King
    ]

    for i in range(64):
        if color[i] == side:
            p = piece[i]
            if p != PAWN:
                for j in range(len(offsets)):
                    n = i
                    while True:
                        # next square along the ray j
                        n = mailbox[mailbox64[n] + offset[p][j]]
                        if n == -1:
                            break

                        if color[n] != EMPTY:
                            if color[n] == xside:
                                #genMove(i, n, 1)
                                print(i,n, 1)
                            break

                        #genMove(i, n, 0)
                        print(i, n, 0)
                        if not slide[p]:
                            break
            else:
                print("pawnmove")
                pass


#move_gen()

init_hash()
print(get_board_hash(piece))
print(get_board_hash(piece))