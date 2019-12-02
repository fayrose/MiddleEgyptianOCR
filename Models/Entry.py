import cv2               as cv
import matplotlib.pyplot as plt
import numpy             as np
import SpecialGlyphs

from scipy                 import ndimage
from BoundaryCreator       import create_boundaries
from Models.Block          import Block
from Models.Glyph          import Glyph
from Services.Display      import display
from Services.ImageResizer import resize_img

class Entry:
    def __init__(self, filename):
        image = cv.imread(filename)
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY) / 255.0
        image = 1 - image
        self.filename = filename
        self.image = image
        self.blocks = []
        self.characters = []
        self.gardiners = []
        self.glyphs = []

    def process_image(self):
        # display(self.image)
        self.split_into_words()
        try:
            self.split_blocks_into_verticals()
        except: return
        for i in range(len(self.glyphs)):
            self.glyphs[i].image = resize_img(self.glyphs[i].image)

    #look for up/down gaps and split words
    def split_into_words(self):
        boundaries = create_boundaries(self.image)
        for i in range(0, len(boundaries) - 1, 2):
            self.blocks.append(Block(boundaries[i], boundaries[i + 1], self.image))
        # display(self.image,boundaries)

    def checkgrouping(self,char,groupings):
        for i in range(len(groupings)):
            if len(groupings[i]) == 3:
                continue
            sample = groupings[i][0]
            lastInGroup = groupings[i][len(groupings[i])-1]
            hori = True
            vert = True
            if abs ( (lastInGroup.right + lastInGroup.xoffset) - (char.left + char.xoffset)) >= 200:
                hori = False
            if abs(char.upper - sample.upper) > 2:
                hori = False
            if abs(char.lower - sample.lower) > 2:
                hori = False
            if abs(char.width - sample.width) > 7:
                hori = False
                vert = False
            if abs((char.lower - char.upper) - (sample.lower- sample.upper)) > 5:
                vert = False
                hori = False
            if abs((char.left + char.xoffset) - (sample.left + sample.xoffset)) > 2:
                vert = False
            if abs((char.right + char.xoffset) - (sample.right + sample.xoffset)) > 2:
                vert = False
            if hori or vert:
                groupings[i].append(char)
                return True

        return False

    
    def isHori(self,grouping):
        if len(grouping) <= 1:
            return True
        s1 = grouping[0]
        s2 = grouping[1]
        if abs(s1.upper-s2.upper) < 3:
            return True
        else:
            return False

    def groupHori(self,group):
        if type(group[0]) is Glyph:
            group = sorted(group, key = lambda g: g.left)
            left = group[0].left
            right = group[-1].right
            upper = min(group, key = lambda char: char.upper)
            lower = max(group, key = lambda char: char.lower)
            upperVal = upper.upper
            lowerVal = lower.lower
        else:
            group = sorted(group, key = lambda g: g.left + g.xoffset)
            left = group[0].left + group[0].xoffset
            right = group[len(group)-1].right + group[len(group)-1].xoffset
            upper = min(group, key = lambda char: char.upper + char.yoffset)
            lower = max(group, key = lambda char: char.lower + char.yoffset)
            upperVal = upper.upper + upper.yoffset
            lowerVal = lower.lower + lower.yoffset
        glyph = Glyph(upperVal,lowerVal,left,right,self.image)
        return glyph

    def groupVert(self,group):
        group = sorted(group, key = lambda g: g.upper)
        if type(group[0]) is Glyph:
            leftChar = min(group, key = lambda char: char.left)
            left = leftChar.left
            rightChar = max(group, key = lambda char: char.right)
            right = rightChar.right
            upper = min(group, key = lambda char: char.upper)
            lower = max(group, key = lambda char: char.lower)
            upperVal = upper.upper
            lowerVal = lower.lower
        else:
            leftChar = min(group, key = lambda char: char.left + char.xoffset)
            left = leftChar.left + leftChar.xoffset
            rightChar = max(group, key = lambda char: char.right + char.xoffset)
            right = rightChar.right + rightChar.xoffset
            upper = min(group, key = lambda char: char.upper + char.yoffset)
            lower = max(group, key = lambda char: char.lower + char.yoffset)
            upperVal = upper.upper + upper.yoffset
            lowerVal = lower.lower + lower.yoffset
        glyph = Glyph(upperVal,lowerVal,left,right,self.image)
        return glyph

    def solvePlugBug(self,group,groupings,i, inverted = False):
        for j in range(len(groupings)):
            if j == i:
                continue
            if len(groupings[j]) != 1:
                continue
            leftPlug = group[0]
            rightPlug = group[1]
            bottomPlug = groupings[j][0]
            if leftPlug.left + leftPlug.xoffset <= bottomPlug.left + bottomPlug.xoffset and \
                rightPlug.left + rightPlug.xoffset >= bottomPlug.right + bottomPlug.xoffset and \
                abs(leftPlug.width - bottomPlug.width) < 5 and \
                (leftPlug.lower < bottomPlug.upper and not inverted or \
                leftPlug.lower > bottomPlug.upper and inverted):
                glyph = self.groupVert(group + [bottomPlug])
                self.glyphs.append(glyph)
                groupings[j] = []
                # display(glyph.image)
                return
                #its a plug
        #incorrect 2 grouping, add them as sepeeratre glyphs.
        for char in group:
            self.glyphs.append(Glyph(char.upper + char.yoffset,char.lower + char.yoffset,char.left + char.xoffset,char.right + char.xoffset,self.image))

    def solveHotdogs(self,groupings,hotdog):
        while hotdog > 0:
            best = None
            bestDistance = 100000
            for i in range(len(groupings)):
                triple = groupings[i]
                if len(triple) < 3:
                    break
                #Ignore vertical triples
                if abs((triple[0].upper + triple[0].yoffset) - (triple[1].upper + triple[1].yoffset)) > 2:
                    continue
                for j in range(i+1,len(groupings)):
                    single = groupings[j]
                    if len(single) > 1:
                        continue
                    distance = (triple[0].upper + triple[0].yoffset) - (single[0].lower + single[0].yoffset)
                    if distance < 0:
                        continue
                    if distance < bestDistance:
                        best = (triple,single)
            if best == None:
                print("COULD NOT FIND ANYTHING WTF")
                return
            tripleHotdog = best[0] + best[1]
            glyph = self.groupVert(tripleHotdog)
            # display(glyph.image)
            self.glyphs.append(glyph)
            groupings.remove(best[0])
            groupings.remove(best[1])

            hotdog -= 1

    #Do a width test to find the best triuple and keep the one with the least variance
    def isBestTriple(self, group,groupings):
        bestGroup = group
        bestWidth =  abs(bestGroup[0].width - bestGroup[1].width) + abs(bestGroup[0].width-bestGroup[2].width)
        for testGroup in groupings:
            if len(testGroup) != 3:
                continue
            widthDif = abs(testGroup[0].width - testGroup[1].width) + abs(testGroup[0].width-testGroup[2].width)
            if widthDif < bestWidth:
                return False
        return True

    #For each word above, look for left/right gaps, split word on them
    def split_blocks_into_verticals(self):
        if self.blocks is None:
            raise("This entry has no blocks. Please call split_into_words() first.")
        else:
            for block in self.blocks:
                block.split_into_verticals(self.characters)
        #chars are glpyhs, convert to Glyth objects
        if len(self.characters) == len(self.gardiners):
            for char in self.characters:
                self.glyphs.append(Glyph(char.upper + char.yoffset,char.lower + char.yoffset,char.left + char.xoffset,char.right + char.xoffset,self.image))
        else:
            if len(self.characters) > len(self.gardiners):
                groupings = []
                for char in self.characters:
                    if groupings == []:
                        groupings.append([char])
                    else:
                        match = self.checkgrouping(char,groupings)
                        if not match:
                            groupings.append([char])
                
                #process big groups first, we might use the 1 sized groups to complete bigger stuff
                groupings = sorted(groupings, key = lambda x: -len(x))
                #WE HAVE A TRIPLE THREAT
                hotdog = len(SpecialGlyphs.tripleHotDog.intersection(self.gardiners)) > 0
                if hotdog:
                    self.solveHotdogs(groupings,hotdog)


                for i in range(len(groupings)):
                    group = groupings[i]
                    if len(group) == 0:
                        continue
                    elif len(group) == 1:
                        char = group[0]
                        self.glyphs.append(Glyph(char.upper + char.yoffset,char.lower + char.yoffset,char.left + char.xoffset,char.right + char.xoffset,self.image))
                        continue
                    elif len(group) == 2:
                        plugbug = len(SpecialGlyphs.electricPlug.intersection(self.gardiners)) > 0
                        if plugbug:
                            self.solvePlugBug(group,groupings,i)
                            continue
                        invertedPlug = len(SpecialGlyphs.invertedPlug.intersection(self.gardiners)) > 0
                        if invertedPlug:
                            self.solvePlugBug(group,groupings,i,True)
                            continue
                        for char in group:
                            self.glyphs.append(Glyph(char.upper + char.yoffset,char.lower + char.yoffset,char.left + char.xoffset,char.right + char.xoffset,self.image))
                        continue
                    elif len(group) != 3:
                        continue

                    tripleThreats = len(SpecialGlyphs.tripleThreats.intersection(self.gardiners))
                    if tripleThreats <= 0:
                        for char in group:
                            self.glyphs.append(Glyph(char.upper + char.yoffset,char.lower + char.yoffset,char.left + char.xoffset,char.right + char.xoffset,self.image))
                        continue
                    tripleCount = 0
                    for q in range(len(groupings)):
                        if len(groupings[q])  == 3:
                            tripleCount += 1
                    #There are false positives..!
                    if tripleThreats < tripleCount:
                        if not self.isBestTriple(group,groupings):
                            for char in group:
                                self.glyphs.append(Glyph(char.upper + char.yoffset,char.lower + char.yoffset,char.left + char.xoffset,char.right + char.xoffset,self.image))
                            continue
                    if self.isHori(group):
                        glyph = self.groupHori(group)
                    else:
                        glyph = self.groupVert(group)
                    # display(glyph.image)
                    self.glyphs.append(glyph)
                    # display(self.image)

                # for glyph in self.glyphs:
                #     display(glyph.image)

                #print(len(groupings))
                    # display(char.image)