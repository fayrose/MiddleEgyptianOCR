class Glyph:
    def __init__(self, upper, lower, leftBound, rightBound, image):
      self.upper = upper
      self.lower = lower
      self.left = leftBound
      self.right = rightBound
      self.image = image[upper:lower,self.left:self.right]
      self.width = self.right - self.left