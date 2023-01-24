import random, itertools
in_hand = ['a', 'a', 'c', 'd', 'n', 'f', 'i', 'o']
words = open("words.txt").read().lower().split()

scores = {' ': 0, 'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10}

# board is 15x15 array of letters, empty spaces are represented by a space
def gen_random_board(empty_spaces=0.7):
    # have more empty spaces than letters
    board = []
    for i in range(15):
        row = []
        for j in range(15):
            if random.random() < empty_spaces:
                row.append(' ')
            else:
                row.append(random.choice(list(scores.keys())))
        board.append(row)
    return board


class Word:
    def __init__(self, word, score, x, y, right):
        self.word = word
        self.score = score
        self.x = x
        self.y = y
        self.right = right
    
    def __str__(self):
        return f"Word: {self.word}, Score: {self.score}, X: {self.x}, Y: {self.y}, Direction: {'Right' if self.right else 'Down'}"

class Board:
    def __init__(self, board=None):
        self.width = 15
        self.height = 15
        self.letters = set()

        if board is None:
            self.board = []
            for _ in range(self.height):
                row = []
                for _ in range(self.width):
                    row.append(' ')
                self.board.append(row)
        else:
            self.board = board

        # letter and word multipliers are represented by a dictionary of coordinates and the multiplier
        self.letter_multipliers = {(0, 3): 2, (0, 11): 3, (1, 5): 3, (1, 9): 3, (2, 6): 2, (2, 8): 2, (3, 0): 2, (3, 7): 2, (3, 14): 2, (5, 1): 3, (5, 5): 3, (5, 9): 3, (5, 13): 3, (6, 2): 2, (6, 6): 2, (6, 8): 2, (6, 12): 2, (7, 3): 2, (7, 11): 2, (8, 2): 2,
                            (8, 6): 2, (8, 8): 2, (8, 12): 2, (9, 1): 3, (9, 5): 3, (9, 9): 3, (9, 13): 3, (10, 0): 3, (11, 1): 2, (11, 14): 2, (12, 6): 2, (12, 8): 2, (13, 5): 3, (13, 9): 3, (14, 3): 3, (14, 11): 2}
        self.word_multipliers = {(0, 0): 3, (0, 7): 3, (0, 14): 3, (1, 1): 2, (1, 13): 2, (2, 2): 2, (2, 12): 2, (3, 3): 2, (3, 11): 2, (4, 4): 2, (4, 10): 2, (7, 0): 3,
                            (7, 14): 3, (10, 4): 2, (10, 10): 2, (11, 3): 2, (11, 11): 2, (12, 2): 2, (12, 12): 2, (13, 1): 2, (13, 13): 2, (14, 0): 3, (14, 7): 3, (14, 14): 3}

    def __str__(self):
        # print column and row numbers
        string = "   "
        for i in range(self.width):
            string += f"{i} "
        string += "\n"
        for i in range(self.height):
            string += f"{i} {' ' if i < 10 else ''}"
            for j in range(self.width):
                string += f"{self.board[i][j]} {' ' if j >= 10 else ''}"
            string += "\n"
        return string

    def get_letter(self, x, y):
        return self.board[y][x]

    def get_neighbors(self, x, y):
        neighbors = []
        if x > 0:
            neighbors.append((x-1, y))
        if x < self.width-1:
            neighbors.append((x+1, y))
        if y > 0:
            neighbors.append((x, y-1))
        if y < self.height-1:
            neighbors.append((x, y+1))
        return neighbors

    # helper function to calculate the score of a word based on letter scores and multipliers on the board
    def calculate_score(self, word, x=None, y=None, right=True):
        score = 0
        word_multiplier = 0
        for i in range(len(word)):
            if x is not None and y is not None:
                if (x, y) in self.letter_multipliers and self.get_letter(x, y) == ' ':
                    score += scores[word[i]] * self.letter_multipliers[(x, y)]
                else:
                    score += scores[word[i]]
                    if (x, y) in self.word_multipliers and self.get_letter(x, y) == ' ':
                        word_multiplier += self.word_multipliers[(x, y)]
                if right:
                    x += 1
                else:
                    y += 1
            else:
                score += scores[word[i]]
        if word_multiplier > 0:
            score *= word_multiplier
        return score
    
    def generate_possible_words(self, in_hand, words):
        # if board is empty, return all the words that can be formed by the letters in hand
        if self.is_empty():
            return self.generate_hand_words(in_hand, words)

        possible_words = []
        # check all the words that can be formed by the letters on the board and in hand
        for x in range(self.width):
            for y in range(self.height):
                if self.get_letter(x, y) != ' ':
                    for word in words:
                        if self.check_word_validity(word, in_hand) and self.get_letter(x, y) in word:
                            if all(letter in in_hand for letter in word.replace(self.get_letter(x, y), '')):
                                for i in range(len(word)):
                                    if self.get_letter(x, y) == word[i]:
                                        if self.check_right(x, y, i, word):
                                            score = self.calculate_score(word)
                                            # figure out the real coordinates of the word, x and y should be the first letter of the word
                                            letter = self.get_letter(x, y)
                                            offset = word.index(letter)
                                            x -= offset
                                            possible_words.append(Word(word, score, x, y, True))
                                            break
                                        elif self.check_down(x, y, i, word):
                                            score = self.calculate_score(word)
                                            # figure out the real coordinates of the word, x and y should be the first letter of the word
                                            letter = self.get_letter(x, y)
                                            offset = word.index(letter)
                                            y -= offset
                                            possible_words.append(Word(word, score, x, y, False))
                                            break

        # check if the letters in the words are touching any other letters, if so they have to form a word as well
        for word in possible_words:
            break_out = False
            try:
                if word.right:
                    # check out of bounds
                    if word.x + len(word.word) >= self.width:
                        possible_words.remove(word)
                        break
                    for i in range(len(word.word)):
                        if self.get_letter(word.x + i, word.y) != " " and self.get_letter(word.x + i, word.y) != word.word[i]:
                            # square is already occupied, remove the word from the list
                            possible_words.remove(word)
                            break
                        elif self.get_letter(word.x + i, word.y) == word.word[i]:
                            # square is occupied by the same letter, no need to check neighbors
                            continue
                        neighbors = self.get_neighbors(word.x + i, word.y)
                        for neighbor in neighbors:
                            if self.get_letter(neighbor[0], neighbor[1]) != ' ':
                                # TODO: add logic to check validity of connecting words
                                if neighbor[1] == word.y and neighbor[0] >= word.x + i:
                                    if word.word[neighbor[0] - word.x] != self.get_letter(neighbor[0], neighbor[1]):
                                        # square is already occupied, remove the word from the list
                                        possible_words.remove(word)
                                        break_out = True
                                        break
                                    else:
                                        # square is occupied by the same letter, no need to check neighbors
                                        continue

                                # # check that the word is valid
                                # word = self.get_letter(neighbor[0], neighbor[1]) + self.get_letter(word.x + i, word.y)
                                # if word in words:
                                #     score = self.calculate_score(word)
                                #     possible_words.append(Word(word, score, neighbor[0], neighbor[1], True))
                                
                                # for now, remove the word from the list
                                possible_words.remove(word)
                                break_out = True
                                break

                        if break_out: break
                else:
                    # check out of bounds
                    if word.y + len(word.word) >= self.height:
                        possible_words.remove(word)
                        break

                    for i in range(len(word.word)):
                        if self.get_letter(word.x, word.y + i) != " " and self.get_letter(word.x, word.y + i) != word.word[i]:
                            # square is already occupied, remove the word from the list
                            possible_words.remove(word)
                            break
                        elif self.get_letter(word.x, word.y + i) == word.word[i]:
                            # square is occupied by the same letter, no need to check neighbors
                            continue

                        neighbors = self.get_neighbors(word.x, word.y + i)
                        for neighbor in neighbors:
                            if self.get_letter(neighbor[0], neighbor[1]) != ' ':
                                # TODO: add logic to check validity of connecting words
                                if neighbor[0] == word.x and neighbor[1] >= word.y + i:
                                    if word.word[neighbor[1] - word.y] != self.get_letter(neighbor[0], neighbor[1]):
                                        # square is already occupied, remove the word from the list
                                        possible_words.remove(word)
                                        break_out = True
                                        break
                                    else:
                                        # square is occupied by the same letter, no need to check neighbors
                                        continue
                                
                                # for now, remove the word from the list
                                possible_words.remove(word)
                                break_out = True
                                break
                        
                        if break_out: break
            except:
                possible_words.remove(word)
                
        return possible_words

    def check_right(self, x, y, i, word):
        if y + len(word) - i <= self.width:
            for j in range(i, len(word)):
                if self.get_letter(x, y + j - i) != ' ' and self.get_letter(x, y + j - i) != word[j]:
                    return False
            return True
        return False

    def check_down(self, x, y, i, word):
        if x + len(word) - i <= self.height:
            for j in range(i, len(word)):
                if self.get_letter(x + j - i, y) != ' ' and self.get_letter(x + j - i, y) != word[j]:
                    return False
            return True
        return False

    def check_word_validity(self, word, in_hand):
        word_letters = list(word)
        in_hand_letters = list(in_hand)
        for letter in word_letters:
            if letter in in_hand_letters:
                in_hand_letters.remove(letter)
            else:
                return False
        return True
    
    def is_empty(self):
        # check if the board is empty
        for i in range(self.height):
            for j in range(self.width):
                if self.get_letter(i, j) != ' ':
                    return False
        return True

    # used on the first turn to generate all the words that can be formed by the letters in hand
    def generate_hand_words(self, in_hand, words):
        possible_words = []
        # check all the words that can be formed by the letters in hand
        for word in words:
            if self.check_word_validity(word, in_hand) and all(letter in in_hand for letter in word):
                # if word is longer than 5 letters, place it 4 squares to the left of the center
                # so we can get the 2x letter multiplier
                y = self.height // 2
                x = self.width // 2
                if len(word) >= 5:
                    x -= 4
                score = self.calculate_score(word, x, y, True)
                possible_words.append(Word(word, score, x, y, True))
        return possible_words

    def get_best_word(self, in_hand, words):
        possible_words = self.generate_hand_words(in_hand, words)
        best_word = possible_words[0]
        for word in possible_words:
            if word.score > best_word.score:
                best_word = word
        return best_word


# board = Board(gen_random_board(0.9))
board = Board()
print(board)

# best word
best_word = board.get_best_word(in_hand, words)
print("BEST WORD:", best_word)
print("ALL WORDS: ")
words = board.generate_possible_words(in_hand, words)

# first 10
counter = 0
for word in words:
    print(word)
    counter += 1
    if counter == 10: break