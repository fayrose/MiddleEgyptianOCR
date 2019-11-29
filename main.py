from Models.Entry import Entry
from Services.CrossCorrelation import myCorrelation
from Services.DataLoader import DataLoader
from Services.Display import display
from Services.ImageResizer import resize_img
from os import listdir
import cv2
import numpy as np
from GlyphMatcher import match
def main():
# C:\Users\Tom-H\Documents\CSC420\MiddleEgyptianOCR\Services\DataLoader.py
    allEntries = []
    entry_img_folder = r"C:\Users\Tom-H\Documents\CSC420\Visual_Vygus\entry_images"
    data_json_path = r"C:\Users\Tom-H\Documents\CSC420\Visual_Vygus\DatasetGenerator\data.json"
    char_img_folder = r"C:\Users\Tom-H\Documents\CSC420\Visual_Vygus\character_images"
    dataLoader = DataLoader(entry_img_folder,data_json_path,char_img_folder)
    image_path,sign_list,answer = dataLoader.load_entries_on_page(3)
    p = 0
    for i in range(len(image_path)):
        entry = Entry(image_path[i])
        entry.gardiners = sign_list[i]
        entry.process_image()
        allEntries.append(entry)
        p += 1
        #FOR TESTING PURPOSES TO KILL CODE EARLY BUT SHOULD REMOVE EVENTUALLY
        if p > 5:
            break
    #match(allEntries,char_img_folder)


if __name__ == "__main__":
    main()