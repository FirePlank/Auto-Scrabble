import itertools, random
in_hand = ['a', 'a', 'c', 'd', 'n', 'f', 'i', 'o']
words = open("words.txt").read().lower().split()

scores = {' ': 0, 'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10}

# board is 15x15 array of letters, empty spaces are represented by a space
def gen_random_board():
    # have more empty spaces than letters
    board = []
    for i in range(15):
        row = []
        for j in range(15):
            if random.random() < 0.7:
                row.append(' ')
            else:
                row.append(random.choice(list(scores.keys())))
        board.append(row)
    return board

class Board:
    def __init__(self, board):
        self.board = board
        self.width = len(board[0])
        self.height = len(board)
        self.letters = set()
        for row in board:
            for letter in row:
                self.letters.add(letter)

    def __str__(self):
        string = ''
        for row in self.board:
            for letter in row:
                string += str(letter) + ' '
            string += '\n'
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

def get_best_word(board, in_hand, words, scores):
    # create a list of all possible words that can be formed with the letters in hand
    possible_words = [word for word in words if set(word).issubset(set(in_hand))]
    # initialize variables to store the best word and its score
    best_word = ""
    best_score = 0
    # loop through all possible words
    for word in possible_words:
        # check if the word can be formed on the board
        if word_on_board(board, word):
            # calculate the score of the word based on letter scores and multipliers on the board
            score = calculate_score(board, word, scores)
            # update the best word and score if the current word has a higher score
            if score > best_score:
                best_word = word
                best_score = score
    return best_word

# helper function to check if a word can be formed on the board
def word_on_board(board, word):
    # loop through all the cells on the board
    for y in range(board.height):
        for x in range(board.width):
            # check if the word can be formed starting from the current cell
            if check_word(board, x, y, word, 0):
                return True
    return False

# helper function to check if a word can be formed starting from a cell on the board
def check_word(board, x, y, word, index):
    # check if the current cell contains the current letter of the word
    if board.get_letter(x, y) == word[index]:
        # check if the word has been formed
        if index == len(word)-1:
            return True
        # word can only go down or right
        # check if the word can be formed by going down
        if y < board.height-1 and check_word(board, x, y+1, word, index+1):
            return True
        # check if the word can be formed by going right
        if x < board.width-1 and check_word(board, x+1, y, word, index+1):
            return True

letter_multipliers = {(0, 3): 2, (0, 11): 3, (1, 5): 3, (1, 9): 3, (2, 6): 2, (2, 8): 2, (3, 0): 2, (3, 7): 2, (3, 14): 2, (5, 1): 3, (5, 5): 3, (5, 9): 3, (5, 13): 3, (6, 2): 2, (6, 6): 2, (6, 8): 2,(6, 12): 2, (7, 3): 2, (7, 11): 2,(8, 2): 2,
                    (8, 6): 2, (8, 8): 2, (8, 12): 2, (9, 1): 3, (9, 5): 3, (9, 9): 3, (9, 13): 3, (10, 0): 3, (11, 1): 2, (11, 14): 2, (12, 6): 2, (12, 8): 2, (13, 5): 3, (13, 9): 3, (14, 3): 3, (14, 11): 2}

word_multipliers = {(0, 0): 3, (0, 7): 3, (0, 14): 3, (1, 1): 2, (1, 13): 2, (2, 2): 2, (2, 12): 2, (3, 3): 2, (3, 11): 2, (4, 4): 2, (4, 10): 2, (7, 0): 3,
                    (7, 14): 3, (10, 4): 2, (10, 10): 2, (11, 3): 2, (11, 11): 2, (12, 2): 2, (12, 12): 2, (13, 1): 2, (13, 13): 2, (14, 0): 3, (14, 7): 3, (14, 14): 3}

# helper function to calculate the score of a word based on letter scores and multipliers on the board
def calculate_score(board, word, scores):
    score = 0
    gotten_multipliers = []
    # loop through all the letters of the word
    for i in range(len(word)):
        # add the score of the letter
        score += scores[word[i]]
        # check for multipliers on the board
        for j in range(board.height):
            for k in range(board.width):
                if board.get_letter(j, k) == word[i]:
                    # check for letter multipliers
                    if (j, k) in letter_multipliers:
                        score *= letter_multipliers[(j, k)]
                    # check for word multipliers
                    if (j, k) in word_multipliers:
                        gotten_multipliers.append(word_multipliers[(j, k)])
    multiplier = sum(gotten_multipliers)
    return score * multiplier

board = Board(gen_random_board())
print(calculate_score(board, 'hello', scores))