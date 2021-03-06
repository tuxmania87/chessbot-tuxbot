

class Board:

    def __init__(self):
        self.board = ['' for i in range(64)]

        self.castle_rights_long_black = True
        self.castle_rights_short_black = True

        self.castle_rights_long_white = True
        self.castle_rights_short_white = True

        # init white
        self.board[0] = 'r'
        self.board[1] = 'n'
        self.board[2] = 'b'
        self.board[3] = 'q'
        self.board[4] = 'k'
        self.board[5] = 'b'
        self.board[6] = 'n'
        self.board[7] = 'r'

        for i in range(8, 16):
            self.board[i] = 'p'

        # init black
        self.board[56] = 'R'
        self.board[57] = 'N'
        self.board[58] = 'B'
        self.board[59] = 'Q'
        self.board[60] = 'K'
        self.board[61] = 'B'
        self.board[62] = 'N'
        self.board[63] = 'R'

        for i in range(48, 56):
            self.board[i] = 'P'

        self.cols = ["a", "b", "c", "d", "e", "f", "g", "h"]

    def copy(self):
        new_b = Board()
        new_b.board = self.board.copy()
        return new_b

    def do_move(self, move):
        _p = self.board[move[0]]
        self.board[move[0]] = ''
        self.board[move[1]] = _p

        if _p == 'k':
            self.castle_rights_long_white = False
            self.castle_rights_short_white = False
        elif _p == 'K':
            self.castle_rights_long_black = False
            self.castle_rights_short_black = False




    def positionToChessCoordinates(self, position):

        x, y = self.positionToCoordinages(position)

        return "{}{}".format(self.cols[x],y+1)

    def ChessCoordinatesToPosition(self, f):

        x = f[0]
        y = int(f[1])


        x2 = int(self.cols.index(x))

        print(x2, y)

        return (y - 1) * 8 + (x2 - 1) + 1





    def positionToCoordinages(self, position):

        return position % 8, position // 8

