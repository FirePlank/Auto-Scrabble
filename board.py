# This file shows my attempt at trying to generate all possible words on a board.
# At this time it doesn't work and I have switched to using the scrabbler library instead.

import random

scores = {'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10}

# used to mark the end of a word in the DAWG
DELIMITER = "#"

# board is 15x15 array of letters, empty spaces are represented by a space
def gen_random_board(empty_spaces=0.7):
    # have more empty spaces than letters
    board = []
    for _ in range(15):
        row = []
        for _ in range(15):
            if random.random() < empty_spaces:
                row.append('')
            else:
                row.append(random.choice(list(scores.keys())))
        board.append(row)
    return board


class DAWG:
    """
    DAWG (Directed Acyclic Word Graph) implementation
    """

    def __init__(self, file_name=None):
        self.root = {}
        if file_name:
            self.load_words(file_name)
        
    def load_words(self, file_name):
        # open the file and read in all the words
        with open(file_name, 'r') as f:
            words = f.read().split()

        # add each word to the DAWG
        for word in words:
            self.add(word)
        
    def add_all(self, words):
        for word in words:
            self.add(word)
    
    def add(self, word):
        current = self.root
        for letter in word:
            if letter not in current:
                current[letter] = {}
            current = current[letter]
        current[DELIMITER] = True # mark the end of a word

    def __len__(self):
        # count the number of words in the DAWG
        return self.__count_words(self.root)
    
    def __count_words(self, node):
        count = 0
        for letter in node:
            if letter == DELIMITER:
                count += 1
            else:
                count += self.__count_words(node[letter])
        return count

    def __iter__(self):
        # iterate over all the words in the DAWG
        return self.__iter_words(self.root, '')
    
    def __iter_words(self, node, word):
        for letter in node:
            if letter == DELIMITER:
                yield word
            else:
                yield from self.__iter_words(node[letter], word + letter)
    
    def count_nodes(self):
        # count the number of nodes in the DAWG
        return self.__count_nodes(self.root)
    
    def __count_nodes(self, node):
        count = 1
        for letter in node:
            if letter != DELIMITER:
                count += self.__count_nodes(node[letter])
        return count

    def search(self, word):
        word = word.upper()
        current = self.root
        for letter in word:
            if letter not in current:
                return False # the word is not in the DAWG
            current = current[letter]
        return DELIMITER in current # check if the end of the word is marked

    # write a function that searches for all words that start with a given prefix and returns them in a list
    def search_prefix(self, prefix):
        prefix = prefix.upper()
        current = self.root
        for letter in prefix:
            if letter not in current:
                return []
            current = current[letter]
        return self.__iter_words(current, prefix)

    def has_prefix(self, prefix):
        prefix = prefix.upper()
        current = self.root
        for letter in prefix:
            if letter not in current:
                return False
            current = current[letter]
        return True
    
    def __contains__(self, word):
        return self.search(word)
    
    def __str__(self):
        return str(self.root)

class Word:
    def __init__(self, word, score, x, y, right):
        self.word = word
        self.score = score
        self.x = x
        self.y = y
        self.right = right
    
    def __str__(self):
        return f"{self.word}, Score: {self.score}, X: {self.x}, Y: {self.y}, Direction: {'Right' if self.right else 'Down'}"

class Board:
    def __init__(self, board=None, dictionary=None):
        self.width = 15
        self.height = 15
        self.letters = set()

        if dictionary:
            self.dictionary = dictionary
        else:
            self.dictionary = DAWG('words.txt')

        if board is None:
            self.board = [['' for _ in range(15)] for _ in range(15)]
        else:
            self.board = board

        # letter and word multipliers are represented by a dictionary of coordinates and the multiplier
        self.letter_multipliers = {(0, 3): 2, (0, 11): 3, (1, 5): 3, (1, 9): 3, (2, 6): 2, (2, 8): 2, (3, 0): 2, (3, 7): 2, (3, 14): 2, (5, 1): 3, (5, 5): 3, (5, 9): 3, (5, 13): 3, (6, 2): 2, (6, 6): 2, (6, 8): 2, (6, 12): 2, (7, 3): 2, (7, 11): 2, (8, 2): 2,
                            (8, 6): 2, (8, 8): 2, (8, 12): 2, (9, 1): 3, (9, 5): 3, (9, 9): 3, (9, 13): 3, (10, 0): 3, (11, 1): 2, (11, 14): 2, (12, 6): 2, (12, 8): 2, (13, 5): 3, (13, 9): 3, (14, 3): 3, (14, 11): 2}
        self.word_multipliers = {(0, 0): 3, (0, 7): 3, (0, 14): 3, (1, 1): 2, (1, 13): 2, (2, 2): 2, (2, 12): 2, (3, 3): 2, (3, 11): 2, (4, 4): 2, (4, 10): 2, (7, 0): 3,
                            (7, 14): 3, (10, 4): 2, (10, 10): 2, (11, 3): 2, (11, 11): 2, (12, 2): 2, (12, 12): 2, (13, 1): 2, (13, 13): 2, (14, 0): 3, (14, 7): 3, (14, 14): 3}

        # This is a list that contains all the letters that are allowed to be placed on a given square.
        self.cross_check_sets = [[set(scores.keys()) for _ in range(15)] for _ in range(15)]
        self.generate_cross_check_sets()

    def __str__(self):
        # print column and row numbers
        string = "   "
        for i in range(self.width):
            string += f"{i} "
        string += "\n"
        for i in range(self.height):
            string += f"{i} {' ' if i < 10 else ''}"
            for j in range(self.width):
                to_add = self.board[i][j]
                if to_add == '':
                    to_add = '.'
                string += f"{to_add} {' ' if j >= 10 else ''}"
            string += "\n"
        return string

    def generate_cross_check_sets(self):
        # update the cross-check sets for every tile directly above and below placed word.
        for r in range(15):
            for c in range(15):
                if self.board[r][c] == '':
                    continue
                # exclude letters that do not form a valid vertical two-letter word when played horizontally
                if c > 0 and self.board[r][c-1] != '':
                    self.cross_check_sets[r][c].discard(self.board[r][c-1])
                if c < 14 and self.board[r][c+1] != '':
                    self.cross_check_sets[r][c].discard(self.board[r][c+1])
                # empty cross-check sets at the squares immediately preceding and ending a word
                if c > 0 and self.board[r][c-1] == '':
                    self.cross_check_sets[r][c-1] = set()
                if c < 14 and self.board[r][c+1] == '':
                    self.cross_check_sets[r][c+1] = set()

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

    

    def generate_possible_moves(self, rack, anchor_x, anchor_y):
        """
        Generates all possible moves that can be made using the tiles in the rack on the current board
        :param rack: A list of tiles that can be used to make a move
        :return: A list of possible moves in the form of Word objects
        """
        if self.is_empty(): 
            return self.generate_hand_moves(rack)

        # TODO: Implement this function
        
    # used on the first turn to generate all the words that can be formed by the letters in hand
    def generate_hand_moves(self, in_hand):
        possible_words = []
        # check all the words that can be formed by the letters in hand
        for word in self.dictionary:
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

    def check_word_validity(self, word, in_hand):
        word_letters = list(word)
        print(word_letters)
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
                if self.get_letter(i, j) != '':
                    return False
        return True

    def get_best_word(self, rack):
        # get all possible words
        possible_words = self.generate_possible_moves(rack)
        # sort the words by score
        possible_words.sort(key=lambda x: x.score, reverse=True)
        # return the word with the highest score
        return possible_words[0]

    def add_letter(self, letter, index):
        # convert index to x and y coordinates
        # board is 15x15
        x = index // 15
        y = index % 15
        self.board[x][y] = letter


if __name__ == '__main__':
    pass

    # # initialize DAWG
    # dictionary = DAWG('words.txt')
    # # initialize board
    # board = Board(dictionary=dictionary)

    # # set letter a at middle of board
    # board.add_letter('A', 112)
    # board.add_letter('A', 113)

    # print(board)
    # print(board.generate_possible_moves(['H', 'D', 'D', 'A', 'I', 'J', 'T']))

    # move.word, move.score, move.start_square, move.direction
    from scrabbler import scrabbler as sc
    game = sc.Game()
    game.play((7, 7), 'ave', 'down')
    for word in game.find_best_moves('HHHHH_H'):
        print(word.word, word.score)