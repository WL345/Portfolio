punctuation = [',', '.', '?', '/', '"', "'", ':', ';', ']', '[', '}', '{', '_', '-', '*', '&', '%', '$', '@', '!', '~', '`', '”', '“']
words = {}
most_Words = [["", 0], ["", 0], ["", 0], ["", 0], ["", 0]] # Saving values in a list of lists to overwrite later on

# To check if the word is already in the list
def check_Words():
  for x in most_Words:
    if i in x[0]:
      return
  return True

with open("Text.txt", "r") as file: 
  for word in file.read().split(): # Singles out words
    for char in word: # Singles out characters
      if char in punctuation: # Eliminates punctuation
        word = word.replace(char, "")
    if len(word) > 2 and word in words: # Eliminates words without 3+ letters
      words[word] += 1 # If the word already exists, take the word key and add 1
    elif len(word) > 2:
        words[word] = 1 # If the word is 3+ letters, but is not in words, adds it

  for i in words: # i is each word
    for num in range(5):
      if words[i] > most_Words[num][1] and check_Words():
        most_Words[num][0] = i
        most_Words[num][1] = words[i]

for stuff in most_Words:
  print(f'"{stuff[0]}" appears {stuff[1]} times')
