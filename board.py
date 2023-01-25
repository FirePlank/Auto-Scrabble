import random
import pickle
import gzip

scores = {'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10}
DELIMITER = "#"

# board is 15x15 array of letters, empty spaces are represented by a space
def gen_random_board(empty_spaces=0.7):
    # have more empty spaces than letters
    board = []
    for i in range(15):
        row = []
        for j in range(15):
            if random.random() < empty_spaces:
                row.append('')
            else:
                row.append(random.choice(list(scores.keys())))
        board.append(row)
    return board
class State:
    """a state in a GADDAG"""

    __slots__ = "arcs", "letter_set"

    def __init__(self):
        self.arcs = dict()
        self.letter_set = set()

    def __iter__(self):
        for char in self.arcs:
            yield self.arcs[char]

    def __contains__(self, char):
        return char in self.arcs

    def get_arc(self, char) -> "Arc":
        return self.arcs[char] if char in self.arcs else None

    def add_arc(self, char: str, destination: "State" = None) -> "State":
        """adds an arc from this node for the given letter
        Args:
            char: the letter for this node
            destination: the state this arc leads to, a new state will be created if this
                is left blank
        Returns:
            the new state that this arc leads to
        """
        if char not in self.arcs:
            self.arcs[char] = Arc(char, destination)
        return self.get_next(char)

    def add_final_arc(self, char: str, final: str) -> "State":
        """adds a final arc from this node for the given letter
        this completes a word by adding the second provided letter into the letter set of the new arc
        Args:
            char: the letter for this arc
            final: the letter which completes the word
        Returns:
            the new state that this arc leads to
        """
        if char not in self.arcs:
            self.arcs[char] = Arc(char)
        self.get_next(char).add_letter(final)
        return self.get_next(char)

    def add_letter(self, char: str):
        self.letter_set.add(char)

    def get_next(self, char: str) -> "State":
        """Gets the node that the given letter leads to"""
        return self.arcs[char].destination if char in self.arcs else None


class Arc:
    """an arc in a GADDAG
    Attributes:
        char: the letter corresponding to this arc
        destination: the node that this arc leads to
    """

    __slots__ = "char", "destination"

    def __init__(self, char: str, destination: "State" = None):
        self.char = char
        if not destination:
            destination = State()
        self.destination = destination

    def __contains__(self, char: str):
        return char in self.destination.letter_set

    def __eq__(self, other: str):
        return other == self.char

    @property
    def letter_set(self):
        return self.destination.letter_set if self.destination else set()

    def get_next(self, char: str):
        return self.destination.arcs[char] if char in self.destination.arcs else None

class Dictionary:
    """The full dictionary implemented as a GADDAG
    Attributes:
        root (State): the root state of the lexicon
    """

    __slots__ = "root"

    def __init__(self, root: "State"):
        self.root = root

    def store(self, filename: str):
        """stores a GADDAG data structure to the designated file"""

        with gzip.open(filename, "wb") as f:
            f.write(pickle.dumps(self.root))

    @classmethod
    def construct_with_text_file(cls, filename: str) -> "Dictionary":
        with open(filename) as f:
            words = f.readlines()
        word_list = set(x.rstrip('\n') for x in words)
        root = cls.__construct_lexicon_with_list_of_words(word_list)
        return cls(root)

    @classmethod
    def load_from_pickle(cls, filename: str) -> "Dictionary":
        root = cls.__load_picked_dictionary_from_file(filename)
        return cls(root)

    @staticmethod
    def __construct_lexicon_with_list_of_words(word_list: set) -> "State":
        """creates a dictionary lexicon with a set of words
        Args:
            word_list: the set of words
        Returns:
            the root state of the lexicon
        """
        root = State()
        for word in word_list:
            word = word.upper()
            Dictionary.__add_word(root, word)
        return root

    @staticmethod
    def __load_picked_dictionary_from_file(filename) -> "State":
        """loads a GADDAG data structure from a file"""

        with gzip.open(filename, "rb") as f:
            return pickle.loads(f.read())

    @staticmethod
    def __add_word(root: "State", word: str):
        """adds a word to the lexicon
        Args:
            root: the root state of the lexicon
            word: the word to be added
        """

        # create path from the last letter to the first letter
        state = root
        for char in word[len(word):1:-1]:  # for i from n down to 3
            state = state.add_arc(char)
        state.add_final_arc(word[1], word[0])

        # create path from second last to last
        state = root
        for char in word[len(word) - 2::-1]:  # for i from n-1 down to 1
            state = state.add_arc(char)
        state = state.add_final_arc(DELIMITER, word[-1])

        # add the remaining paths
        for m in range(len(word) - 2, 0, -1):  # for m from n-2 down to 1
            destination = state
            state = root
            for char in word[m - 1::-1]:  # for i from m down to 1
                state = state.add_arc(char)
            state = state.add_arc(DELIMITER)
            state.add_arc(word[m], destination)  # keep the current state at the second last node

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
    def __init__(self, board=None):
        self.width = 15
        self.height = 15
        self.letters = set()
        self.dictionary = Dictionary.load_from_pickle('dictionary.pickle')

        if board is None:
            self.board = [['' for _ in range(15)] for _ in range(15)]
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
    
    def generate_possible_moves(self, rack):
        """
        Generates all possible moves that can be made using the tiles in the rack on the current board
        :param rack: A list of tiles that can be used to make a move
        :return: A list of possible moves in the form of (x, y, orientation, word)
        """
        possible_moves = []
        for row in range(15):
            for col in range(15):
                for orientation in ['horizontal', 'vertical']:
                    move = self.__check_move(row, col, orientation, rack)
                    if move:
                        possible_moves.append(move)
        return possible_moves

    def __check_move(self, row, col, orientation, rack):
        """
        Helper function to check if a move can be made starting at a certain position on the board with a certain orientation
        :param row: Starting row of the move
        :param col: Starting col of the move
        :param orientation: Orientation of the move (horizontal or vertical)
        :param rack: Tiles that can be used to make the move
        :return: A move in the form of (x, y, orientation, word) if a move can be made, otherwise None
        """
        if orientation == 'horizontal':
            if col > 0 and self.board[row][col-1] != '':
                # check if move is adjacent to existing tiles
                return None
            if col < 14 and self.board[row][col+1] != '':
                # check if move is adjacent to existing tiles
                return None
            # check if move can be made using the tiles in the rack
            word = ''
            for i in range(col, 15):
                if self.board[row][i] != '':
                    word += self.board[row][i]
                else:
                    if len(word) == 0:
                        start_col = i
                    else:
                        if i - start_col > len(rack):
                            # not enough tiles in rack to complete the move
                            return None
                        for j in range(i - start_col):
                            if rack[j] != word[j]:
                                # tile in rack does not match tile on board
                                return None
                        return (row, start_col, orientation, word)
        elif orientation == 'vertical':
            if row > 0 and self.board[row-1][col] != '':
                # check if move is adjacent to existing tiles
                return None
            if row < 14 and self.board[row+1][col] != '':
                # check if move is adjacent to existing tiles
                return None
            # check if move can be made using the tiles in the rack
            word = ''
            for i in range(row, 15):
                if self.board[i][col] != '':
                    word += self.board[i][col]
                else:
                    if len(word) == 0:
                        start_row = i
                    else:
                        if i - start_row > len(rack):
                            # not enough tiles in rack to complete the move
                            return None
                        for j in range(i - start_row):
                            if rack[j] != word[j]:
                                # tile in rack does not match tile on board
                                return None
                        # check if the word is in the dictionary using the GADDAG algorithm
                        if not self.__check_word_in_dictionary(word, row, col, orientation):
                            return None
                        return (start_row, col, orientation, word)

    def __check_word_in_dictionary(self, word, row, col, orientation):
        """
        Helper function to check if a word is in the dictionary using the GADDAG algorithm
        :param word: The word to be checked
        :param row: Starting row of the word
        :param col: Starting col of the word
        :param orientation: Orientation of the word (horizontal or vertical)
        :return: True if the word is in the dictionary, False otherwise
        """
        state = self.dictionary.root
        if orientation == 'horizontal':
            for i in range(col - 1, -1, -1):
                if self.board[row][i] != '':
                    state = state.arcs.get(self.board[row][i])
                    if not state:
                        return False
                else:
                    break
            for char in word:
                state = state.arcs.get(char)
                if not state:
                    return False
            if state.letter_set:
                return True
            return False
        elif orientation == 'vertical':
            for i in range(row - 1, -1, -1):
                if self.board[i][col] != '':
                    state = state.arcs.get(self.board[i][col])
                    if not state:
                        return False
                else:
                    break
            for char in word:
                state = state.arcs.get(char)
                if not state:
                    return False
            if state.letter_set:
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

    def get_best_word(self, in_hand, words):
        possible_words = self.generate_hand_words(in_hand, words)
        if len(possible_words) == 0:
            return None
        best_word = possible_words[0]
        for word in possible_words:
            if word.score > best_word.score:
                best_word = word
        return best_word

    def add_letter(self, letter, index):
        # convert index to x and y coordinates
        # board is 15x15
        x = index // 15
        y = index % 15
        self.board[x][y] = letter


if __name__ == '__main__':
    board = Board()
    print(board.generate_possible_moves(['A', 'D', 'Q', 'A', 'I', 'J', 'T']))
#   board_string = """   0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
# 0
# 1
# 2
# 3
# 4
# 5                a
# 6              n e s t l  e
# 7                r
# 8            b i o
# 9
# 10
# 11
# 12
# 13
# 14"""
#   board = parse_board_from_string(board_string)
#   print(board)
