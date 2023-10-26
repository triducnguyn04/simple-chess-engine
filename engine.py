import numpy as np
#storing all the information about the current state of the game, generate valid moves, etc.
#suggestion: numpy list, set and dictionary to store data more efficiently

class GameState():
    def __init__(self):
        #initial state of the game 
        # "--" means empty squares
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],
        ]
        self.moveFunctions = {'p':self.getPawnMoves,'R':self.getRookMoves,'N':self.getKnightMoves,'B':self.getBishopMoves,'Q':self.getQueenMoves,'K':self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()
        self.castleRightsLog = [(True,True,True,True)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol]= "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove 

        #update the king's location
        if move.pieceMoved=='wK':
            self.whiteKingLocation=(move.endRow,move.endCol)
        elif move.pieceMoved=='bK':
            self.blackKingLocation=(move.endRow,move.endCol)

        #promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol]=move.pieceMoved[0]+'Q'

        #enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'

        #update enpassantPossible
        if (move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow)==2):
            self.enpassantPossible=((move.startRow+move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible=()

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:     #kingside
                self.board[move.endRow][move.endCol-1]=self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1]='--'
            else:                                    #queenside
                self.board[move.endRow][move.endCol+1]=self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2]='--'
        #update castling rights
        self.updateCastleRights(move)

    #undo the last move made
    def undoMove(self):
        if len(self.moveLog)!=0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol]= move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove 
            
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol]='--'
                self.board[move.startRow][move.endCol]=move.pieceCaptured
                self.enpassantPossible=(move.endRow,move.endCol)
            if (move.pieceMoved[1]=='p' and abs(move.endRow-move.startRow)==2):
                self.enpassantPossible=()

                #need to check for pins considering en passant! make move then undomove in this case!
                #cannot use enpassant to stop checks. 
            self.castleRightsLog.pop()

            #track white and black king postition!
            if move.pieceMoved[1] == 'K':
                if move.isCastleMove:
                    if move.endCol - move.startCol == 2:        #kingside
                        self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                        self.board[move.endRow][move.endCol-1] = '--'
                    else:                                       #queenside
                        self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                        self.board[move.endRow][move.endCol+1] = '--'
                if self.whiteToMove:
                    self.whiteKingLocation=(move.startRow,move.startCol)
                else:
                    self.blackKingLocation=(move.startRow,move.startCol)
           
    def updateCastleRights(self,move):
        temp=list(self.castleRightsLog[-1])
        if move.pieceMoved == 'wK':
            temp[0]=False
            temp[1]=False
        elif move.pieceMoved == 'bK':
            temp[2]=False
            temp[3]=False
        elif move.pieceMoved == 'wR':
            if move.startRow==7:
                if move.startCol==0:
                    temp[1]=False
                if move.startCol==7:
                    temp[0]=False
        elif move.pieceMoved == 'bR':
            if move.startRow==0:
                if move.startCol==0:
                    temp[3]=False
                if move.startCol==7:
                    temp[2]=False
        self.castleRightsLog.append((temp[0],temp[1],temp[2],temp[3]))
        
    #return if player is in check, a list of pins, a list of checks
    def checkforPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor='b'
            allyColor='w'
            startRow=self.whiteKingLocation[0]
            startCol=self.whiteKingLocation[1]
        else:
            enemyColor='w'
            allyColor='b'
            startRow=self.blackKingLocation[0]
            startCol=self.blackKingLocation[1]
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(8):
            d=directions[j]
            possiblePin=()
            for i in range(1,8):
                endRow=startRow+d[0]*i
                endCol=startCol+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece[0]==allyColor and endPiece[1]!='K':
                        if possiblePin==():
                            possiblePin=(endRow,endCol,d[0],d[1])
                        else:                           #2nd allied piece, so no pin!
                            break                       #no pin from that direction, no check either
                    elif endPiece[0]==enemyColor:
                        type = endPiece[1]
                        # 5 possibilities here!
                        #1) orthogonally away and it's a rook or queen
                        #2) diagonally away and it's a bishop or queen
                        #3) 1 square away and it's a pawn
                        #4) any direction 1 square away and piece is a king
                        if (0<=j<=3 and type=='R') or \
                           (4<=j<=7 and type=='B') or \
                           (i==1 and type == 'p') and ((enemyColor=='w' and 6<=j<=7) or (enemyColor=='b' and 4<=j<=5)) or \
                           (type=='Q'):
                            if possiblePin==():
                                inCheck=True
                                checks.append((endRow,endCol,d[0],d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:   #enemy pieces not applying checks
                            break
                else:
                    break       #off board

        #check for knight checks
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]==enemyColor and endPiece[1]=='N':
                    inCheck=True
                    checks.append((endRow,endCol,m[0],m[1]))
        return inCheck,pins,checks

    #generate valid moves (considering checks)
    def getValidMoves(self): 
        self.inCheck,self.pins,self.checks=self.checkforPinsAndChecks()
        moves=set()
        valid_moves=set()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks)==1:                     #only one check, not double check
                moves=self.getAllPossibleMoves()
                check=self.checks[0]
                checkRow=check[0]
                checkCol=check[1]
                pieceChecking=self.board[checkRow][checkCol]
                validSquares = set()
                if pieceChecking[1]=='N':
                    validSquares = [(checkRow,checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2]*i, kingCol + check[3]*i)
                        validSquares.add(validSquare)
                        if validSquare==(checkRow,checkCol):
                            break
                #get rid of any moves that don't block check or move king
                for i in moves:
                    if i.pieceMoved[1]=='K' or (i.endRow,i.endCol) in validSquares:
                        valid_moves.add(i)
            else:
                #double check
                self.getKingMoves(kingRow,kingCol,valid_moves)
        else:
            valid_moves=self.getAllPossibleMoves()
            #castle move if castle rights true
            if self.whiteToMove:
                if self.castleRightsLog[-1][0] or self.castleRightsLog[-1][1]:
                    self.getCastleMoves(kingRow,kingCol,valid_moves)
            else:   
                if self.castleRightsLog[-1][2] or self.castleRightsLog[-1][3]:
                    self.getCastleMoves(kingRow,kingCol,valid_moves)
        if len(valid_moves)==0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return valid_moves

    #generate all possible moves (without considering checks)
    #it's an expensive function. Looking forward to generate each move individually and check if it's okay
    def getAllPossibleMoves(self):
        moves=set()
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn =='w' and self.whiteToMove) or (turn=='b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves

    def getPawnMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if self.board[r-1][c]=="--":            #empty square in front of white pawn
                if not piecePinned or pinDirection == (-1,0):
                    moves.add(Move((r,c),(r-1,c),self.board))
                    if r==6 and self.board[r-2][c]=="--":  
                        moves.add(Move((r,c),(r-2,c),self.board))
            #capture for white                                        
            if c-1>=0:
                if self.board[r-1][c-1][0]=='b':
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.add(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1)==self.enpassantPossible:
                    if self.whiteKingLocation[0]==r:
                        temp = (self.board[r][c],self.board[r][c-1])
                        self.board[r][c] ='--'
                        self.board[r][c-1] = '--'
                        if not self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1]):
                            moves.add(Move((r,c),(r-1,c-1),self.board))
                        self.board[r][c] = temp[0]
                        self.board[r][c-1] = temp[1]
                    else:
                        moves.add(Move((r,c),(r-1,c-1),self.board))
            if c+1<=7:
                if self.board[r-1][c+1][0]=='b':
                    if not piecePinned or pinDirection == (-1,1):
                        moves.add(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1)==self.enpassantPossible:
                    if self.whiteKingLocation[0]==r:
                        temp = (self.board[r][c],self.board[r][c+1])
                        self.board[r][c] ='--'
                        self.board[r][c+1] = '--'
                        if not self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1]):
                            moves.add(Move((r,c),(r-1,c+1),self.board))
                        self.board[r][c] = temp[0]
                        self.board[r][c+1] = temp[1]
                    else:
                        moves.add(Move((r,c),(r-1,c+1),self.board))
        else:
            if self.board[r+1][c]=="--":            #empty square in front of black pawn
                if not piecePinned or pinDirection == (1,0):
                    moves.add(Move((r,c),(r+1,c),self.board))
                    if r==1 and self.board[r+2][c]=="--":  
                        moves.add(Move((r,c),(r+2,c),self.board))
            #capture for black                                       
            if c-1>=0:
                if self.board[r+1][c-1][0]=='w':
                    if not piecePinned or pinDirection == (1,-1):
                        moves.add(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1)==self.enpassantPossible:
                    if self.blackKingLocation[0]==r:
                        temp = (self.board[r][c],self.board[r][c-1])
                        self.board[r][c] ='--'
                        self.board[r][c-1] = '--'
                        if not self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1]):
                            moves.add(Move((r,c),(r+1,c-1),self.board))
                        self.board[r][c] = temp[0]
                        self.board[r][c-1] = temp[1]
                    else:
                        moves.add(Move((r,c),(r+1,c-1),self.board))
            if c+1<=7:
                if self.board[r+1][c+1][0]=='w':
                    if not piecePinned or pinDirection == (1,1):
                        moves.add(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1)==self.enpassantPossible:
                    if self.blackKingLocation[0]==r:
                        temp = (self.board[r][c],self.board[r][c+1])
                        self.board[r][c] ='--'
                        self.board[r][c+1] = '--'
                        if not self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1]):
                            moves.add(Move((r,c),(r+1,c+1),self.board))
                        self.board[r][c] = temp[0]
                        self.board[r][c+1] = temp[1]
                    else:
                        moves.add(Move((r,c),(r+1,c+1),self.board))

    def getRookMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                if self.board[r][c][1]!='Q':    #can't remove queen from rook moves, only on bishop moves
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1,0),(1,0),(0,-1),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0<=endRow<8 and 0<=endCol<8: #on board
                    if not piecePinned or (pinDirection == d or pinDirection == (-d[0],-d[1])):
                        if self.board[endRow][endCol]=='--': #empty space valid
                            moves.add(Move((r,c),(endRow,endCol),self.board))
                        elif self.board[endRow][endCol][0]==enemyColor:
                            moves.add(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                else:
                    break
        
    def getKnightMoves(self,r,c,moves):
        #knights cannot move when pinned
        piecePinned=False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                self.pins.remove(self.pins[i])
                break
        directions = ((-1,2),(-1,-2),(1,-2),(1,2),(-2,1),(-2,-1),(2,-1),(2,1))
        allyColor = "w" if self.whiteToMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0<=endRow<8 and 0<=endCol<8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0]!=allyColor:      #not an ally piece
                        moves.add(Move((r,c),(endRow,endCol),self.board))

    def getBishopMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                if self.board[r][c][1]!='Q':    #can't remove queen from rook moves, only on bishop moves
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1,1),(-1,-1),(1,-1),(1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0<=endRow<8 and 0<=endCol<8: #on board
                    if not piecePinned or (pinDirection == d or pinDirection == (-d[0],-d[1])):
                        if self.board[endRow][endCol]=='--': #empty space valid
                            moves.add(Move((r,c),(endRow,endCol),self.board))
                        elif self.board[endRow][endCol][0]==enemyColor:
                            moves.add(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                else:
                    break

    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getKingMoves(self,r,c,moves):
        rowMoves=(-1,-1,-1,0,0,1,1,1)
        colMoves=(-1,0,1,-1,1,-1,0,1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow=r+rowMoves[i]
            endCol=c+colMoves[i]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=allyColor:
                    if not self.squareUnderAttack(endRow, endCol):
                        moves.add(Move((r,c),(endRow,endCol),self.board))

    def getCastleMoves(self,r,c,moves):
        if (self.whiteToMove and self.castleRightsLog[-1][0]) or ((not self.whiteToMove) and self.castleRightsLog[-1][2]):
            self.getKingSideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.castleRightsLog[-1][1]) or ((not self.whiteToMove) and self.castleRightsLog[-1][3]):
            self.getQueenSideCastleMoves(r,c,moves)

    def getKingSideCastleMoves(self,r,c,moves):
        if self.board[r][c+1]=='--' and self.board[r][c+2]=='--':
            if (not self.squareUnderAttack(r,c+1)) and (not self.squareUnderAttack(r,c+2)):
                moves.add(Move((r,c),(r,c+2),self.board))

    def getQueenSideCastleMoves(self,r,c,moves):
        if self.board[r][c-1]=='--' and self.board[r][c-2]=='--' and self.board[r][c-3]=='--':
            if (not self.squareUnderAttack(r,c-1)) and (not self.squareUnderAttack(r,c-2)):
                moves.add(Move((r,c),(r,c-2),self.board))
    
    def squareUnderAttack(self, r, c):
        if self.whiteToMove:
            enemyColor='b'
            allyColor='w'
        else:
            enemyColor='w'
            allyColor='b'
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(8):
            d=directions[j]
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece[0]==allyColor:
                        break                       
                    elif endPiece[0]==enemyColor:
                        type = endPiece[1]
                        if (0<=j<=3 and type=='R') or \
                           (4<=j<=7 and type=='B') or \
                           (i==1 and type == 'p') and ((enemyColor=='w' and 6<=j<=7) or (enemyColor=='b' and 4<=j<=5)) or \
                           (type=='Q') or (i==1 and type == 'K'):
                            return True
                        else:   
                            break
                else:
                    break      

        #check for knight checks
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]==enemyColor and endPiece[1]=='N':
                    return True
        return False

class Move():
    ranksToRows = {"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #enpassant
        self.isEnpassantMove = (self.pieceMoved[1]=='p' and self.pieceCaptured=='--' and self.startCol!=self.endCol)
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        #((self.pieceMoved[1]=='p' and (self.endRow, self.endCol)==enpassantPossible))
            
        #castle move
        self.isCastleMove = (self.pieceMoved[1]=='K' and abs(self.endCol - self.startCol) == 2)

        #may try underpromotion later
        self.promotionChoice = 'Q'
        self.isPawnPromotion = ((self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7))
        self.moveID = (self.startRow+1) * 1000 + (self.startCol+1) * 100 + (self.endRow+1) * 10 + (1+self.endCol) + (10000 if self.isCastleMove else 0)

    #overiding the equal method. neccessary to compare two different objects. not a good idea, need improvement
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        else:
            return False
        
    def __hash__(self):
        return self.moveID

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow,self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c]+self.rowsToRanks[r]
