from Models.Entry import Entry
from Services.CrossCorrelation import myCorrelation
from Services.DataLoader import DataLoader
from Services.Display import display
from Services.ImageResizer import resize_img
from os import listdir
import cv2
import numpy as np

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

    for entry in allEntries[2:]:
        for glyph in entry.glyphs[:]:
            pastMatches = []
            bestMatch = np.zeros((1,1))
            bestMatchVal = 0
            matchSquare = None
            sift = cv2.xfeatures2d.SIFT_create()
            glyph.image *= 255
            # display(glyph.image)
            kernel = np.ones((3,3),np.uint8)/9
            glyph.image = cv2.filter2D(glyph.image,-1,kernel)
            glyph.image = glyph.image.astype(np.uint8)

            display(glyph.image)
            
            for f in listdir(char_img_folder):
                # print(f)
                img = cv2.imread(char_img_folder + "\\"+f)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img = np.invert(img)
                img = resize_img(img)
                img = img.astype(np.uint8)

                entry = Entry(char_img_folder + "\\"+f)
                # entry.gardiners = sign_list[i]
                #BUG BUG BUG BUG BUG
                # BUG BUG
                #RIGHT SIDE OF IMAGES ARE BEING CUT OFF????
                entry.process_image()
                if len(entry.glyphs) == 0:
                    continue
                img = entry.glyphs[0].image * 255
                kernel = np.ones((3,3),np.uint8)/9
                img = cv2.filter2D(img,-1,kernel)
                img = img.astype(np.uint8)

                kp1,des1 = sift.detectAndCompute(img,None)
                # display(img)

                
                patches = []
                for i in range(len(kp1)):
                    pt = kp1[i].pt
                    pt = (int(pt[0]), int(pt[1]))
                    if len(patches) > 0:
                        closest = sorted(patches, key = lambda x: np.linalg.norm(np.asarray(pt)-(np.asarray(x[0]))))[0][0]
                        if np.linalg.norm(np.asarray(closest) - np.asarray(pt)) < 15:
                            continue
                    size = np.random.randint(30,60)
                    Xstart = max(pt[1]-size,0)
                    Xend = min(127,pt[1]+size)
                    Ystart = max(pt[0]-size,0)
                    Yend = min(127,pt[0]+size)
                    patches.append(   (pt,img[Xstart:Xend,Ystart:Yend])    )
                    if len(patches) > 20:
                        break
                maxVSum = 0
                maxVs= []
                for pt, patch in patches:
                    # display(patch)
                    correlation = cv2.matchTemplate(glyph.image, patch, cv2.TM_CCOEFF_NORMED)
                    minV,maxV,minL,maxL = cv2.minMaxLoc(correlation)
                    # display(correlation)  
                    top_left = maxL
                    bottom_right = (top_left[0] + 20, top_left[1] + 20)
                    squared = np.copy(glyph.image)
                    cv2.rectangle(squared,top_left,bottom_right,1,1)
                    # plt.imshow(squared)
                    # plt.show()
                    # maxVSum += maxV

                        
                    maxVs.append(maxV)
                if f == "F34.tiff":
                    display(img)  
                if len(patches) == 0 :
                    continue
                maxVs = sorted(maxVs, key = lambda x: -x)
                maxLens = 0
                for maxi in maxVs:
                    maxVSum+= maxi
                    maxLens+=1
                    if maxLens > 5:
                        break

                currentMatchVal = maxVSum/maxLens
                if currentMatchVal > bestMatchVal:
                    bestMatchVal = currentMatchVal
                    pastMatches = [img] + pastMatches
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
            for w in pastMatches[:4]:
                display(w)


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