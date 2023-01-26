import cv2
import numpy as np

# import pytesseract
# import getpass

# user = getpass.getuser()
# pytesseract.pytesseract.tesseract_cmd = f'C:/Users/{user}/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

# preprocess tiles by cropping to the largest contour
def preprocess_tile(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (17, 18))
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # edges = cv2.Canny(gray, 50, 150)
    # contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # crop the image to the largest contour
    # valid_contours = [c for c in contours if cv2.arcLength(c, True) > 50]
    # tile_contour = max(valid_contours, key=cv2.contourArea)
    # x,y,w,h = cv2.boundingRect(tile_contour)
    # tile = gray[y:y+h, x:x+w]
    return image

def find_board_edges(image):
    # normalize and resize image
    image = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
    # find edges
    edges = cv2.Canny(image, 50, 150)

    # find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # find the largest contour
    valid_contours = [c for c in contours if cv2.arcLength(c, True) > 200]
    # if none found, return None
    if len(valid_contours) == 0: return None
    valid_contours = [c for c in valid_contours if cv2.boundingRect(c)[2] > 200 and cv2.boundingRect(c)[3] > 200]
    board_contour = max(valid_contours, key=cv2.contourArea)
    # find the bounding rectangle
    x,y,w,h = cv2.boundingRect(board_contour)
    org = (x*2,y*2)

    # return ROI (region of interest)
    board = image[y:y+h, x:x+w]

    # hsv = cv2.cvtColor(board, cv2.COLOR_BGR2HSV)
    # lower_blue = np.array([100,50,50])
    # upper_blue = np.array([140,255,255])
    # mask = cv2.inRange(hsv, lower_blue, upper_blue)
    # blue_edges = cv2.Canny(board, 50, 150)
    # blue_edges = cv2.bitwise_not(blue_edges)
    # blue_edges = cv2.bitwise_and(blue_edges, mask)

    second = cv2.Canny(board, 50, 150)

    # convert to grayscale
    board = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)

    # save edges
    # cv2.imwrite("edges.png", second)

    # find contours
    contours, _ = cv2.findContours(second, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # find all the squares in the board
    squares = []
    for c in contours:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        # if the contour has 4 vertices, then it is a square
        if len(approx) == 4:
            # make sure the square is not too small
            x,y,w,h = cv2.boundingRect(approx)
            if w > 10 and h > 10:
                squares.append(approx)

    if len(squares) == 0: return None
    first = squares[0]
    last = squares[-1]

    # find the bounding rectangle of the first and last squares
    x1,y1,w1,h1 = cv2.boundingRect(first)
    x2,y2,w2,h2 = cv2.boundingRect(last)

    # find the top-left and bottom-right coordinates of the cropped board
    x_start = min(x1,x2)
    y_start = min(y1,y2)
    x_end = max(x1+w1,x2+w2)
    y_end = max(y1+h1,y2+h2)

    # crop the board
    board = board[y_start:y_end, x_start:x_end]

    # save the board
    cv2.imwrite("board.png", board)

    # get the amount of pixels needed to move the board to the top-left corner
    print(x_start, y_start)

    board_x, board_y, board_w, board_h = cv2.boundingRect(board_contour)
    square_size = board_w // 15
    return (square_size, org[0]+y_start+10, org[1]+x_start)

def find_tile_in_board(tile, board):
    result = cv2.matchTemplate(board, tile, cv2.TM_CCOEFF_NORMED)
    threshold = 0.70
    locations = np.where(result >= threshold)
    found = []
    for point in zip(*locations[::-1]):
        x, y = point
        found.append((x, y))
    if len(found) > 0:
        return found
        
import numpy as np

def predict_board(image, model):
    # Load the image of the board
    board_image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

    # Resize the image to match the size of the board
    board_image = cv2.resize(board_image, (255, 270))

    # Define the size of the window (same as the tile size)
    window_size = (17, 18)
    # Define the step size of the window (2 pixels in x and y)
    step_size = (2, 2)

    # Initialize the 2D array to store the board
    board = np.empty((15, 15), dtype=str)

    # define letter to int mapping
    letter_to_int = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25}

    # Slide the window across the board and classify each tile
    for i in range(0, 15*18, step_size[1]):
        for j in range(0, 15*17, step_size[0]):
            x1 = j
            y1 = i
            x2 = x1 + window_size[0]
            y2 = y1 + window_size[1]
            tile_image = board_image[y1:y2, x1:x2]
            tile_image = cv2.resize(tile_image, (17, 18))
            tile_image = np.expand_dims(tile_image, axis=-1)
            tile_image = np.expand_dims(tile_image, axis=0)
            #resize the image before saving
            tile_image = cv2.resize(tile_image, window_size)
            # save the tile
            cv2.imwrite("tile.png", tile_image)
            # wait for key press
            cv2.waitKey(0)
            # prediction = model.predict(tile_image)
            # letter = letter_to_int.keys()[letter_to_int.values().index(np.argmax(prediction))]
            # board[i//18][j//17] = letter

def move_mouse_to_square(x, y, square_size, x_offset, y_offset):
    # calculate the x and y coordinates of the square on the screen, accounting for the 2px gap
    center_x = (2 * square_size + square_size // 2)
    center_y = (2 * square_size + square_size // 2)
    square_x = (center_x + 2 * 2.9)
    square_y = (center_y + 2 * 2.7)
    square_x *= x/1.4
    square_y *= y/1.4
    # move the mouse to the square
    pyautogui.moveTo(square_x + x_offset + 10, square_y + y_offset)

if __name__ == '__main__':
    # image = cv2.imread('examples/wide_board.png')

    # Load model
    # model = tf.keras.models.load_model('tile_classifier.h5')
    # preprocess tiles
    # for image in os.listdir('tiles'):
    #     tile = preprocess_tile(os.path.join('tiles', image))
    #     cv2.imwrite(os.path.join('tiles', image), tile)

    # see if we can find the tiles in the board
    import pyautogui
    # tiles = find_board_edges(image)
    # take full monitor screenshot
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    # save the screenshot
    cv2.imwrite("screenshot.png", screenshot)
    # get the board coordinates
    board_coords = find_board_edges(screenshot)
    print(board_coords)
    if board_coords is None:
        print("Board not found!")
        exit(1)
    import time
    move_mouse_to_square(2, 13, board_coords[0], board_coords[1], board_coords[2])
    time.sleep(1)
    # board = cv2.imread("board.png")
    # predict_board("board.png", None)
    # for idx, tile in enumerate(tiles):
    #     x,y,w,h = cv2.boundingRect(tile)
    #     # get the tile from the board based on the x,y,w,h
    #     tile = board[y:y+h, x:x+w]
    #     # preprocess the tile
    #     _, thresh = cv2.threshold(tile, 127, 255, cv2.THRESH_BINARY)
        
    #     # use pytesseract to get the letter on the tile
    #     # letter = pytesseract.image_to_string(thresh, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    #     # if letter != '':
    #     #     print("Found letter", letter, "at", idx)

    # import os
    # for image in os.listdir('tiles/a'):
    #     tile = cv2.imread(os.path.join('tiles/a', image))
    #     # save image at location of tile
    #     # tile = board[loc[0][1]:loc[0][1]+tile.shape[0], loc[0][0]:loc[0][0]+tile.shape[1]]

    #     # save the tile
    #     cv2.imwrite("tile.png", tile)
        
    #     # load the tile
    #     image = cv2.imread("tile.png", cv2.IMREAD_GRAYSCALE)
    #     # image needs to be shape=(None, 17, 18, 1)
    #     image = image.reshape((1, 17, 18, 1))
    #     # save the tile
    #     # cv2.imwrite("tile.png", image.reshape((17, 18)))

    #     # predict tile
    #     # image = cv2.resize(tile, (17, 18))
    #     # image = tile.reshape((17, 18, 1))
    #     prediction = model.predict(image)
    #     predicted_label = tf.argmax(prediction)
    #     # # convert hot one encoding to label
    #     # letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    #     # predicted_label = letters[predicted_label]

    #     print("Predicted label:", predicted_label)
