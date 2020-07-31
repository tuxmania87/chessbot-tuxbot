
from PIL import Image, ImageDraw, ImageFont
import PySimpleGUI as sg

class Board:

    def __init__(self):
        self.board = ['' for i in range(64)]

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
