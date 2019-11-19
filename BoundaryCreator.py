import numpy as np
import cv2 as cv

def create_boundaries(image, vertical=False):
    bound_axis = 1 if vertical else 0
    vectorized_image = np.sum(image, axis=bound_axis).astype(np.uint8)

    for i in range(len(vectorized_image)):
        if vectorized_image[i] == 0:
            vectorized_image[i] = 1
        else:
            vectorized_image[i] = 0

    canny = cv.Canny(vectorized_image, 3.5, 3.5)
    canny = canny.reshape(canny.shape[0])
    boundaries = np.argwhere(canny > 200)
    boundaries = boundaries.reshape(boundaries.shape[0])
    return boundaries