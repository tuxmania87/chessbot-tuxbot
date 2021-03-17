import random

class Board2:

    EMPTY = -1
    LIGHT = 1
    DARK = 0

    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5

    def copy(self):

        _b = Board2()
        _b.piece = self.piece.copy()
        _b.color = self.color.copy()

        return _b


    def __init__(self):



        self.rook_moved = {
            0: False,
            7: False,
            56: False,
            63: False
        }

        self.king_moved = {
            4: False,
            60: False
        }


        self.color = [self.EMPTY for _ in range(64)]
        self.piece = [self.EMPTY for _ in range(64)]

        for i in range(0,16):
            self.color[i] = self.LIGHT

        for i in range (48,64):
            self.color[i] = self.DARK

        self.piece[0] = self.ROOK
        self.piece[1] = self.KNIGHT
        self.piece[2] = self.BISHOP
        self.piece[3] = self.QUEEN
        self.piece[4] = self.KING
        self.piece[5] = self.BISHOP
        self.piece[6] = self.KNIGHT
        self.piece[7] = self.ROOK

        for i in range(8, 16):
            self.piece[i] = self.PAWN

        # init black
        self.piece[56] = self.ROOK
        self.piece[57] = self.KNIGHT
        self.piece[58] = self.BISHOP
        self.piece[59] = self.QUEEN
        self.piece[60] = self.KING
        self.piece[61] = self.BISHOP
        self.piece[62] = self.KNIGHT
        self.piece[63] = self.ROOK

        for i in range(48, 56):
            self.piece[i] = self.PAWN


        self.mailbox = [
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

        self.mailbox64 = [
            21, 22, 23, 24, 25, 26, 27, 28,
            31, 32, 33, 34, 35, 36, 37, 38,
            41, 42, 43, 44, 45, 46, 47, 48,
            51, 52, 53, 54, 55, 56, 57, 58,
            61, 62, 63, 64, 65, 66, 67, 68,
            71, 72, 73, 74, 75, 76, 77, 78,
            81, 82, 83, 84, 85, 86, 87, 88,
            91, 92, 93, 94, 95, 96, 97, 98
        ]


    def do_move(self, move):

        f, t = move[0], move[1]

        # check if castle moves

        if f == 4 and t == 2 and self.piece[f] == self.KING:
            self.piece[2] = self.KING
            self.piece[3] = self.ROOK
            self.piece[0] = self.EMPTY
            self.piece[4] = self.EMPTY

            self.color[2] = self.LIGHT
            self.color[3] = self.LIGHT
            self.color[0] = self.EMPTY
            self.color[4] = self.EMPTY


        elif f == 4 and t == 6 and self.piece[f] == self.KING:
            self.piece[6] = self.KING
            self.piece[3] = self.ROOK
            self.piece[7] = self.EMPTY
            self.piece[4] = self.EMPTY

            self.color[6] = self.LIGHT
            self.color[3] = self.LIGHT
            self.color[7] = self.EMPTY
            self.color[4] = self.EMPTY

        elif f == 60 and t == 62 and self.piece[f] == self.KING:
            self.piece[62] = self.KING
            self.piece[61] = self.ROOK
            self.piece[63] = self.EMPTY
            self.piece[60] = self.EMPTY

            self.color[62] = self.DARK
            self.color[61] = self.DARK
            self.color[63] = self.EMPTY
            self.color[60] = self.EMPTY

        elif f == 60 and t == 58 and self.piece[f] == self.KING:
            self.piece[58] = self.KING
            self.piece[60] = self.EMPTY
            self.piece[61] = self.ROOK
            self.piece[56] = self.EMPTY

            self.color[58] = self.DARK
            self.color[60] = self.EMPTY
            self.color[61] = self.DARK
            self.color[56] = self.EMPTY
            #or f == 60 and t == 62 and piece[f] == KING \
            #or f == 60 and t == 58 and piece[f] == KING

        else:
            p = self.piece[f]
            self.piece[t] = p
            self.piece[f] = self.EMPTY

            pc = self.color[f]
            self.color[t] = pc
            self.color[f] = self.EMPTY

            if p == self.ROOK and f in [0,7,58,63]:
                self.rook_moved[f] = True

            if p == self.KING and f in [4,60]:
                self.king_moved[f] = True


    def is_player_in_check(self, side):
        # generate all moves for oponnent
        # if king can be taken, player was in check

        moves = self.move_gen(side, 1 if side == -1 else 1)

        for m in moves:
            if m[1] != self.EMPTY and self.piece[m[1]] == self.KING and self.color[m[1]] == side:
                return True
        return False


    def move_gen_pseudo_legal(self, side, xside):
        all_moves = []

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
            if self.color[i] == side:
                p = self.piece[i]
                if p != self.PAWN:



                    if p == self.KING:
                        # check castle moves

                        if self.color[i] == self.LIGHT:
                            if not self.rook_moved[0] and not self.king_moved[4] and self.color[3] == self.EMPTY and \
                                    self.color[2] == self.EMPTY and self.color[1] == self.EMPTY:
                                # check if squares are in check
                                # generate all enemy moves
                                op_moves = self.move_gen_pseudo_legal(xside, side)
                                abort = False
                                for _m in op_moves:
                                    f, t, c = _m
                                    if t in [4,3,2]:
                                        abort = True
                                        break

                                all_moves.append((4,2,0))

                            if not self.rook_moved[7] and not self.king_moved[4] and self.color[6] == self.EMPTY and self.color[5] == self.EMPTY:
                                # check if squares are in check
                                # generate all enemy moves
                                op_moves = self.move_gen_pseudo_legal(xside, side)
                                abort = False
                                for _m in op_moves:
                                    f, t, c = _m
                                    if t in [4, 3, 2]:
                                        abort = True
                                        break

                                all_moves.append((4, 7, 0))




                    for j in range(len(offset[0])):
                        n = i
                        while True:
                            # next square along the ray j
                            n = self.mailbox[self.mailbox64[n] + offset[p][j]]
                            if n == -1:
                                break

                            if self.color[n] != self.EMPTY:
                                if self.color[n] == xside:
                                    all_moves.append((i,n,1))
                                break

                            all_moves.append((i, n, 0))
                            if not slide[p]:
                                break
                else:
                    all_moves += self.get_pawn_moves(i)





        return all_moves

    #print(move_gen(1,-1))

    def get_pawn_moves(self,i):

        mm = []

        # print("pawnmove")

        if self.color[i] == self.LIGHT:
            candidates = [10]
            candidates64 = [8]
            if i < 16:
                candidates.append(20)
                candidates64.append(16)

            for ii in range(len(candidates)):
                n = self.mailbox[self.mailbox64[i] + candidates[ii]]
                if self.piece[i + candidates64[ii]] == self.EMPTY and self.color[
                    i + candidates64[ii]] == self.EMPTY and n != -1:
                    mm.append((i, n, 0))
        else:
            candidates = [-10]
            candidates64 = [-8]
            if i > 47:
                candidates.append(-20)
                candidates64.append(-16)

            for ii in range(len(candidates)):
                n = self.mailbox[self.mailbox64[i] + candidates[ii]]
                if self.piece[i + candidates64[ii]] == self.EMPTY and self.color[
                    i + candidates64[ii]] == self.EMPTY and n != -1:
                    mm.append((i, n, 0))

        # check pawn takes moves
        if self.color[i] == self.LIGHT:
            candidates = [9, 11]
            candidates64 = [7, 9]

            for ii in range(len(candidates)):
                n = self.mailbox[self.mailbox64[i] + candidates[ii]]
                if self.color[i + candidates64[ii]] == self.DARK and n != -1:
                    mm.append((i, n, 0))
        elif self.color[i] == self.DARK:
            candidates = [-9, -11]
            candidates64 = [-7, -9]

            for ii in range(len(candidates)):
                n = self.mailbox[self.mailbox64[i] + candidates[ii]]
                if self.color[i + candidates64[ii]] == self.LIGHT and n != -1:
                    mm.append((i, n, 0))

        return mm

    def helper(self, move, side, xside):

        b2 = self.copy()
        b2.do_move(move)

        op_moves = b2.move_gen_pseudo_legal(xside, side)

        for _om in op_moves:
            if _om[2] == 1 and self.piece[_om[1]] == self.KING and self.color[_om[1]] == side:
                return False
        return True

    def move_gen_legal(self, side, xside):

        all_moves = self.move_gen_pseudo_legal(side, xside)


        filtered_moves = []
        for _m in all_moves:
            # get all opponent moves

            if self.helper(_m, side, xside):
                filtered_moves.append(_m)

        return filtered_moves



