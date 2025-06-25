
                  ##########################################################################################################
################   This was originally made in REPLIT, so there are some functions (db) that won't work if run other places   ################
###----------------------------------------------------------------------------------------------------------------------------------------###
################  I also created this before I knew about APIs or separate files, so there were two very long lists of words  ################
                  ##########################################################################################################


import random
import sys
from replit import db

global keys
keys = db.keys()

attempts = 1
max_attempts = 7

successful_tries = 0
failed_attempts = 0
# All words that can be picked
words = ["list of many many words"]

# All words the user can guess
allowed = ["another list of so many words"]

# Picks the random word
def select():
  global word, og_word
  og_word = random.choice(words)
  word = [*og_word.upper().lstrip().rstrip()]

#color functions
def prRed(skk): print("\033[31m {}\033[00m" .format(skk),end="")
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk),end="")
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk),end="")

#checks guess and prints result
def wordle():

  global word, attempts, query, games
  enum_word=enumerate(word)
  games+=1
  if attempts==1:
    query = input("Welcome to Wordle! What is your first guess? ")
    
  else:
    query = input("What is your next guess? ")

  if query.lower() == og_word:
    check_correct()
  elif query.lower() in allowed or query.lower() in words:
    global test
    test=[*query.upper().lstrip().rstrip()]
    enum_test=enumerate(test)

    for count, ele in enumerate(test):
      nxt_t=next(enum_test)
      nxt_w=next(enum_word)
      
      if nxt_t==nxt_w:
        prGreen(ele)
      else:
        if ele in set(word):
          prYellow(ele)
        else:
          prRed(ele)
    
    attempts += 1
    print()
    if attempts < 7:
      print()
      print(f"You have {max_attempts - attempts}/6 attempts left")
      wordle()
    elif attempts == 7:
      print()
      print("You ran out of attempts")
      print(f"The word was {og_word}")
  else:
    print("Not a valid word")
    print()
    wordle()
    print("\n")
#Game loop
def check_correct():
  if query.lower() == og_word:
    print()
    print("Thats the word!")
    print(f"you got it in {attempts} attempts")
  else:
    wordle()
    check_correct()

def scores():
  global user, time, num
  time = input("Is this your first time playing (y/n)? ")
  if time.lower() == "y":
    num = "10"
    signup()
  elif time.lower() == "n":
    num = "10"
    user = input("What is your username? ")
    if user in keys:
      print("User found! Logged in")
      print()
    else:
      print("User not found, Restarting...")
      print()
      scores()  
  else: 
    print("y or n was not inputted, restarting...")
    print()
    scores()
def signup():
  global user
  user = input("What would you like your username to be? ")
  if user in keys:
    print("Username taken. Please try again")
    signup()
  elif user not in keys:
    print("Great!")
    print()

global games
games=0
scores()
play = "y"
# Main Functions
while play.lower() == "y":
  attempts = 1
  select()
  wordle()
  if time.lower() == "n":
    db[user] = (db[user] + attempts)/2
  elif time.lower() == "y":
    db[user] = attempts
  play = input("Do you want to play again? (y/n): ")
  if play.lower() == "y":
    time = "n"
while play.lower() == "n":
  if time.lower() == "y":
    print("Ok, Thanks for playing!")
    sys.exit()
  elif time.lower() == "n":
    print(f"Your average score is {db[user]}")
    print("Thanks for playing!")
    sys.exit()
    
if __name__ == "__main__":
  sys.exit()
