from BoundaryCreator import create_boundaries
import matplotlib.pyplot as plt
from Models.Character import Character

class VerticalSlice:
    def __init__(self, upper, lower, block, image):
      self.upper = upper
      self.lower = lower + 2
      self.left = block.left_bound
      self.right = block.right_bound + 2
      self.image = image[self.upper:self.lower, :]
      self.width = self.right - self.left
      self.characters = []


    def split_slice_into_glyphs(self):
      bounds = create_boundaries(self.image)
      for i in range(0, len(bounds) - 1, 2):
        character = Character(bounds[i],bounds[i+1],self.image)
        # display(character.image)
        self.characters.append(character)

