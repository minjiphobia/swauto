#!/usr/bin/python3
import cv2 as cv
import numpy as np

im_screencap = cv.imread('screencap.png', 0)
im_pattern = cv.imread('tmp.png')

gray_pattern = cv.cvtColor(im_pattern, cv.COLOR_BGR2GRAY)

h, w = im_pattern.shape[0:2]
print(w, h)

res = cv.matchTemplate(im_screencap, gray_pattern, cv.TM_CCOEFF_NORMED)

print('res.shape:', res.shape)
threshold = 0.8

minval, max_val, min_loc, max_loc = cv.minMaxLoc(res)
print(cv.minMaxLoc(res))

print(max_loc[0]+w/2, max_loc[1]+h/2)
