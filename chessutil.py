import random
from board2 import Board2

class HashEntry:

    EXACT = 1
    UPPERBOUND = 2
    LOWERBOUND = 3

    def __init__(self):
        self.upper = 0
        self.lower = 0


class ChessUtils:
    table = None

    hash_lookup_pieces = {
        "p" : 1,
        "P" : 2,
        "r" : 3,
        "R" : 4,
        "b" : 5,
        "B" : 6,
        "n" : 7,
        "N" : 8,
        "k" : 9,
        "K" : 10,
        "q" : 11,
        "Q" : 12

    }


    cols = ["a", "b", "c", "d", "e", "f", "g", "h"]

    @staticmethod
    def positionToChessCoordinates(position):

        x, y = ChessUtils.positionToCoordinages(position)

        return "{}{}".format(ChessUtils.cols[x],y+1)

    @staticmethod
    def ChessCoordinatesToPosition(f):

        x = f[0]
        y = int(f[1])


        x2 = int(ChessUtils.cols.index(x))

        print(x2, y)

        return (y - 1) * 8 + (x2 - 1) + 1

    @staticmethod
    def positionToCoordinages(position):

        return position % 8, position // 8


    def random_bitstring(self):
        return random.randint(0, 2 ** 64 - 1)

    def init_hash(self):
        global table
        table = [[] for _ in range(64)]
        for i in range(64):
            table[i] = [[] for _ in range(12)]
            for j in range(12):
                table[i][j] = self.random_bitstring()

    def get_board_hash(self, board):
        '''
        constant indices
        white_pawn := 1
        white_rook := 2
        # etc.
        black_king := 12

        '''



        h = 0
        for i in range(64):
            if board[i] != '':

                j = self.hash_lookup_pieces[board[i]] -1

                h = h ^ table[i][j]

        return h


    def get_board_hash_board2(self, board):
        '''
        constant indices
        white_pawn := 1
        white_rook := 2
        # etc.
        black_king := 12

        '''



        h = 0
        for i in range(64):
            if board.piece[i] != Board2.EMPTY:


                if board.color[i] == Board2.DARK:
                    j = board.piece[i] * 2
                else:
                    j = board.piece[i] * 2 +1


                h = h ^ table[i][j]

        return h

    def __init__(self):
        pass

        self.table = None
        self.init_hash()

        self.moves = {}
        self.moves["NORTH"] = 8
        self.moves["SOUTH"] = -8
        self.moves["EAST"] = 1
        self.moves["WEST"] = -1
        self.moves["SOUTH EAST"] = -7
        self.moves["SOUTH WEST"] = -9
        self.moves["NORTH EAST"] = 9
        self.moves["NORTH WEST"] = 7

        self.moves["NORTH NORTH WEST"] = 15
        self.moves["NORTH NORTH EAST"] = 17
        self.moves["EAST EAST NORTH"] = 10
        self.moves["EAST EAST SOUTH"] = -6
        self.moves["SOUTH SOUTH EAST"] = -15
        self.moves["SOUTH SOUTH WEST"] = -17
        self.moves["WEST WEST SOUTH"] = -10
        self.moves["WEST WEST NORTH"] = 6


    def crossingborders(self, position, direction, piece="X"):
        checkpos = position - self.moves[direction]
        if piece.lower() == "n":

            if (checkpos - 1) % 8 == 0 and direction.find("WEST") == 0:
                return True

            if (checkpos + 2 ) % 8 == 0 and direction.find("EAST") == 0:
                return True


        #print("CC ", position, direction)

        if checkpos < 0:
            return True

        # check left border
        if checkpos % 8 == 0 and "WEST" in direction:
            return True

        if (checkpos + 1) % 8 == 0 and "EAST" in direction:
            return True

        return False

    def getPieceThreats(self, board, position):
        legalmoves = self.getPieceMoves(board, position)

        if board[position].lower() == "p":
            legalmoves = self.getPawnTakeMoves(board, position)

        moves = []

        for move in legalmoves:
            if board[move] != '' and board[position].islower() != board[move].islower():
                moves.append(move)

        return moves

    def getPawnTakeMoves(self, board, position):

        moves = []
        filtermoves = []
        #check for white
        if board[position].islower():
            moves += self.getStraightMoves(board, position, "NORTH WEST", maxsteps=1)
            moves += self.getStraightMoves(board, position, "NORTH EAST", maxsteps=1)

            # check if there is enemy piece on it if yes its legal move
            for move in moves:
                if board[move] != '' and not board[move].islower():
                    filtermoves.append(move)

        else:
            moves += self.getStraightMoves(board, position, "SOUTH WEST", maxsteps=1)
            moves += self.getStraightMoves(board, position, "SOUTH EAST", maxsteps=1)

            # check if there is enemy piece on it if yes its legal move
            for move in moves:
                if board[move] != '' and board[move].islower():
                    filtermoves.append(move)

        return filtermoves

    def getStraightMoves(self, board, position, direction, maxsteps = 10000):
        moves = []
        #print("call ", position, direction)
        count = 0
        iter = position
        # conditions,
        # while not end of the board
        # and not hit any other piece

        abort = False

        while True:

            if count != 0:
                moves.append(iter)
                #print("c {} i {} d {}".format(count,iter,direction))

            count += 1
            iter += self.moves[direction]
            # if iter >= 64 or  board[iter] != '':
            if iter >= 64 or iter < 0 or count > maxsteps or self.crossingborders(iter,direction, board[position]) or abort:
                #print("break 1")
                break

            # if there is a piece and my piece is a pawn, not way of crossing, IF its not a take move
            if board[iter] != '' and board[position].lower() == "p" and (direction == "NORTH" or direction == "SOUTH"):
                #print("pawnbreak")
                break;

            # if found piece is not own color, add legal move but abort after that, and no pawn
            if board[iter] != '' and board[iter].islower() != board[position].islower():
                #print("break 2")
                abort = True
                maxsteps += 1

            # if piece is own abort now
            if board[iter] != '' and board[iter].islower() == board[position].islower():
                #print("break 3")
                break
        #print("return ",moves)
        return moves

    def isPlayerInCheck(self, board, iswhite):
        # get all threats of enemies and check if one is my king
        for i in range(64):
            if board[i] != '' and \
                    ((board[i].islower() and not iswhite) or (not board[i].islower() and iswhite)):
                # get all enemy moves
                moves = self.getPieceThreats(board, i)
                # if one of it is my king then check
                for move in moves:
                    if ((board[move] == 'k' and iswhite) or (board[move] == 'K' and not iswhite)):
                        return True

        return False

    def isPlayerInCheckMate(self, board, iswhite):

        # find my king
        kingpos = -1

        for i in range(64):
            if (board[i] == "k" and iswhite) or (board[i]=="K" and not iswhite):
                kingpos = i
                break

        # get all legal Kings moves
        moves = self.getAllPieceMoves(board, kingpos)

        # filter moves

        moves = self.filterKingsMoves(board, moves, kingpos)


        if self.isPlayerInCheck(board,iswhite) and len(moves) == 0:
            return True

        return False


    def filterKingsMoves(self, board, moves, position):
        moves2 = []

        iswhite = board[position].islower()


        # check if threatlist contains any move of the king if not take over
        for m in moves:

            #creat temp board by doing move and then do check test
            board_temp = board.copy()
            board_temp[position] = ''

            if iswhite:
                board_temp[m] = 'k'
            else:
                board_temp[m] = 'K'

            if not self.isPlayerInCheck(board_temp, iswhite):
                moves2.append(m)


        return moves2

    def getAllPlayerMoves(self, board, iswhite):

        allmoves = []

        for i in range(64):


            #print("Check for ", i)

            if (board[i] != '' and board[i].islower() and iswhite) or (board[i] != '' and not board[i].islower() and not iswhite):
                possible_moves = self.getAllPieceMoves(board, i)

                #print("Check for ", i, possible_moves)

                for targets in possible_moves:
                    allmoves.append((i, targets))

        filteredMoves = []

        # if in check then only consider moves that bring you out of check
        if self.isPlayerInCheck(board, iswhite):
            #print("CHECK FILTER")
            # for each move create temp board and see if in check, if not consider it
            for move in allmoves:
                f,t = move

                temp_board = board.copy()

                piece = temp_board[f]
                temp_board[f] = ''
                temp_board[t] = piece

                if not self.isPlayerInCheck(temp_board, iswhite):
                    filteredMoves.append(move)

            allmoves = filteredMoves


        else:
            filteredMoves = allmoves

        return allmoves


    def getAllPieceMoves(self, board, position):

        moves = self.getPieceMoves(board, position)
        if board[position].lower() == 'k':
            moves = self.filterKingsMoves(board, moves, position)
        return moves;


    def getPieceMoves(self, board, position):

        # only test implement bishios

        moves = []

        if board[position] == '':
            return moves


        if board[position] == 'b' or board[position] == "B":
            # check all diagonals

            moves += (self.getStraightMoves(board, position, "NORTH WEST"))
            moves += (self.getStraightMoves(board, position, "NORTH EAST"))
            moves += (self.getStraightMoves(board, position, "SOUTH WEST"))
            moves += (self.getStraightMoves(board, position, "SOUTH EAST"))

        elif board[position] == 'p':
            # if pawn is in base line, also allow two field leap
            if position >= 8 and position < 16:
                steps = 2
            else:
                steps = 1
            moves += (self.getStraightMoves(board, position, "NORTH", maxsteps=steps))


        elif board[position] == 'P':
            moves += (self.getStraightMoves(board, position, "SOUTH", maxsteps=1))

        elif board[position] == 'r' or board[position] == "R":
            # check all diagonals

            moves += (self.getStraightMoves(board, position, "NORTH"))
            moves += (self.getStraightMoves(board, position, "EAST"))
            moves += (self.getStraightMoves(board, position, "WEST"))
            moves += (self.getStraightMoves(board, position, "SOUTH"))

        elif board[position] == 'q' or board[position] == "Q":
            # check all diagonals

            moves += (self.getStraightMoves(board, position, "NORTH"))
            moves += (self.getStraightMoves(board, position, "EAST"))
            moves += (self.getStraightMoves(board, position, "WEST"))
            moves += (self.getStraightMoves(board, position, "SOUTH"))
            moves += (self.getStraightMoves(board, position, "NORTH WEST"))
            moves += (self.getStraightMoves(board, position, "NORTH EAST"))
            moves += (self.getStraightMoves(board, position, "SOUTH WEST"))
            moves += (self.getStraightMoves(board, position, "SOUTH EAST"))

        elif board[position] == 'k' or board[position] == "K":
            # check all diagonals

            moves += (self.getStraightMoves(board, position, "NORTH", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "EAST", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "WEST", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "SOUTH", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "NORTH WEST", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "NORTH EAST", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "SOUTH WEST", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "SOUTH EAST", maxsteps=1))


        elif board[position] == 'n' or board[position] == "N":

            moves += (self.getStraightMoves(board, position, "NORTH NORTH WEST", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "NORTH NORTH EAST", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "EAST EAST NORTH", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "EAST EAST SOUTH", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "SOUTH SOUTH EAST", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "SOUTH SOUTH WEST", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "WEST WEST SOUTH", maxsteps=1))
            moves += (self.getStraightMoves(board, position, "WEST WEST NORTH", maxsteps=1))


        if board[position].lower() == 'p':
            moves += self.getPawnTakeMoves(board,position)

        return moves



