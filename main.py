from os import listdir

import cv2
import numpy as np
from tqdm import trange

from GlyphMatcher import CCSiftMatcher
from Models.Entry import Entry
from Models.LabelGenerator import generateLabel
from MomentMatcher import Matcher
from Services.Accuracy import *
from Services.CrossCorrelation import myCorrelation
from Services.DataLoader import DataLoader
from Services.Display import display
from Services.ImageResizer import resize_img


def main():
# C:\Users\Tom-H\Documents\CSC420\MiddleEgyptianOCR\Services\DataLoader.py
    entry_img_folder = "/Users/thomashorga/Documents/CSC420/Visual_Vygus/entry_images"
    data_json_path = "/Users/thomashorga/Documents/CSC420/Visual_Vygus/DatasetGenerator/data2.json"
    char_img_folder = "/Users/thomashorga/Documents/CSC420/Visual_Vygus/character_images"

    dataLoader = DataLoader(entry_img_folder,data_json_path,char_img_folder)
    gm = Matcher(char_img_folder)
    proc_list, class1_list, class2_list = [], [], []
    batches = [range(item, item + 100) if item != 2501 else range(item, 2569) for item in range(1, 2569, 100)] 

    for batch in batches:
        allEntries = []
        print("Batch - Pages {0} to {1}".format(batch.start, batch.stop - 1))
        image_path,sign_list, answer = dataLoader.load_entries_in_range(batch)

        for i in trange(len(image_path), desc="Processing images", leave=None):
            entry = Entry(image_path[i])
            entry.answer = answer[i]
            entry.gardiners = [x if x != "{V11 should be 'mirrored' V11" else "V11" for x in sign_list[i]]
            entry.process_image()
            allEntries.append(entry)

        # Image Processing Stage
        proc_acc, filtered = processing_accuracy(allEntries)
        print("Processing Accuracy: {0}".format(proc_acc))

        # class_rate, good_entries = gm.classify_entries(filtered)
        # print("Hu Moments Classification Accuracy: {0} \n".format(class_rate))
        
        # Image Classification Stages
        cc_sift = CCSiftMatcher(char_img_folder)
        accuracy, CCSCEntries = cc_sift.match(filtered)
        print("Cross Correlation + SIFT Classification Accuracy: {0}".format(accuracy))

        # Image Labelling Stage
        for entry in CCSCEntries:
            matches = entry.CCSCMatches
            label = generateLabel(matches)
            entry.CCSCFormatted = label

        CCSC_formatted = [x.CCSCFormatted for x in CCSCEntries]
        CCSC_answer = [x.CCSCAnswer for x in good_entries]
        order_acc = get_order_accuracy(CCSC_formatted, [x.gardiners for x in good_entries])
        print("Order Accuracy for Hu Moment Classified: {0}".format(order_acc))

        glyphblock_acc = get_glyph_accuracy(CCSC_formatted, CCSC_answer)
        print("GlyphBlock Accuracy for CCSC Moment Classified: {0}".format(glyphblock_acc))
        
        entry_acc = get_entry_accuracy(CCSC_formatted, CCSC_answer)
        print("Entry Accuracy for CCSC Moment Classified: {0}".format(entry_acc))


        for entry in good_entries:
            entry_tpl = [(glyph.gardiner, glyph) for glyph in entry.glyphs]
            label = generateLabel(entry_tpl)
            entry.formatted = label

        # Test accuracy of both
        hu_formatted = [x.formatted for x in good_entries]
        hu_answer = [x.answer for x in good_entries]
        order_acc = get_order_accuracy(hu_formatted, [x.gardiners for x in good_entries])
        print("Order Accuracy for Hu Moment Classified: {0}".format(order_acc))

        glyphblock_acc = get_glyph_accuracy(hu_formatted, hu_answer)
        print("GlyphBlock Accuracy for Hu Moment Classified: {0}".format(glyphblock_acc))
        
        entry_acc = get_entry_accuracy(hu_formatted, hu_answer)
        print("Entry Accuracy for Hu Moment Classified: {0}".format(entry_acc))

        # Add metrics to list for average over all batches
        proc_list.append(proc_acc)
        class1_list.append(class_rate)
        class2_list.append(accuracy)
        #class2_list.append(accuracy)

    print("Processing accuracy over all batches: {0}".format(sum(proc_list) / len(proc_list)))
    print("Hu Classification accuracy over all batches: {0}".format(float(sum(class1_list)) / len(class1_list)))
    print("CC + SIFT Classification accuracy over all batches: {0}".format(float(sum(class2_list)) / len(class2_list)))



if __name__ == "__main__":
    main()
