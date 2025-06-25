import requests
import pygame as py
import sys
import random
import time

py.init()
py.font.init()

Intro = True
Game = False

def get_one():
    length = input("Do you have a requested amount of letters for words? If you input over 9, it will default to 9. ("
                   "Input 0 for no preference): ")
    if int(length) == 0:
        length = random.randint(2, 9)
    if int(length) > 9:
        length = 9
    while True:
        resp = requests.get(f'https://random-word-api.herokuapp.com/word?length={int(length)}')
        word = resp.json()[0]
        return word

def get_phrase():
    dis.blit(NotFinished, (0, 0))
    py.display.update()
    time.sleep(3)

dis = py.display.set_mode((1500, 950))
py.display.set_caption("Hangman")
my_font = py.font.SysFont('arial', 150)  # Increased font size

ONE_WORD = py.Rect(91, 604, 536, 93)
PHRASE1 = py.Rect(882, 675, 511, 93)
PHRASE2 = py.Rect(927, 542, 423, 133)
initial_x = 50
y = 128
guessed_letters = []
num_of_guesses = 0

IntroScreen = py.transform.scale(py.image.load('Resources/Intro Screen.png'), (1500, 950))
Background = py.transform.scale(py.image.load('Resources/Background.png'), (1500, 950))
NotFinished = py.transform.scale(py.image.load('Resources/Not Finished.png'), (1500, 950))
Post = py.transform.scale(py.image.load('Resources/HangPost.png'), (450, 461))

while Intro:
    dis.blit(IntroScreen, (0, 0))
    mousepos = py.mouse.get_pos()
    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            sys.exit()
        if event.type == py.KEYDOWN:
            if event.key == py.K_ESCAPE:
                py.quit()
                sys.exit()
        if event.type == py.MOUSEBUTTONDOWN:
            if ONE_WORD.collidepoint(mousepos):
                text = get_one()
                Intro = False
                Game = True
            if PHRASE1.collidepoint(mousepos) or PHRASE2.collidepoint(mousepos):
                get_phrase()
                Intro = False
                Intro = True
    py.display.update()

letters = {}


while Game:
    dis.blit(Background, (0, 0))
    dis.blit(Post, (100, 200))

    x = initial_x
    for i in text:
        py.draw.line(dis, 'white', (x, y), (x + 100, y), 15)
        if i in letters:
            letters[i].append((x, y + 100))
        else:
            letters[i] = [(x, y + 100)]
        x += 150

    # Handle events
    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            sys.exit()
        if event.type == py.KEYDOWN:
            if event.key == py.K_ESCAPE:
                py.quit()
                sys.exit()
        if event.type == py.MOUSEBUTTONDOWN:
            pass

    # Blit guessed letters
    for letter in guessed_letters:
        if letter in letters:
            rendered_letter = my_font.render(letter, False, "white")
            for i in letters[letter]:
                dis.blit(rendered_letter, (i[0] + 25, i[1] - 250))

    py.display.update()

    # Get guess from user
    guess = input("What is your guess?: ")
    if guess.isalpha() and len(guess) == 1 and guess not in guessed_letters:
        guessed_letters.append(guess)
        num_of_guesses += 1
    elif guess == text:
        print(f"Congrats! You got it in {num_of_guesses} guesses!")
        py.quit()
        sys.exit()
    else:
        print("Not a valid answer")
