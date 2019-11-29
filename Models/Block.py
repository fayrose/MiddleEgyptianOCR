import numpy as np
from BoundaryCreator import create_boundaries
from Models.VerticalSlice import VerticalSlice

class Block:
    def __init__(self, left_boundary, right_boundary, image):
        self.left_bound = left_boundary
        self.right_bound = right_boundary
        self.image = np.copy(image[:, self.left_bound : self.right_bound+2])
        self.verticals = []

    def split_into_verticals(self, allChars):
        bounds = create_boundaries(self.image, vertical=True)
        
        if len(bounds) %2 != 0 or len(bounds) == 0: #BUG LEN OF 1 WHAT DO?
            sliced = VerticalSlice(0, self.image.shape[0]-1, self, self.image)
            characters = sliced.split_slice_into_glyphs()
            allChars += characters
            self.verticals.append(sliced)
        else:
            for i in range(0, len(bounds), 2):
                sliced = VerticalSlice(bounds[i], bounds[i + 1], self, self.image)
                characters = sliced.split_slice_into_glyphs()
                allChars += characters
                self.verticals.append(sliced)
