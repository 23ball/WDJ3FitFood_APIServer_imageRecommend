from keras.models import Sequential
from keras.layers import Convolution2D, MaxPool2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.utils import np_utils
import numpy as np
import os



root_dir = "./input/"
# categories = ["dongas", "kimchi", "onion", "ttukbul", "rice"]
# nb_classes = len(categories)
image_size = 50

image_w = 64
image_h = 64

def main():
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    # os.environ["CUDA_VISIBLE_DEVICES"] = "0,1" # GPU 0번과 1번 사용시 설정
    os.environ["CUDA_VISIBLE_DEVICES"] = "" # CPU만 사용할 경우 설정
    X_train, X_test, y_train, y_test = np.load("./input/image/5obj.npy", allow_pickle=True)
    X_train = X_train.astype("float") / 256
    X_test = X_test.astype("float") / 256
    y_train = np_utils.to_categorical(y_train, nb_classes)
    y_test = np_utils.to_categorical(y_test, nb_classes)
    model = model_train(X_train, y_train)
    model_eval(model, X_test, y_test)

def build_model(in_shape, resNum):

    caltech_dir = './images/' + str(resNum)
    categories = os.listdir(caltech_dir)
    if ".DS_Store" in categories :
       categories.remove('.DS_Store')
    categories = sorted(categories)
    nb_classes = len(categories)


    model = Sequential()
    model.add(Convolution2D(32,3,3, 
        border_mode='same', 
        input_shape=in_shape))
    model.add(Activation('relu'))
    model.add(MaxPool2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Convolution2D(64,3,3, border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3))
    model.add(MaxPool2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nb_classes))
    model.add(Activation('softmax'))
    model.compile(loss='binary_crossentropy',
        optimizer='rmsprop',
        metrics=['accuracy'])
    return model

def model_train(X, y):
    model = build_model(X.shape[1:])
    model.fit(X, y, batch_size=32, nb_epoch=50)
    hdf5_file="./input/image/food-model.hdf5"
    model.save_weights(hdf5_file)
    return model

def model_eval(model, X, y):
    score = model.evaluate(X_test, y_test)
    print('loss=', score[0])
    print('accuracy=', score[1])


if __name__ == "__main__":
    main()