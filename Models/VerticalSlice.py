class VerticalSlice:
    def __init__(self, upper, lower, block, image):
      self.upper = upper
      self.lower = lower + 2
      self.left = block.left_bound
      self.right = block.right_bound + 2
      self.image = image[self.upper:self.lower, :]
      self.width = self.right - self.left

    def split_slice_into_glyphs():
      pass