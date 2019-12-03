from Models.Entry import Entry
from Services.CrossCorrelation import myCorrelation
from Services.DataLoader import DataLoader
from Services.Display import display
from Services.ImageResizer import resize_img
from os import listdir
import cv2
import numpy as np
from BoundaryCreator import create_boundaries
from Services.Display import display
from tqdm import tqdm
#V28
def getAccuracy(allEntries,matches):
    totalAccuracy = 0
    for i in range(len(matches)):
        gardiners,entryMatches = matches[i]
        entry = allEntries[i]
        print(gardiners)
        print(entry.gardiners)
        intersect = set(gardiners).intersection(set(entry.gardiners))
        accuracy = len(intersect)/len(set(entry.gardiners))

        # if accuracy < 1:
        #     print(entryMatches)
        #     display(entry.image)
        totalAccuracy += accuracy
    totalAccuracy = totalAccuracy/len(matches)
    print(totalAccuracy)
    return (totalAccuracy,matches)


def match(allEntries,char_img_folder):
    matches = []
    for entry in tqdm(allEntries, desc="Matching CC + SIFT", leave=None):
        entryMatches = []
        entryGardiners = []
        for glyph in entry.glyphs:
            pastMatches = []
            bestMatch = np.zeros((1,1))
            bestGardiner = ""
            bestMatchVal = 0
            matchSquare = None
            sift = cv2.xfeatures2d.SIFT_create()
            glyph.image *= 255
            kernel = np.ones((3,3),np.uint8)/9
            glyph.image = cv2.filter2D(glyph.image,-1,kernel)
            glyph.image = glyph.image.astype(np.uint8)

            
            for f in listdir(char_img_folder):
                # if gardiner 
                # print(f)
                if f[0] == ".":
                    continue
                gardiner = f.split(".")[0]
                if not gardiner in entry.gardiners:
                    continue
                img = cv2.imread(char_img_folder + "/"+f)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img = np.invert(img)
                # get borders, remove them
                horizontal_bounds = create_boundaries(img)
                vert_bounds = create_boundaries(img,True)

                if len(horizontal_bounds) > 0:
                    if len(horizontal_bounds) == 1:
                        x_val = horizontal_bounds[0]
                        if x_val <= abs(img.shape[1]-x_val):
                            img = img[:,x_val+1:]
                        else:
                            img = img[:,:x_val+1]
                    else:
                        left_bound = horizontal_bounds[0]+1
                        right_bound = min(horizontal_bounds[len(horizontal_bounds)-1]+1, img.shape[1])
                        if img[ :,:left_bound].size != 0 and np.amax (img[ :,:left_bound]) > 0:
                            left_bound = 0
                        if img[ : , right_bound:].size != 0 and np.amax (img[ : , right_bound:]) > 0:
                            right_bound = img.shape[1]     
                        img = img[:,left_bound:right_bound]
                if len(vert_bounds) > 0:
                    if len(vert_bounds) == 1:
                        y_val = vert_bounds[0]
                        if abs(y_val) < abs(img.shape[0]-y_val):
                            img = img[y_val:,:]
                        else:
                            img = img[:y_val,:]
                    else:
                        top_bound = vert_bounds[0]+1
                        bot_bound = min(vert_bounds[len(vert_bounds)-1]+1,img.shape[0])
                        if img[ :vert_bounds[0] , :].size != 0 and np.amax(img[ :vert_bounds[0] , :]) > 0:
                            top_bound = 0
                        if img[ bot_bound: , :].size != 0 and np.amax(img[ bot_bound: , :]) > 0:
                            bot_bound = img.shape[0]                        
                        img = img[top_bound:bot_bound,:]

                if img.size == 0:
                    display(img)
                img = resize_img(img)
                kernel = np.ones((3,3),np.uint8)/9
                img = cv2.filter2D(img,-1,kernel)
                img = img.astype(np.uint8)


                kp1,des1 = sift.detectAndCompute(img,None)
                patches = []
                for i in range(len(kp1)):
                    pt = kp1[i].pt
                    pt = (int(pt[0]), int(pt[1]))
                    if len(patches) > 0:
                        closest = sorted(patches, key = lambda x: np.linalg.norm(np.asarray(pt)-(np.asarray(x[0]))))[0][0]
                        if np.linalg.norm(np.asarray(closest) - np.asarray(pt)) < 5:
                            continue
                    size = np.random.randint(40,64)
                    Xstart = max(pt[1]-size,0)
                    Xend = min(127,pt[1]+size)
                    Ystart = max(pt[0]-size,0)
                    Yend = min(127,pt[0]+size)
                    patches.append(   (pt,img[Xstart:Xend,Ystart:Yend])    )
                    if len(patches) > 40:
                        break
                # patches = [ ((0,0),np.copy(img))] + patches
                maxVSum = 0
                maxVs= []
                for _, patch in patches:
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
                if len(patches) == 0 :
                    display(img)
                    continue
                maxVs = sorted(maxVs, key = lambda x: -x)
                maxLens = 0
                for maxi in maxVs:
                    maxVSum+= maxi
                    maxLens+=1
                    if maxLens > 7:
                        break

                currentMatchVal = maxVSum/maxLens
                if currentMatchVal > bestMatchVal:
                    bestMatchVal = currentMatchVal
                    pastMatches = [img] + pastMatches
                    bestGardiner = gardiner
                    bestMatch = img
                    matchSquare =squared

            # display(bestMatch)
            # display(glyph.image)
            entryMatches.append((bestGardiner,glyph))
            entryGardiners.append(bestGardiner)
            # for w in pastMatches[:4]:
            #     display(w)
        matches.append((entryGardiners,entryMatches))

    return getAccuracy(allEntries,matches)
