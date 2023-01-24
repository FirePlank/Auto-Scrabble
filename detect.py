from main import Board
import cv2
import os

# preprocess tiles by cropping to the largest contour
def preprocess_tile(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # crop the image to the largest contour
    valid_contours = [c for c in contours if cv2.arcLength(c, True) > 50]
    tile_contour = max(valid_contours, key=cv2.contourArea)
    x,y,w,h = cv2.boundingRect(tile_contour)
    tile = gray[y:y+h, x:x+w]
    return tile

def find_board_edges(image):
    # normalize and resize image
    image = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
    # convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # find edges
    edges = cv2.Canny(gray, 50, 150)
    # find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # find the largest contour
    valid_contours = [c for c in contours if cv2.arcLength(c, True) > 50]
    board_contour = max(valid_contours, key=cv2.contourArea)
    # find the bounding rectangle
    x,y,w,h = cv2.boundingRect(board_contour)
    # print("x,y,w,h:",x,y,w,h)

    # save image
    # cv2.imwrite('edges.png', edges)

    # return ROI (region of interest)
    board = gray[y:y+h, x:x+w]
    return board

if __name__ == '__main__':
    image = cv2.imread('examples/wide_board.png')
    find_board_edges(image)

    # preprocess tiles
    for image in os.listdir('tiles'):
        tile = preprocess_tile(os.path.join('tiles', image))
        cv2.imwrite(os.path.join('tiles', image), tile)