import cv2
import os
import numpy as np
from Services.ImageResizer import resize_img

class Matcher:
    def __init__(self, char_folder_path):
        self.char_folder = char_folder_path
        self.char_moments = {}
        self.__get_train_moments()

    def __get_train_moments(self):
        for char in os.listdir(self.char_folder):
            location = os.path.join(self.char_folder, char)
            glyph_name = char[:char.index('.')]
            img = resize_img(cv2.bitwise_not(cv2.imread(location, flags=cv2.IMREAD_GRAYSCALE)), False) / 255.0
            huMoment = cv2.HuMoments(cv2.moments(img))
            self.char_moments[glyph_name] = huMoment

    def classify(self, image_to_classify):
        compare = lambda a, b: np.sum(np.abs(a - b))
        moment = cv2.HuMoments(cv2.moments(image_to_classify))

        best_candidate_name = None
        best_candidate_moment = float('inf')

        for glyph, candidate_moment in self.char_moments.items():
            dist = compare(moment, candidate_moment)
            if dist < best_candidate_moment:
                best_candidate_moment = dist
                best_candidate_name = glyph
        return best_candidate_name
    

