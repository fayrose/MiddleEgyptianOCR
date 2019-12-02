class Character:
    def __init__(self,xoffset, yoffset, upper, lower, leftBound, rightBound, image):
      self.xoffset = xoffset
      self.yoffset = yoffset
      self.upper = upper
      self.lower = lower
      self.left = leftBound
      self.right = rightBound
      self.image = image[upper:lower,self.left:self.right]
      self.width = self.right - self.left