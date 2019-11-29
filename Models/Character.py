class Character:
    def __init__(self,xoffset, upper, lower, leftBound, rightBound, image):
      self.xoffset = xoffset
      self.yoffset = upper
      self.upper = upper
      self.lower = lower
      self.left = leftBound
      self.right = rightBound
      self.image = image[:,self.left:self.right]
      self.width = self.right - self.left