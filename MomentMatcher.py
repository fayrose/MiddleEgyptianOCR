import cv2
import os
import numpy as np
from collections import Counter
from Services.ImageResizer import resize_img
from Services.Display import display

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

    def classify(self, image_to_classify, chars_to_compare=None):
        compare = lambda a, b: np.sum(np.abs(a - b))
        moment = cv2.HuMoments(cv2.moments(image_to_classify))

        best_candidate_name = None
        best_candidate_moment = float('inf')

        if chars_to_compare is None:
            for glyph, candidate_moment in self.char_moments.items():
                dist = compare(moment, candidate_moment)
                if dist < best_candidate_moment:
                    best_candidate_moment = dist
                    best_candidate_name = glyph
        
        else:
            for glyph in set(chars_to_compare):
                candidate_moment = self.char_moments[glyph]
                dist = compare(moment, candidate_moment)
                if dist < best_candidate_moment:
                    best_candidate_moment = dist
                    best_candidate_name = glyph

        return best_candidate_name

    def classify_entry(self, entry):
        if len(entry.gardiners) == 1 and len(entry.glyphs) == 1:
            entry.glyphs[0].set_classification(entry.gardiners[0])
            return True

        
        # Classify each sign in entry
        classified = []
        for sign in entry.glyphs:
            classification = self.classify(sign.image, entry.gardiners)
            classified.append(classification)
            sign.set_classification(classification)
        
        # Create count dict of classified signs and assert equal
        dict1 = Counter(entry.gardiners)
        dict2 = Counter(classified)
        if dict1 == dict2: return True

        # If not equal, take sign that has been classified more than it should
        # and only take top k correct. Distribute other signs.
        print("Deal with this situation.")
        return False
    
    def classify_entries(self, entry_list):
        num = 0
        good_entries = []
        for entry in entry_list:
            out = self.classify_entry(entry)
            if out:
                num += 1
                good_entries.append(entry)
        if len(entry_list) == 0: return 0.0
        return float(num) / len(entry_list), good_entries