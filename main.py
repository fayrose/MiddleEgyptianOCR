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
    entry_img_folder = r"C:\Users\lfr2l\source\repos\DatasetGenerator\entry_images"
    data_json_path = r"C:\Users\lfr2l\source\repos\DatasetGenerator\DatasetGenerator\data.json"
    char_img_folder = r"C:\Users\lfr2l\source\repos\DatasetGenerator\character_images"
    batches = [range(item, item + 100) if item != 2501 else range(item, 2569) for item in range(1, 2569, 100)] 

    dataLoader = DataLoader(entry_img_folder,data_json_path,char_img_folder)
    gm = Matcher(char_img_folder)
    proc_list, class1_list, class2_list = [], [], []

    for batch in batches:
        allEntries = []
        print("Batch - Pages {0} to {1}".format(batch.start, batch.stop - 1))
        image_path,sign_list, answer = dataLoader.load_entries_in_range(batch)

        for i in range(len(image_path)):
            entry = Entry(image_path[i])
            entry.gardiners = [x if x != "{V11 should be 'mirrored' V11" else "V11" for x in sign_list[i]]
            entry.process_image()
            allEntries.append(entry)

        # Image Processing Stage
        proc_acc, filtered = processing_accuracy(allEntries)
        print("Processing Accuracy: {0}".format(proc_acc))
        
        # Image Classification Stages
        #accuracy , allMatches = match(allEntries,char_img_folder)
        #print("Cross Correlation + SIFT Classification Accuracy: {0}".format(accuracy))

        class_rate, good_entries = gm.classify_entries(filtered)
        print("Hu Moments Classification Accuracy: {0} \n".format(class_rate))
        
        # Image Labelling Stage
        #for gardiners, matches in allMatches:
        #    generateLabel(matches)

        #for entry in good_entries:
        #    generateLabel(matches)

        # Test accuracy of both

        # Add metrics to list for average over all batches
        proc_list.append(proc_acc)
        class1_list.append(class_rate)
        #class2_list.append(accuracy)

    print("Processing accuracy over all batches: {0}".format(sum(proc_list) / len(proc_list)))
    print("Hu Classification accuracy over all batches: {0}".format(float(sum(class1_list)) / len(class1_list)))
    #print("CC + SIFT Classification accuracy over all batches: {0}".format(float(sum(class2_list)) / len(class2_list)))



if __name__ == "__main__":
    main()