import random
#may need to do "positional scoring": piece in the center may have a higher score than the piece in the side.
#weird things happening for find move minmax 
pieceScore ={"K":0, "Q":9, "R":5, "B":3, "N":3, "p":1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
def findRandomMove(validMoves):
    return random.choice(tuple(validMoves))

def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentMoves = list(gs.getValidMoves())
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            #if we make better eval, we don't need to shuffle
            random.shuffle(opponentMoves)
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)
                if gs.checkmate:
                    score = -turnMultiplier*CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                score = -turnMultiplier*scoreBoard(gs.board)
                if (score > opponentMaxScore):
                    opponentMaxScore = score  
                gs.undoMove()
            if opponentMinMaxScore > opponentMaxScore:
                opponentMinMaxScore = opponentMaxScore
                bestPlayerMove = playerMove
            gs.undoMove()
    return bestPlayerMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            #if we make better eval, we don't need to shuffle
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, not gs.whiteToMove)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            try:
                nextMoves = random.shuffle(gs.getValidMoves())
            except:
                nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, not gs.whiteToMove)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore
    
def findBestMoveMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    return nextMove
    
#positive for white, negative for black
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in gs.board:
        for square in row:
            if square[0]=='w':
                score += pieceScore[square[1]]
            elif square[0]=='b':
                score -= pieceScore[square[1]]
    return score

def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier*scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        try:
            nextMoves = random.shuffle(gs.getValidMoves())
        except:
            nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore






    

















