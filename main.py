# from board import Board
from scrabbler import scrabbler as sc
import detect

import json
from mitmproxy import http
import pyautogui
import numpy as np
import asyncio

# create a new board
board = sc.Game()
# define x and y offsets and square size
x_offsets = None
y_offsets = None
square_sizes = None

async def type(word, delay, position):
    # get currently focused window
    window = pyautogui.getActiveWindow()
    # wait a bit
    await asyncio.sleep(delay)
    # if the word is down, double click, otherwise just click
    if word.direction == 'down': pyautogui.doubleClick()
    else: pyautogui.click()
    # sleep for a bit
    await asyncio.sleep(0.1)
    # type the word
    pyautogui.typewrite(word.word.lower(), 0.15)
    # press enter
    pyautogui.press('enter')
    # change focus back to original window
    window.activate()
    # move mouse back to original position
    pyautogui.moveTo(position[0], position[1])

def move_mouse_to_square(x, y, square_size, x_offset, y_offset):
    # calculate the x and y coordinates of the square on the screen, accounting for the 2px gap
    center_x = (2 * square_size + square_size // 2)
    center_y = (2 * square_size + square_size // 2)
    square_x = (center_x + 2 * 2.3)
    square_y = (center_y + 2 * 2.3)
    square_x *= x/1.45
    square_y *= y/1.45
    if x < 3: square_x /= 1.5
    if y < 3: square_y /= 1.5
    if x == 3: square_x /= 1.3
    if y == 3: square_y /= 1.3
    # move the mouse to the square
    pyautogui.moveTo(square_x + x_offset, square_y + y_offset)

print("Starting proxy, ready to play!")

class MyProxy:
    def request(self, _: http.HTTPFlow):
        pass

    async def response(self, flow: http.HTTPFlow):
        global x_offsets, y_offsets, square_sizes
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
                        screenshot = np.array(screenshot)
                        # get the board coordinates
                        board_coords = None
                        if x_offsets is None:
                            board_coords = detect.find_board_edges(screenshot)
                            x_offsets = board_coords[1]
                            y_offsets = board_coords[2]
                            square_sizes = board_coords[0]
                        else:
                            board_coords = (square_sizes, x_offsets, y_offsets)

                        square = best_word.start_square
                        start_square = best_word.start_square
                        got = False
                        word = ''
                        for i in range(len(best_word.word)):
                            # check if square is empty
                            lett = board.board.get_letter(square[0], square[1])
                            print(lett, best_word.word[i], square)
                            if lett is None:
                                if got == False:
                                    start_square = square
                                    got = True
                                word += best_word.word[i]

                            if best_word.direction == 'down':
                                square = (square[0]+1, square[1])
                            else:
                                square = (square[0], square[1]+1)
                        
                        best_word.word = word

                        # get current mouse position
                        position = pyautogui.position()
                        move_mouse_to_square(start_square[1]+1, start_square[0]+1, board_coords[0], board_coords[1]+10, board_coords[2]+10)
                        # type word without blocking this function, return but still continue the rest of the code
                        asyncio.create_task(type(best_word, 3, position))
                except Exception as e:
                    print(e)
        except:
            pass

addons = [
    MyProxy()
]