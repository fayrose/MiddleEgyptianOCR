import numpy as np
from BoundaryCreator import create_boundaries
from Models.VerticalSlice import VerticalSlice

class Block:
    def __init__(self, left_boundary, right_boundary, image):
        self.left_bound = left_boundary
        self.right_bound = right_boundary
        self.image = np.copy(image[:, self.left_bound : self.right_bound+2])
        self.verticals = []

    def split_into_verticals(self):
        bounds = create_boundaries(self.image, vertical=True)
        for i in range(0, len(bounds), 2):
            sliced = VerticalSlice(bounds[i], bounds[i + 1], self, self.image)
            sliced.split_slice_into_glyphs()
            self.verticals.append(sliced)
