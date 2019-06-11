import os
import cv2
from tqdm import tqdm
import pickle
import numpy as np
from math import sqrt

from . import config

if config.FEATURE_VECTOR_FUNCTION == "CNN":
    import keras_rmac.rmac

def get_frame(frame_index, video):
    """
    Given a frame position number and the videocapture variable, returns the frame as an image object (numpy array)
    """
    video.set(1,frame_index)
    _, img = video.read()

    return img

fouriers = [
    [1,1,1,1,1,1,1,1],
    [-1,1,-1,1,1,-1,1,-1], 
    [-sqrt(2)/2, 0, sqrt(2)/2, -1, 1, -sqrt(2)/2,0,sqrt(2)/2],
    [-sqrt(2)/2, -1, -sqrt(2)/2, 0, 0, sqrt(2)/2, 1, sqrt(2)/2], 
    [0, -1, 0, 1, 1, 0, -1, 0],
    [1,0,-1, 0, 0, -1, 0, 1],
    [sqrt(2)/2, 0 , -sqrt(2)/2, -1, 1, sqrt(2)/2, 0, -sqrt(2)/2],
    [-sqrt(2)/2, 1, -sqrt(2)/2, 0, 0, sqrt(2)/2, -1, sqrt(2)/2]
]

for i,f in enumerate(fouriers):
    f.insert(4,0)
    fouriers[i] = np.array(f)
    fouriers[i] = fouriers[i].reshape((3,3)).astype('float32')

max_vals = []
for f in fouriers:
    m = np.array([255])
    m = cv2.matchTemplate(m.astype('float32'),f, cv2.TM_CCORR).clip(0,255)
    max_vals.append(cv2.matchTemplate(m.astype('float32'),f, cv2.TM_CCORR)[0][0])

def color_texture_moments(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    result = []
    for channel in range(0,3):
        for template, max_val in zip(fouriers, max_vals):
            r = cv2.matchTemplate(img[:,:,channel].astype('float32'),template, cv2.TM_CCORR)
            
            r = r / max_val
            result.append(r.mean())
            result.append(r.std())
                            
    return result


def cnn_feature_vectors(img):
    feature_vector = keras_rmac.rmac.to_feature_vector(img)
    return feature_vector


def get_img_color_hist(image, binsize):
    """
    Given an image as input, output its color histogram as a numpy array.
    Binsize will determine the size
    """

    chans = cv2.split(image)
    main = np.zeros((0,1))

    # loop over the image channels
    for chan in chans:
        # create a histogram for the current channel and
        # concatenate the resulting histograms for each
        # channel
        hist = cv2.calcHist([chan], [0], None, [binsize], [0, 256])
        main = np.append(main,hist)

    #normalize so sum of all values equals 1
    main = main / (image.shape[0] * image.shape[1])

    return main.astype('float32')

def color_hist(img):
    result = get_img_color_hist(img, 100)
    return result

def construct_feature_vectors(video_fn, result_dir_name, vector_function):
    base_video_fn = os.path.basename(video_fn)
    video = cv2.VideoCapture(video_fn)
    series_dir = os.path.dirname(video_fn)
    vectors_fn = os.path.join(series_dir, result_dir_name, base_video_fn + ".p")

    # make sure folder of experimentname exists or create otherwise
    os.makedirs(os.path.dirname(vectors_fn), exist_ok=True)

    # check if histograms exist, else create them and save to pickle
    if not os.path.isfile(vectors_fn):

        # construct the histograms from frames at the start of scenes
        feature_vectors = []
        total = int(video.get(cv2.CAP_PROP_FRAME_COUNT) / config.FRAMEJUMP) - 1

        # apply the vector function for every xth frame determined by framejump
        for i in tqdm(range(total)):
            img = get_frame(i * config.FRAMEJUMP, video)
            feature_vector = vector_function(img)
            feature_vectors.append(feature_vector)
            
        # save to pickle file
        with open(vectors_fn, 'wb') as handle:
            pickle.dump(feature_vectors, handle, protocol=2)