class Character:
    def __init__(self, leftBound, rightBound, image):
      self.left = leftBound
      self.right = rightBound
      self.image = image[:,self.left:self.right]
      self.width = self.right - self.left