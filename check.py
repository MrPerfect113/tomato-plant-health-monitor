import cv2
from detector import detect

img = cv2.imread("test.jpg")
print(detect(img))
