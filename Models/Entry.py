import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
from BoundaryCreator import create_boundaries
from Models.Block import Block

class Entry:
    def __init__(self, filename):
        image = cv.imread(filename)
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY) / 255.0
        image = 1 - image
        self.image = image
        self.blocks = []
        self.characters = []

    #look for up/down gaps and split words
    def split_into_words(self):
        boundaries = create_boundaries(self.image)
        for i in range(0, len(boundaries) - 1, 2):
            self.blocks.append(Block(boundaries[i], boundaries[i + 1], self.image))

    #For each word above, look for left/right gaps, split word on them
    def split_blocks_into_verticals(self):
        if self.blocks is None:
            raise("This entry has no blocks. Please call split_into_words() first.")
        else:
            for block in self.blocks:
                block.split_into_verticals()