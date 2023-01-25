import tensorflow as tf
from sklearn.model_selection import train_test_split
import os
import cv2
import numpy as np

# images are all in tiles folder in a folder named after the letter
path = 'tiles/'
images = []
labels = []
for folder in os.listdir(path):
    for image in os.listdir(os.path.join(path, folder)):
        # load the image
        img = cv2.imread(os.path.join(path, folder, image), cv2.IMREAD_GRAYSCALE)
        # resize the image
        img = cv2.resize(img, (18, 17))
        # add the image to the list of images
        images.append(img)
        # add the label to the list of labels
        labels.append(folder)

# Convert labels to one-hot encoded format
letter_to_int = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25}
num_classes = len(letter_to_int)
labels = [letter_to_int[x] for x in labels]
labels = tf.keras.utils.to_categorical(labels, num_classes)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2)

# Define the model
model = tf.keras.Sequential()
model.add(tf.keras.layers.Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(17, 18, 1)))
model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(num_classes, activation='softmax'))

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(np.array(X_train), np.array(y_train), epochs=9)

# Evaluate the model
test_loss, test_acc = model.evaluate(np.array(X_test), np.array(y_test))
print('Test accuracy:', test_acc)

# Save the model
model.save('tile_classifier.h5')