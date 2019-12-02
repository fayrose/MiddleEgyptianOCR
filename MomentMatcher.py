import cv2
import os
import numpy as np
from collections import Counter
from Models.Entry import Entry
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
        needs_fixing = len(entry.gardiners) != len(entry.glyphs)
        replace_dict = {"N19": "N18", "Z4": "Z5A", "Z4A": "Z1", "Z4B":"Z1A"}
        if len(entry.gardiners) == 1 and len(entry.glyphs) == 1:
            entry.glyphs[0].set_classification(entry.gardiners[0])
            return True
        
        input = entry.gardiners
        if needs_fixing:
            input = [replace_dict[x] if x in replace_dict else x for x in input]

        # Classify each sign in entry
        for sign in entry.glyphs:
            classification, dist = self.classify(sign.image, input)
            sign.set_classification(classification)

            if classification in class_dict:
                class_dict[classification].append((dist, sign))
            else:
                class_dict[classification] = [(dist, sign)]
        
        # Create count dict of classified signs and assert equal
        dict1 = Counter(entry.gardiners)
        if needs_fixing:
            self.fix_groupings(entry, replace_dict, dict1, class_dict)
        dict2 = Counter([x.gardiner for x in entry.glyphs])
        
        if dict1 == dict2: return True
        if len(entry.gardiners) != len(entry.glyphs): return False

        # If not equal, take sign that has been classified more than it should
        # and only take top k correct. Distribute other signs.
        return self.try_and_recover(entry, class_dict, dict1, dict2)
    
    def fix_groupings(self, entry, replace_dict, dict1, class_dict):
        for sign in replace_dict.keys():
            if sign in dict1:
                if sign != "N19":
                    self.fix_hor_grouping(entry, sign, replace_dict[sign], dict1, class_dict)
                else:
                    self.fix_vert_grouping(entry, sign, replace_dict[sign], dict1, class_dict)

    def fix_hor_grouping(self, entry, to_replace, replace_with, dict1, class_dict):
        num_groups = dict1[to_replace]
        replaced = 0
        grouping_candidates = sorted([x for x in entry.glyphs if x.gardiner == replace_with], key=lambda x: x.left)
        
        if len(grouping_candidates) % 2 == 0:
            itr = range(0, len(grouping_candidates), 2)
        else:
            itr = range(0, len(grouping_candidates))

        for i in itr:
            group = [grouping_candidates[i], grouping_candidates[i + 1]]
            if entry.isHori(group) or group[1].left - group[0].right < 15:
                grouped = entry.groupHori(group)
                grouped.gardiner = to_replace
                entry.glyphs.remove(group[0])
                entry.glyphs.remove(group[1])
                entry.glyphs.append(grouped)
                class_dict[to_replace] = [(0, grouped)]

                # Update class dict to reflect changes
                to_delete = [i for i in range(len(class_dict[replace_with])) if class_dict[replace_with][i][1] in group][::-1]
                for item in to_delete:
                    del class_dict[replace_with][item]
                    if len(class_dict[replace_with]) == 0: del class_dict[replace_with]                 
                replaced += 1
                if replaced == num_groups: return
        
    def fix_vert_grouping(self, entry, to_replace, replace_with, dict1, class_dict):
        num_groups = dict1[to_replace]
        replaced = 0
        grouping_candidates = sorted([x for x in entry.glyphs if x.gardiner == replace_with], key=lambda x: x.left)
        for i in range(0, len(grouping_candidates), 2):
            group = [grouping_candidates[i], grouping_candidates[i + 1]]
            if abs(group[0].left - group[1].left) < 3 and abs(group[0].upper - group[1].upper) > 3:
                grouped = entry.groupVert(group)
                grouped.gardiner = to_replace
                entry.glyphs.remove(group[0])
                entry.glyphs.remove(group[1])
                entry.glyphs.append(grouped)
                replaced += 1
                if replaced == num_groups: return

    def try_and_recover(self, entry, class_dict, dict1 : Counter, dict2 : Counter, print_success=False):
        # Partition dictionaries into over/under/correctly classified
        under, same = {}, {}
        over = {item : [0, dict2[item]] for item in dict2.keys() if item not in dict1}

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