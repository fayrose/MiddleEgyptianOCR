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
        if len(vertBounds) == 0:
          upper = 0
          lower = self.image.shape[0]-1
        elif len(vertBounds) == 1:
          if abs(vertBounds[0]) < abs(self.image.shape[0]-vertBounds):
            upper = vertBounds[0]
            lower = self.image.shape[0]-1
          else:
            upper = 0
            lower = vertBounds[0]
        else:
          upper = vertBounds[0]
          lower = vertBounds[1]+1
        character = Character(self.left, self.upper, upper,lower,bounds[i],bounds[i+1],self.image)
        # display(character.image)
        self.characters.append(character)
      return self.characters

