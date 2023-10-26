#test code for AI play. It serves the purpose of building the intial evaluation dataset.
import engine
import smartMoveFinder

def main():
    gs = engine.GameState()
    gameOver = False
    validMoves = gs.getValidMoves()

    while True:
        #continue playing if game not over
        if not gameOver:
            AIMove = smartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            validMoves = gs.getValidMoves()
            gameOver = gs.stalemate or gs.checkmate
        else:
        #if game over then restart
            gs = engine.GameState()
            validMoves = gs.getValidMoves()

if __name__=="__main__":
    main()
