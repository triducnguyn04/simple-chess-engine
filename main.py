#display and get user input
import pygame as p
import engine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}

#initialize a global dictionary for images, which would be called only once in the main
def loadImages():
    pieces = ['wp','wN','wB','wQ','wK','wR','bp','bN','bR','bB','bQ','bK']
    for piece in pieces:
        IMAGES[piece]=p.transform.scale(p.image.load("images/"+piece+".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.GameState()
    loadImages()
    running = True
    sqSelected = ()                             #no square selected, variable to keep track of clicked square
    playerClicks = []                           #keep track of player's clicks, two tuples [(6,4),(4,4)]
    validMoves = gs.getValidMoves()
    movemade = False
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row,col):
                    sqSelected=()
                    playerClicks = []
                else:
                    sqSelected=(row,col)
                    playerClicks.append(sqSelected)

                if len(playerClicks)==2:        #after 2nd click
                    move = engine.Move(playerClicks[0], playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move==validMoves[i]:
                            gs.makeMove(validMoves[i])
                            movemade=True
                            sqSelected = ()
                            playerClicks = []
                    if not movemade:
                        #should fix: if player click an invalid move and it is his color then change, else delete
                        playerClicks = [sqSelected]
            #key handlers
            elif e.type==p.KEYDOWN:
                if e.key == p.K_z:              #undo when "z" pressed
                    gs.undoMove()
                    movemade = True
                elif e.key == p.K_r:            #restart when "r" pressed
                    gs = engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
            else:
                pass

        if movemade:
            validMoves = gs.getValidMoves()
            movemade = False

        drawGameState(screen,gs,validMoves,sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected!=():
        r,c = sqSelected
        if gs.board[r][c][0]==('w' if gs.whiteToMove else 'b'):
            #highlight selected square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE,r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow==r and move.startCol==c:
                    screen.blit(s,(SQ_SIZE*move.endCol,move.endRow*SQ_SIZE))

#draw graphics for each game state
def drawGameState(screen,gs,validMoves,sqSelected):
    drawBoard(screen)
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece!="--":
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

if __name__=="__main__":
    main()
