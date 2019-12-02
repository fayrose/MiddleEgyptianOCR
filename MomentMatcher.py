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
                candidate_moment = self.char_moments[glyph.upper()]
                dist = compare(moment, candidate_moment)
                if dist < best_candidate_moment:
                    best_candidate_moment = dist
                    best_candidate_name = glyph

        return best_candidate_name, best_candidate_moment

    def classify_entry(self, entry):
        class_dict = {}
        if len(entry.gardiners) == 1 and len(entry.glyphs) == 1:
            entry.glyphs[0].set_classification(entry.gardiners[0])
            return True

        # Classify each sign in entry
        classified = []
        for sign in entry.glyphs:
            classification, dist = self.classify(sign.image, entry.gardiners)
            classified.append(classification)
            sign.set_classification(classification)

            if classification in class_dict:
                class_dict[classification].append((dist, sign))
            else:
                class_dict[classification] = [(dist, sign)]
        
        # Create count dict of classified signs and assert equal
        dict1 = Counter(entry.gardiners)
        dict2 = Counter(classified)
        if dict1 == dict2: return True

        # If not equal, take sign that has been classified more than it should
        # and only take top k correct. Distribute other signs.
        return self.try_and_recover(entry, class_dict, dict1, dict2)
    
    def try_and_recover(self, entry, class_dict, dict1 : Counter, dict2 : Counter, print_success=False):
        # Partition dictionaries into over/under/correctly classified
        over, under, same = {}, {}, {}
        for dkey in dict1.keys():
            d1, d2 = dict1[dkey], dict2.get(dkey, 0)
            if d1 > d2:
                under[dkey] = [d1, d2]
            elif d1 < d2:
                over[dkey] = [d1, d2]
            elif d1 == d2:
                same[dkey] = d1
        
        to_remove_over, to_remove_under = [], []
        # Distribute overclassified to underclassified
        for dkey, tpl in over.items():
            # Get distance of each in classified
            # Take lowest d1-distances to keep
            classed_sorted_by_dist = sorted(class_dict.get(dkey, 0), key=lambda x: x[0])
            to_reclassify = classed_sorted_by_dist[tpl[0]:]
            
            # For any distances higher than that, reclassify to under
            for _, sign in to_reclassify:
                out_class, _ = self.classify(sign.image, under.keys())
                sign.set_classification(out_class)

            # Update dictionaries
                over[dkey][1] -= 1
                if over[dkey][0] == over[dkey][1]:
                    same[dkey] = over[dkey][0]
                    to_remove_over.append(dkey)

                under[out_class][1] += 1
                if under[out_class][0] == under[out_class][1]:
                    same[out_class] = under[out_class][0]
                    to_remove_under.append(out_class)
        
        for item in to_remove_over:  del over[item]
        for item in to_remove_under: del under[item]

        rec_success = len(under) == 0 and len(over) == 0
        if print_success:
            print("Reconstruction successful: {0}".format(rec_success))
        return rec_success

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