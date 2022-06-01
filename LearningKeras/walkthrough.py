# Python script for running the demo found here:
# https://elitedatascience.com/keras-tutorial-deep-learning-in-python#step-2

import numpy as np

# Set the randomizer seed to known value in demo
np.random.seed(123)

from keras.models import Sequential # Sequential == linear network layers
from keras.layers import Dense, Dropout, Activation, Flatten # "Core" Neural Net layers
from keras.layers import Conv2D, MaxPooling2D # CNN layers for efficient training
from keras.utils import np_utils

from keras.datasets import mnist # Get the mnist dataset

(X_train, Y_train), (X_test, Y_test) = mnist.load_data() # grab the preshuffled data

print(X_train.shape) #(60000, 28, 28) => 60k images that are 28x28 pixels

from matplotlib import pyplot as plt
plt.imshow(X_train[0])
#plt.show() # Display the first image of the lot

# Keras requires that we denote the depth of the image - in this case it is just 1
X_train = X_train.reshape(X_train.shape[0],1,28,28)
X_test = X_test.reshape(X_test.shape[0],1,28,28)

print(X_train.shape) #(60000, 1, 28, 28) => 60k images that are 28x28 pixels with a depth of 1

# Convert the types of the input data to floats
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')

# Normalize the data to the range [0,1]
X_train /= 255
X_test /= 255

print(Y_train.shape) #(60000)
print(Y_train[:10]) # Classes aren't sorted numerically

# Convert 1-dimensional class arrays into 10 dimensional class matrices
Y_train = np_utils.to_categorical(Y_train,10)
Y_test = np_utils.to_categorical(Y_test,10)

print(Y_train.shape) #(60000, 10)
#print(Y_train[:10])

model = Sequential() # Declare the sequential model format

# All of the following steps were generated through math and theory that were not explained

# Declare a convolution input layer
# First three parameters correspond to number of convolution filters used, number of rows in the kernel, and number of columns in the kernel
# Input shape is just the shape of data we are feeding - 1dx28wx28h
model.add(Conv2D(32, (3, 2), activation='relu', input_shape=(1,28,28)))
#model.add(Convolution2D(32, 3, 3, activation='relu', input_shape=(1,28,28)))
#model.add(Conv2D(filters=32, kernel_size=3, strides=3, activation='relu', input_shape=(1,28,28)))

# Should be (None, 32, 26, 26), but is (None, -1, 26, 32)
print(model.output_shape) 

# Add another input layer
model.add(Conv2D(32, (2, 3), activation='relu'))
# Reduce the number of parameters in our model by setting a 2x2 pooling filter across the prev layer, taking the max of the 4 vals in the 2x2 filter
model.add(MaxPooling2D(pool_size=(2,2))) 
model.add(Dropout(0.25)) # Regularizes the model to prevent overfitting

# Add a fully connected layer and the output layer
model.add(Flatten())
model.add(Dense(128, activation='relu')) # First param is output size of layers
model.add(Dropout(0.5))
model.add(Dense(10, activation='softmax')) # Reduce output to the 10 categories

# Compile the model and declare the loss function:
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

#Fit the model by declaring the batch size and number of epochs to train for
model.fit(X_train, Y_train, 
          batch_size=32, nb_epoch=10, verbose=1)

# Evaluate model on the test data
score = model.evaluate(X_test, Y_test, verbose=0)

# Further reading links:
# https://www.quora.com/How-does-the-dropout-method-work-in-deep-learning-And-why-is-it-claimed-to-be-an-effective-trick-to-improve-your-network
# https://keras.io/api/losses/
# https://keras.io/api/optimizers/
# https://keras.io/api/callbacks/
