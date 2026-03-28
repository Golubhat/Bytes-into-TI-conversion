import cv2
import numpy as np
width, height = 1800, 1800

data = bytearray()
fileName = input("Enter file name for input: ")
with open(fileName, "rb") as file:
    data = file.read()

no_of_images = int(np.ceil(len(data)/(width*height*3)))
count = 0

for k in range(1, no_of_images):
    image = np.zeros((height, width, 3), np.uint8)
    for i in range(height):
        for j in range(width):
            image[i][j][0] = data[count]
            image[i][j][1] = data[count+1]
            image[i][j][2] = data[count+2]
            count += 3
    cv2.imwrite(str(k)+'.png', image)

done = False
image = np.zeros((height, width, 3), np.uint8)
for i in range(height):
    for j in range(width):
        if count < len(data):
            image[i][j][0] = data[count]
        else:
            done = True
            break
        if count+1 < len(data):
            image[i][j][1] = data[count+1]
        else:
            done = True
            break
        if count+2 < len(data):
            image[i][j][2] = data[count+2]
        else:
            done = True
            break
        count += 3
    if done:
        break

cv2.imwrite(str(no_of_images)+'.png', image)
