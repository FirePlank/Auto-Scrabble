from board import Board

in_hand = ['a', 'a', 'c', 'd', 'n', 'f', 'i', 'o']
words = open("words.txt").read().lower().split()


import json
from mitmproxy import http

class MyProxy:
    def request(self, _: http.HTTPFlow):
        pass

    def response(self, flow: http.HTTPFlow):
        try:
            if 'cloudfront.net' in flow.response.headers.get('via') and 'application/json' in flow.response.headers.get('content-type'):
                # get the json data
                json_data = json.loads(flow.response.content)['Data']
                # create new board
                board = Board()
                for entry in json_data['Data'][0]['Actions']:
                    if "Tiles" in entry:
                        for tile in entry["Tiles"]:
                            # convert int to letter
                            letter = chr(tile['Flags']+96)
                            board_index = tile['BoardIndex']
                            # add the letter to the board
                            board.add_letter(letter, board_index)
                # get our rack
                user_id = json_data['CurrentPlayer']['UserId']
                rack = []
                other_rack = []
                for player in json_data['Data'][0]['Players']:
                    if player['UserId'] == user_id:
                        rack = player['Rack']
                        break
                    else:
                        try: other_rack = player['Rack']
                        except: pass

                # print the board
                print(board)

                # print racks
                if other_rack:
                    print("Your rack:", other_rack)
                    print("Opponent rack:", rack)
                    # get the best word for opponent because why not
                    best_word = board.get_best_word(other_rack, words)
                    print("Best word for the opponent:", best_word)
                else:
                    print("Your rack:", rack)
                    # get the best word
                    best_word = board.get_best_word(rack, words)
                    print("Best word:", best_word)

        except:
            pass

addons = [
    MyProxy()
]


# if __name__ == "__main__":

#     board = Board(gen_random_board(0.9))
#     # board = Board()
#     print(board)

#     # best word
#     best_word = board.get_best_word(in_hand, words)
#     print("BEST WORD:", best_word)
#     print("ALL WORDS: ")
#     words = board.generate_possible_words(in_hand, words)

#     # first 10
#     counter = 0
#     for word in words:
#         print(word)
#         counter += 1
#         if counter == 10: break