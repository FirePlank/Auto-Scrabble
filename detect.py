from main import Board
import cv2
import tensorflow as tf
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
    valid_contours = [c for c in contours if cv2.arcLength(c, True) > 50]
    board_contour = max(valid_contours, key=cv2.contourArea)
    # find the bounding rectangle
    x,y,w,h = cv2.boundingRect(board_contour)
    # print("x,y,w,h:",x,y,w,h)

    # return ROI (region of interest)
    board = image[y:y+h, x:x+w]

    # hsv = cv2.cvtColor(board, cv2.COLOR_BGR2HSV)
    # lower_blue = np.array([100,50,50])
    # upper_blue = np.array([140,255,255])
    # mask = cv2.inRange(hsv, lower_blue, upper_blue)
    # blue_edges = cv2.Canny(board, 50, 150)
    # blue_edges = cv2.bitwise_not(blue_edges)
    # blue_edges = cv2.bitwise_and(blue_edges, mask)

    # remove blue edges
    second = cv2.Canny(board, 50, 150)

    # second = cv2.bitwise_and(second, cv2.bitwise_not(mask))

    # convert board to grayscale
    board = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)

    # save edges
    cv2.imwrite("edges.png", second)

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
            
    # save the first square as image
    x,y,w,h = cv2.boundingRect(squares[94])

    # save the board
    cv2.imwrite("board.png", board)

    return squares

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
        

if __name__ == '__main__':
    image = cv2.imread('examples/wide_board.png')

    # Load model
    model = tf.keras.models.load_model('tile_classifier.h5')
    # preprocess tiles
    # for image in os.listdir('tiles'):
    #     tile = preprocess_tile(os.path.join('tiles', image))
    #     cv2.imwrite(os.path.join('tiles', image), tile)

    # see if we can find the tiles in the board
    tiles = find_board_edges(image)
    board = cv2.imread("board.png")
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

    import os
    for image in os.listdir('tiles/a'):
        tile = cv2.imread(os.path.join('tiles/a', image))
        # save image at location of tile
        # tile = board[loc[0][1]:loc[0][1]+tile.shape[0], loc[0][0]:loc[0][0]+tile.shape[1]]

        # save the tile
        cv2.imwrite("tile.png", tile)
        
        # load the tile
        image = cv2.imread("tile.png", cv2.IMREAD_GRAYSCALE)
        # image needs to be shape=(None, 17, 18, 1)
        image = image.reshape((1, 17, 18, 1))
        # save the tile
        # cv2.imwrite("tile.png", image.reshape((17, 18)))

        # predict tile
        # image = cv2.resize(tile, (17, 18))
        # image = tile.reshape((17, 18, 1))
        prediction = model.predict(image)
        predicted_label = tf.argmax(prediction)
        # # convert hot one encoding to label
        # letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        # predicted_label = letters[predicted_label]

        print("Predicted label:", predicted_label)
    