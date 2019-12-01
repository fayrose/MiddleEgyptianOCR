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

def main():
# C:\Users\Tom-H\Documents\CSC420\MiddleEgyptianOCR\Services\DataLoader.py
    allEntries = []
    entry_img_folder = r"C:\Users\lfr2l\source\repos\DatasetGenerator\entry_images"
    data_json_path = r"C:\Users\lfr2l\source\repos\DatasetGenerator\DatasetGenerator\data.json"
    char_img_folder = r"C:\Users\lfr2l\source\repos\DatasetGenerator\character_images"
    dataLoader = DataLoader(entry_img_folder,data_json_path,char_img_folder)
    image_path,sign_list,answer = dataLoader.load_entries_on_page(3)
    p = 0
    for i in range(len(image_path)):
        entry = Entry(image_path[i])
        entry.gardiners = sign_list[i]
        entry.process_image()
        allEntries.append(entry)
        p += 1
        
    proc_acc, filtered = processing_accuracy(allEntries)
    print("Processing Accuracy: {0}".format(proc_acc))
    gm = Matcher(char_img_folder)
    class_rate, good_entries = gm.classify_entries(filtered)
    print("Classification Accuracy: {0}".format(class_rate))

    # Now match good entries to their formatting
    #match(allEntries,char_img_folder)


if __name__ == "__main__":
    main()