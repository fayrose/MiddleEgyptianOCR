from BoundaryCreator import create_boundaries
import matplotlib.pyplot as plt
from Models.Character import Character
from Services.Display import display
class VerticalSlice:
    def __init__(self, upper, lower, block, image):
      self.upper = upper
      self.lower = lower + 2
      self.left = block.left_bound # This is xOffset?
      self.right = block.right_bound + 2
      self.image = image[self.upper:self.lower, :]
      self.width = self.right - self.left
      self.characters = []


    def split_slice_into_glyphs(self):
      bounds = create_boundaries(self.image)
      # display(self.image,bounds)

      for i in range(0, len(bounds) - 1, 2):
        characterImage = self.image[:,bounds[i]:bounds[i+1]]
        vertBounds = create_boundaries(characterImage,True)
        character = Character(self.left, self.upper, vertBounds[0],vertBounds[1]+1,bounds[i],bounds[i+1],self.image)
        # display(character.image)
        self.characters.append(character)
      return self.characters

