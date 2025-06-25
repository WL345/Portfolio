import pygame as py, sys, time

py.init()

def win(b):
    if b[0] is not None and b[0] == b[1] and b[0] == b[2]:
        print("Activated")
        if b[0] == "X": color = "blue"
        elif b[0] == "O": color = "black"
        else:
            return
        py.draw.line(dis, color, (101, 200), (900, 196), 25)
        py.display.update()
        time.sleep(3)
        sys.exit()
    elif b[3] is not None and b[3] == b[4] and b[3] == b[5]:
        if b[3] == "X": color = "blue"
        elif b[3] == "O": color = "black"
        else:
            return
        py.draw.line(dis, color, (101, 450), (900, 446), 25)
        py.display.update()
        time.sleep(3)
        sys.exit()
    elif b[6] is not None and b[6] == b[7] and b[6] == b[8]:
        if b[6] == "X": color = "blue"
        elif b[6] == "O": color = "black"
        else:
            return
        py.draw.line(dis, color, (101, 700), (900, 696), 25)
        py.display.update()
        time.sleep(3)
        sys.exit()
    elif b[0] is not None and b[0] == b[3] and b[0] == b[6]:
        if b[0] == "X": color = "blue"
        elif b[0] == "O": color = "black"
        else:
            return
        py.draw.line(dis, color, (210, 95), (210, 800), 25)
        py.display.update()
        time.sleep(3)
        sys.exit()
    elif b[1] is not None and b[1] == b[4] and b[1] == b[7]:
        if b[1] == "X": color = "blue"
        elif b[1] == "O": color = "black"
        else:
            return
        py.draw.line(dis, color, (500, 95), (500, 800), 25)
        py.display.update()
        time.sleep(3)
        sys.exit()
    elif b[2] is not None and b[2] == b[5] and b[2] == b[8]:
        if b[2] == "X": color = "blue"
        elif b[2] == "O": color = "black"
        else:
            return
        py.draw.line(dis, color, (780, 95), (780, 800), 25)
        py.display.update()
        time.sleep(3)
        sys.exit()
    elif b[0] is not None and b[0] == b[4] and b[0] == b[8]:
        if b[0] == "X": color = "blue"
        elif b[0] == "O": color = "black"
        else:
            return
        py.draw.line(dis, color, (100, 95), (890, 800), 25)
        py.display.update()
        time.sleep(3)
        sys.exit()
    elif b[2] is not None and b[2] == b[4] and b[2] == b[6]:
        if b[2] == "X": color = "blue"
        elif b[2] == "O": color = "black"
        else:
            return
        py.draw.line(dis, color, (850, 95), (100, 800), 25)
        py.display.update()
        time.sleep(3)
        sys.exit()


O = False
X = True

TTTboard = py.transform.scale(py.image.load('Resources/TTT Board.png'), (800, 700))
Ximg = py.transform.scale(py.image.load('Resources/X.png'), (225, 200))
Oimg = py.transform.scale(py.image.load('Resources/O.png'), (225, 200))

dis = py.display.set_mode((1000, 900))
py.display.set_caption("Tic Tac Toe")

Sec1 = py.Rect(101, 95, 251, 220)
Sec2 = py.Rect(385, 95, 233, 220)
Sec3 = py.Rect(652, 95, 251, 220)
Sec4 = py.Rect(101, 343, 251, 210)
Sec5 = py.Rect(385, 343, 233, 206)
Sec6 = py.Rect(652, 343, 251, 210)
Sec7 = py.Rect(101, 578, 251, 220)
Sec8 = py.Rect(385, 578, 233, 220)
Sec9 = py.Rect(652, 578, 251, 210)

# Create a board state to track Xs and Os
board = [None] * 9  # None means empty, 'X' means X, 'O' means O

while True:
    mousepos = py.mouse.get_pos()
    dis.fill((255, 255, 255))
    dis.blit(TTTboard, (100, 95))

    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            sys.exit()
        if event.type == py.KEYDOWN:
            if event.key == py.K_ESCAPE:
                py.quit()
                sys.exit()
        if event.type == py.MOUSEBUTTONDOWN:
            for i, sec in enumerate([Sec1, Sec2, Sec3, Sec4, Sec5, Sec6, Sec7, Sec8, Sec9]):
                if sec.collidepoint(mousepos) and board[i] is None:
                    if X:
                        board[i] = 'X'
                        X = False
                        O = True
                    elif O:
                        board[i] = 'O'
                        O = False
                        X = True

    # Blit Xs and Os according to the board state
    positions = [(101, 95), (385, 95), (652, 95), (101, 343), (385, 343), (652, 343), (101, 578), (385, 578), (652, 578)]
    for i, state in enumerate(board):
        if state == 'X':
            dis.blit(Ximg, positions[i])
        elif state == 'O':
            dis.blit(Oimg, positions[i])

    win(board)

    py.display.update()
