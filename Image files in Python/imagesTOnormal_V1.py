import cv2
import numpy as np
width, height = 1800, 1800

fileName = input("Enter file name for output: ")
sizeOfFile = int(input("Enter size of output: "))
no_of_images = int(np.ceil(sizeOfFile/(width*height*3)))
count = 0

with open(fileName, "wb") as file:

    for k in range(1, no_of_images):
        image = cv2.imread(str(k)+'.png')
        for i in range(height):
            for j in range(width):
                file.write(image[i][j][0])
                file.write(image[i][j][1])
                file.write(image[i][j][2])
                count += 3

    done = False
    image = cv2.imread(str(no_of_images)+'.png')
    for i in range(0, height):
        for j in range(0, width):
            if count < sizeOfFile:
                file.write(image[i][j][0])
            else:
                done = True
                break
            if count+1 < sizeOfFile:
                file.write(image[i][j][1])
            else:
                done = True
                break
            if count+2 < sizeOfFile:
                file.write(image[i][j][2])
            else:
                done = True
                break
            count += 3
        if done:
            break
