# from board import Board
from scrabbler import scrabbler as sc
import detect

import json
from mitmproxy import http
import pyautogui

def move_mouse_to_square(x, y, board_x, board_y, square_size):
    # calculate the x and y coordinates of the square on the screen, accounting for the 2px gap
    square_x = board_x + x * square_size + 2 * x
    square_y = board_y + y * square_size + 2 * y
    # move the mouse to the square
    pyautogui.moveTo(square_x, square_y)

# create a new board
board = sc.Game()

print("Starting proxy, ready to play!")

class MyProxy:
    def request(self, _: http.HTTPFlow):
        pass

    def response(self, flow: http.HTTPFlow):
        try:
            if 'cloudfront.net' in flow.response.headers.get('via') and 'application/json' in flow.response.headers.get('content-type'):
                # get the json data
                json_data = json.loads(flow.response.content)['Data']
                # print(json_data)
                try:
                    # clear board
                    board.board.clear()
                    for entry in json_data['Data'][0]['Actions']:
                        if "Tiles" in entry:
                            # a very convoluted and inefficient way to get the blank tile letters because for some reason the Flags is very random for blank tiles
                            blank_tiles = []
                            for i in entry['Tiles']:
                                if i['Flags'] > 30: blank_tiles.append((i['BoardIndex'], '-'))
                            for i in entry['WordsPlayed']:
                                # get blank tile letters
                                for idx, j in enumerate(i['Tiles']):
                                    for idx, k in enumerate(blank_tiles):
                                        if k[0] == j['BoardIndex']:
                                            blank_tiles[idx] = (k[0], i['Word'][idx])
                                            break
                            for tile in entry["Tiles"]:
                                # convert int to letter
                                letter = ''
                                if tile['Flags'] > 30:
                                    for i in blank_tiles:
                                        if i[0] == tile['BoardIndex']:
                                            letter = i[1]
                                            break
                                else: letter = chr((tile['Flags'])+96)
                                board_index = tile['BoardIndex']
                                # convert board index to x, y
                                x = board_index % 15
                                y = board_index // 15

                                # add the letter to the board
                                board.play((y, x), letter, 'across')

                    # get our rack
                    user_id = json_data['CurrentPlayer']['UserId']
                    rack = []
                    other_rack = []
                    for player in json_data['Data'][0]['Players']:
                        if player['UserId'] == user_id:
                            rack = player['Rack']
                            break
                        else:
                            # funny thing is that the playscrabble.com API actually returns the opponent's rack in the response once it becomes their turn
                            try: other_rack = player['Rack']
                            except: pass

                    # print the board
                    board.show()

                    # print racks
                    if other_rack:
                        print("Your rack:", other_rack)
                        print("Opponent rack:", rack)
                        # get the best word for opponent because why not
                        # best_word = board.find_best_moves(''.join(rack).upper())[0]
                        # print("Best word for the opponent:", best_word)
                    else:
                        print("Your rack:", rack)
                        # get the best word
                        best_word = board.find_best_moves(''.join(rack).upper())[0]
                        print("Best word:", best_word)

                        # take full monitor screenshot
                        screenshot = pyautogui.screenshot()
                        # get the board coordinates
                        board_coords = detect.find_board_edges(screenshot)
                        move_mouse_to_square(5, 3, board_coords[0], board_coords[1], board_coords[2])
                except Exception as e:
                    print(e)
        except:
            pass

addons = [
    MyProxy()
]