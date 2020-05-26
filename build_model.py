from keras.models import Sequential
from keras.layers import Convolution2D, MaxPool2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.utils import np_utils
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from PIL import Image
import os, glob, numpy as np
from sklearn.model_selection import train_test_split

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "" # CPU만 사용할 경우 설정

image_w = 64
image_h = 64
pixels = image_h * image_w * 3

# 이미지 크기 조정 비율
optRescale = 1./255
# 이미지 회전 
optRotationRange=10
# 이미지 수평 이동
optWidthShiftRange=0.2
# 이미지 수직 이동
optHeightShiftRange=0.2
# 이미지 밀림 강도 
optShearRange=0.5
# 이미지 확대/ 축소 
optZoomRange=[0.9,2.2]
# 이미지 수평 뒤집기 
optHorizontalFlip = True 
# 이미지 수직 뒤집기 
optVerticalFlip = True
optFillMode='nearest'
# 이미지당 늘리는 갯수 
optNbrOfIncreasePerPic = 5
# 배치 수 
optNbrOfBatchPerPic = 5

train_datagen = ImageDataGenerator(rescale=optRescale, 
                                   rotation_range=optRotationRange,
                                   width_shift_range=optWidthShiftRange,
                                   height_shift_range=optHeightShiftRange,
                                   shear_range=optShearRange,
                                   zoom_range=optZoomRange,
                                   horizontal_flip=optHorizontalFlip,
                                   vertical_flip=optVerticalFlip,
                                   fill_mode=optFillMode)


images_dir = os.listdir('./images')
for oneResImagesDir in images_dir:
    if os.path.isfile('./numpy_data/' + oneResImagesDir+ '.npy'):
        continue
    X = []
    y = []
    print(oneResImagesDir)
    if oneResImagesDir == '84':
        caltech_dir = './images/' + oneResImagesDir
        categories = sorted(os.listdir(caltech_dir))
        nb_classes = len(categories)
        if nb_classes == 0:
            continue
        
        for idx, cat in enumerate(categories):
            #one-hot 돌리기.
            label = [0 for i in range(nb_classes)]
            label[idx] = 1
            image_dir = caltech_dir + "/" + cat
            files = glob.glob(image_dir+"/*.jpg")
            if len(files) < 50:
                for i, f in enumerate(files):
                    img = load_img(f)
                    x = img_to_array(img)
                    x = x.reshape((1,) + x.shape)
                    i = 0
                    for batch in train_datagen.flow(x, batch_size=1, save_to_dir=image_dir, save_prefix='tri', save_format='jpg'):
                        i += 1
                        if i > 30: 
                            break
            files = glob.glob(image_dir+"/*.png")
            for i, f in enumerate(files):
                img = Image.open(f)
                img = img.convert("RGB")
                img = img.resize((image_w, image_h))
                data = np.asarray(img)

                X.append(data)
                y.append(label)
                if i % 700 == 0:
                    print(cat, " : ", f)

        X = np.array(X)
        y = np.array(y)
        #1 0 0 0 이면 airplanes
        #0 1 0 0 이면 buddha 이런식
        X_train, X_test, y_train, y_test = train_test_split(X, y)
        xy = (X_train, X_test, y_train, y_test)
        np.save('./numpy_data/' + oneResImagesDir+ '.npy', xy)

        print("ok", len(y))
