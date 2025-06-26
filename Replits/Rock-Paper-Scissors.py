import random
import sys


play = input("Would you like to play Rock Paper Scissors? (y/n) (don't accidentally hit the space bar or anything): ")

if play.lower() == "y":
  print("Great!")
  choice = input("What do you choose? (pick ONLY rock, paper, or scissors!): ")
elif play.lower() == "n":
  print("Ok fine")
  sys.exit()  
else:
  print("IDK what you said, so you will play anyway")
  choice = input("What do you choose? (pick ONLY rock, paper, or scissors! OR ELSE!): ")

choices = ["rock", "paper", "scissors"]
bot = random.choice(choices)

win = 0
games = 0
gamesamt = 0

while play.lower() == "y":
  bot = random.choice(choices)
  print()
  if choice.lower() == "rock" and bot == "paper":
    games += 1
    gamesamt +=1 
    print("The computer chose paper... You lost")
    print("Current amount of games played is", gamesamt)
  elif choice.lower() == "paper" and bot == "scissors":
    games += 1
    gamesamt +=1 
    print("The bot choses scissors... You lost")
    print("Current amount of games played is", gamesamt)
  elif choice.lower() == "scissors" and bot == "rock":
    games += 1
    gamesamt +=1 
    print("The bot chose rock... You lost")
    print("Current amount of games played is", gamesamt)
  elif choice.lower() == "rock" and bot == "scissors":
    games += 1
    win += 1
    gamesamt +=1 
    print("The computer chose scissors! You won!")
    print("Current amount of games played is", gamesamt)
  elif choice.lower() == "paper" and bot == "rock":
    games += 1
    win +=1 
    gamesamt +=1 
    print("The bot choses rock! You won!")
    print("Current amount of games played is", gamesamt)
  elif choice.lower() == "scissors" and bot == "paper":
    games += 1
    win += 1
    gamesamt +=1 
    print("The bot chose Paper! You won!")
    print("Current amount of games played is", gamesamt)
  elif choice.lower() == "rock" and bot == "rock":
    gamesamt +=1 
    print("Its a tie! You both chose rock!")
    print("Current amount of games played is", gamesamt)
  elif choice.lower() == "paper" and bot == "paper": 
    gamesamt +=1 
    print("Its a tie! You both chose paper!")
    print("Current amount of games played is", gamesamt)
  elif choice.lower() == "scissors" and bot == "scissors": 
    gamesamt +=1 
    print("Its a tie! You both chose scissors!")
    print("Current amount of games played is", gamesamt)
  else:
    print("You didn't pick rock, paper, or scissors. The game will now end.")
    sys.exit()

  print()
  play = input("Do you want to play again? (y/n): ")
  
  if play.lower() == "n":
    break
  elif play.lower() == "y":
    choice = input("What do you choose? (rock, paper, scissors): ")
  else:
    print("You didn't input y or n. The game will now end. Hope you had fun!")
    break

print()
print(f"Your win percentage was {((win / games) * 100):.1f}% (not includng tied games), you played {gamesamt} games, and the current average of everyone who has played is 56.6%")
print("Thanks for playing!")
