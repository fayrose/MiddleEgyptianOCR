import numpy as np
from BoundaryCreator import create_boundaries
from VerticalSlice import VerticalSlice

class Block:
    def __init__(self, left_boundary, right_boundary, image):
        self.left_bound = left_boundary
        self.right_bound = right_boundary
        self.image = np.copy(image[:, self.left_bound : self.right_bound])
        self.verticals = []

    def split_into_verticals(self):
        bounds = create_boundaries(self.image, vertical=True)
        for i in range(0, len(bounds), 2):
            sliced = VerticalSlice(bounds[i], bounds[i + 1], self, self.image)
            self.verticals.append(sliced)