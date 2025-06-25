import sys

board = [
  ["-", "-", "-"],
  ["-", "-", "-"],
  ["-", "-", "-"]
]

numbers = [1, 2, 3]

player = 0

def place(row, column, choice):
    board[row][column] = choice
    print(f"Successfully placed {choice} at ({row + 1}, {column + 1})\n")

def check_spot(row, column):
    if board[row][column] != "-":
        print("That spot is taken!\n")
        return False
    return True

def display_board():
    print("The current board is:\n")
    for row in board:
        print(*row)
    print()

def congrats(player, board):
  if player % 2 == 0:
    print("Congrats player one! You won!")
    print("The final board looked like this:\n")
    for row in board:
      print(*row)
    sys.exit()
  else:
    print("Congrats player two! You won!")
    print("The final board looked like this:\n")
    for row in board:
      print(*row)
    sys.exit()

def check_winner(board, player):
  x = 0
  a = 0
  diagonal = 0
  check = ""

  
  for row in board:
    check = check + board[diagonal][diagonal]
    diagonal += 1
  if str(check) == "x" * len(board) or check == "o"*len(board):
    congrats(player, board)


  # Inspired from Lila's code
  result = ""
  row_index = 0
  col_index = 0

  for line in board:
      for item in line:
          result += board[row_index][col_index]
          row_index += 1

      if result == "x" * len(board) or result == "o" * len(board):
          congrats(player, board)

      row_index = 0
      result = ""


  # Tie
  for row in board:
    for i in range(len(row)):
      if row[i] != "-":
        a += 1
  if a == 9:
    print("It ended in a tie!")
    sys.exit()

ready = input("Are you ready to play?: ")
if ready.lower() != "yes":
    print("You did not input yes. Goodbye!")
    sys.exit()

play = True

while play:
    if player % 2 == 0:
        print("It is player one's turn!")
        choice = "x"
    else:
        print("It is player two's turn!")
        choice = "o"

    display_board()


    row = input(f"What row would you like to place {choice} in? (1-3): ")
    column = input(f"What column would you like to place {choice} in? (1-3): ")

    if row.isdigit() and column.isdigit():
        row = int(row) - 1
        column = int(column) - 1


        if 0 <= row < 3 and 0 <= column < 3:
            if check_spot(row, column):
                place(row, column, choice)
                check_winner(board, player)
                player += 1
        else:
            print("Row or column is out of range. Please choose numbers between 1 and 3.")
    else:
        print("You did not input a valid number for either the row or column.")
