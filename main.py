from Models.Entry import Entry
from Services.Accuracy import processing_accuracy
from Services.CrossCorrelation import myCorrelation
from Services.DataLoader import DataLoader
from Services.Display import display
from Services.ImageResizer import resize_img
from GlyphMatcher import match
from MomentMatcher import Matcher
from os import listdir
import cv2
import numpy as np
from Models.LabelGenerator import generateLabel

def main():
# C:\Users\Tom-H\Documents\CSC420\MiddleEgyptianOCR\Services\DataLoader.py
    entry_img_folder = "/Users/thomashorga/Documents/CSC420/Visual_Vygus/entry_images"
    data_json_path = "/Users/thomashorga/Documents/CSC420/Visual_Vygus/DatasetGenerator/data.json"
    char_img_folder = "/Users/thomashorga/Documents/CSC420/Visual_Vygus/character_images"
    batches = [range(item, item + 100) if item != 2501 else range(item, 2569) for item in range(1, 2569, 100)] 

    dataLoader = DataLoader(entry_img_folder,data_json_path,char_img_folder)
    gm = Matcher(char_img_folder)
    proc_list, class_list = [], []

    for batch in batches:
        allEntries = []
        print("Batch - Pages {0} to {1}".format(batch.start, batch.stop - 1))
        image_path,sign_list, answer = dataLoader.load_entries_in_range(range(60,61))

        for i in range(len(image_path)):
            entry = Entry(image_path[i])
            entry.gardiners = sign_list[i]
            entry.process_image()
            allEntries.append(entry)

        accuracy , allMatches = match(allEntries,char_img_folder)

        for gardiners, matches in allMatches:
            generateLabel(matches)

        # proc_acc, filtered = processing_accuracy(allEntries)
        # print("Processing Accuracy: {0}".format(proc_acc))
        # class_rate, good_entries = gm.classify_entries(filtered)
        # print("Classification Accuracy: {0} \n".format(class_rate))
        # proc_list.append(proc_acc)
        # class_list.append(class_rate)



    print("Processing accuracy over all batches: {0}".format(sum(proc_list) / len(proc_list)))
    print("Classification accuracy over all batches: {0}".format(sum(class_list) / len(class_list)))

    # Now match good entries to their formatting
    #match(allEntries,char_img_folder)


if __name__ == "__main__":
    main()