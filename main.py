from Models.Entry import Entry
import matplotlib.pyplot as plt
from Services.DataLoader import DataLoader
from Services.CrossCorrelation import myCorrelation
from os import listdir
import cv2
import numpy as np

def display(image, boundaries=None, vertical=True):
    plt.imshow(image)
    if boundaries is not None:
        if vertical:
            for boundary in boundaries:
                plt.axvline(boundary)
        else:
            for boundary in boundaries:
                plt.axhline(boundary)
    plt.show()
#32x32 <- want
def resize_img(image):
    desired_size = 128
    old_size = image.shape[:2] # old_size is in (height, width) format

    ratio = float(desired_size)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])

    # new_size should be in (width, height) format
    image = cv2.resize(image, (new_size[1], new_size[0]))

    delta_w = desired_size - new_size[1]
    delta_h = desired_size - new_size[0]
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)

    color = [0, 0, 0]
    new_im = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT,
        value=color)
    return new_im
    # display(new_im)
def main():
# C:\Users\Tom-H\Documents\CSC420\MiddleEgyptianOCR\Services\DataLoader.py
    allEntries = []
    entry_img_folder = r"C:\Users\Tom-H\Documents\CSC420\Visual_Vygus\entry_images"
    data_json_path = r"C:\Users\Tom-H\Documents\CSC420\Visual_Vygus\DatasetGenerator\data.json"
    char_img_folder = r"C:\Users\Tom-H\Documents\CSC420\Visual_Vygus\character_images"
    dataLoader = DataLoader(entry_img_folder,data_json_path,char_img_folder)
    image_path,sign_list,answer = dataLoader.load_entries_on_page(3)
    for i in range(len(image_path)):
        entry = Entry(image_path[i])
        entry.gardiners = sign_list[i]
        entry.process_image()
        allEntries.append(entry)
        break

    for entry in allEntries:
        for glyph in entry.glyphs:
            bestMatch = np.zeros((1,1))
            bestMatchVal = 0
            matchSquare = None
            sift = cv2.xfeatures2d.SIFT_create()
            glyph.image[glyph.image > 0] = 255
            display(glyph.image)
            glyph.image = glyph.image.astype(np.uint8)
            kernel = np.ones((3,3),np.uint8)/9
            glyph.image = cv2.filter2D(glyph.image,-1,kernel)
            display(glyph.image)
            
            for f in listdir(char_img_folder):
                # print(f)
                img = cv2.imread(char_img_folder + "\\"+f)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img = np.invert(img)
                img = resize_img(img)
                img = img.astype(np.uint8)
                
                kp1,des1 = sift.detectAndCompute(img,None)
                # display(img)

                
                patches = []
                for i in range(len(kp1)):
                    pt = kp1[i].pt
                    pt = (int(pt[0]), int(pt[1]))
                    if len(patches) > 0:
                        closest = sorted(patches, key = lambda x: np.linalg.norm(np.asarray(pt)-(np.asarray(x[0]))))[0][0]
                        if np.linalg.norm(np.asarray(closest) - np.asarray(pt)) < 40:
                            continue
                    if pt[0] < 20 or pt[0] > 107:
                        continue
                    if pt[1] < 20 or pt[1] > 107:
                        continue
                    patches.append(   (pt,img[pt[1]-20:pt[1]+20,pt[0]-20:pt[0]+20])    )
                    if len(patches) > 10:
                        break
                maxVSum = 0
                for pt, patch in patches:
                    # display(patch)
                    correlation = cv2.matchTemplate(glyph.image, patch, cv2.TM_CCORR_NORMED)
                    minV,maxV,minL,maxL = cv2.minMaxLoc(correlation)
                    # display(correlation)  
                    top_left = maxL
                    bottom_right = (top_left[0] + 20, top_left[1] + 20)
                    squared = np.copy(glyph.image)
                    cv2.rectangle(squared,top_left,bottom_right,1,1)
                    # plt.imshow(squared)
                    # plt.show()
                    maxVSum += maxV
                if len(patches) == 0 :
                    continue
                if maxVSum/len(patches) > bestMatchVal:
                    bestMatchVal = maxVSum/len(patches)
                    bestMatch = img
                    matchSquare =squared

                # display(glyph.image)
                # display(img)



                # correlation = cv2.matchTemplate(glyph.image, img, cv2.TM_CCORR_NORMED)
                # correlation = cv2.filter2D(glyph.image,-1,img)

                # correlation = myCorrelation(glyph.image,img,"same")
                # display(correlation)        

                # if np.amax(correlation) > np.amax(bestMatch):
                #     display(correlation)

                #     bestMatch = img
                #     bestMatchCorrelation = correlation
            display(matchSquare)
            display(bestMatch)
            display(glyph.image)


        print(entry)
    # entry = Entry("/Users/thomashorga/Documents/CSC420/MiddleEgyptianOCR/sample4.png")
    # entry.gardiners = ["A1","B1","Z2", "Z2B","N16"]
    # display(entry.image)
    # entry.split_into_words()
    # entry.split_blocks_into_verticals()
    # display(entry.blocks[0].image)
    # display(entry.blocks[0].verticals[1].image)


if __name__ == "__main__":
    main()