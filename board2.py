
from PIL import Image, ImageDraw, ImageFont
import PySimpleGUI as sg

class Board2:

    def __init__(self):
        self.board = ['' for i in range(144)]

        self.castle_rights_long_black = True
        self.castle_rights_short_black = True

        self.castle_rights_long_white = True
        self.castle_rights_short_white = True

        # init white
        self.board[26] = 'r'
        self.board[27] = 'n'
        self.board[28] = 'b'
        self.board[29] = 'q'
        self.board[30] = 'k'
        self.board[31] = 'b'
        self.board[32] = 'n'
        self.board[33] = 'r'

        for i in range(38, 46):
            self.board[i] = 'p'

        # init black
        self.board[110] = 'R'
        self.board[111] = 'N'
        self.board[112] = 'B'
        self.board[113] = 'Q'
        self.board[114] = 'K'
        self.board[115] = 'B'
        self.board[116] = 'N'
        self.board[117] = 'R'

        for i in range(98, 106):
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

    def renderBoard(self, highlights=None):

        layout = [
            [
                sg.Graph(
                    canvas_size=(600, 600),
                    graph_bottom_left=(0, 0),
                    graph_top_right=(600, 600),
                    key="graph"
                )
            ]
        ]

        window = sg.Window("Chess", layout)
        window.Finalize()

        graph = window.Element("graph")

        graph.DrawImage(filename="board.png", location=(0,600))



        #graph.DrawRectangle((0,0),(600/8 +1,600/8+1), line_color="red")

        scale_width = 600 / 8

        for i in range(64):

            # calculate coordinates
            x,y = self.positionToCoordinages(i)

            x += 1
            y += 1

            # multiply to scale
            x = x * scale_width - scale_width/2
            y = y * scale_width - scale_width/2

            graph.DrawText(self.board[i],location=(x,y),color="red",font=("Courier New", 20))

        if highlights != None:
            for pos in highlights:
                x, y = self.positionToCoordinages(pos)
                graph.DrawRectangle(top_left=(x*scale_width, y*scale_width),  bottom_right=(x*scale_width + scale_width, y*scale_width+scale_width), line_color="blue",line_width=10)



        window.read()
