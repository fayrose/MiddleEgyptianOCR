import os
import random
import json
import matplotlib.pyplot as plt
import cv2
import numpy as np

#Question 4 Part a)
def myCorrelation(image,f,mode):
  #Image Dimensions
  x = image.shape[0]
  y = image.shape[1]
  # Filter Dimensions
  fr = f.shape[0]
  fc = f.shape[1]
  kr = int((fr-1)/2)
  kc = int((fc-1)/2)

  
  #Setup appropriate bounds for loops and output based on mode
  if mode == "full":
    xs = 0 - kr #X Start
    xe = x + kr #X end
    ys = 0 - kc #Y Start
    ye = y + kc #Y End
    out = np.zeros([image.shape[0] + 2*k,image.shape[1] + 2*k])
  elif mode == "same":
    xs = 0 #X Start
    xe = x #X end
    ys = 0 #Y Start
    ye = y #Y End
    out = np.zeros(image.shape)
  elif mode == "valid":
    xs = 0+kr #X Start
    xe = x-kr #X end
    ys = 0+kc #Y Start
    ye = y-kc #Y End
    out = np.zeros([image.shape[0] - 2*k,image.shape[1] - 2*k])
  else:
    print("Invalid mode, Returning Early")
    return
  
  #Initialize a output array the size of the input
  
  xo = 0
  yo = 0
  for i in range(xs,xe,1):
    yo = 0
    for j in range(ys,ye,1):
      for u in range(-kr,kr+1,1):
        if i+u < 0 or i+u >= x:
          continue 
        for v in range(-kc,kc+1,1):
          if j+v < 0 or j+v >= y:
            continue
          v = np.add(out[xo][yo], np.dot(f[(kr-1)+u][(kc-1)+v],image[i+u][j+v]))
          out[xo][yo] = v
      yo+=1
    xo+=1
  return out