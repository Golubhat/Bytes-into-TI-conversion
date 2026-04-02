import cv2
import numpy as np

width, height = 1800, 1800

# Encode: File to PNG images
def file_to_images():
    fileName = input("Enter file name for input: ")

    with open(fileName, "rb") as file:
        data = file.read()

    total_bytes = len(data)
    pixels_per_image = width * height * 3
    no_of_images = int(np.ceil(total_bytes / pixels_per_image))

    count = 0

    for k in range(1, no_of_images + 1):
        image = np.zeros((height, width, 3), np.uint8)

        for i in range(height):
            for j in range(width):
                if count < total_bytes:
                    image[i][j][0] = data[count]
                    count += 1
                else:
                    break

                if count < total_bytes:
                    image[i][j][1] = data[count]
                    count += 1
                else:
                    break

                if count < total_bytes:
                    image[i][j][2] = data[count]
                    count += 1
                else:
                    break
            if count >= total_bytes:
                break

        cv2.imwrite(f"{k}.png", image)

    print(f"Done! Images created: {no_of_images}")


# Decode: PNG images to File
def images_to_file():
    fileName = input("Enter file name for output: ")
    sizeOfFile = int(input("Enter size of output file (in bytes): "))

    pixels_per_image = width * height * 3
    no_of_images = int(np.ceil(sizeOfFile / pixels_per_image))

    count = 0

    with open(fileName, "wb") as file:

        for k in range(1, no_of_images + 1):
            image = cv2.imread(f"{k}.png")

            for i in range(height):
                for j in range(width):

                    if count < sizeOfFile:
                        file.write(bytes([image[i][j][0]]))
                        count += 1
                    else:
                        return

                    if count < sizeOfFile:
                        file.write(bytes([image[i][j][1]]))
                        count += 1
                    else:
                        return

                    if count < sizeOfFile:
                        file.write(bytes([image[i][j][2]]))
                        count += 1
                    else:
                        return

    print("Done!")


# Main menu
def main():
    print("1. Normal file bytes into image files")
    print("2. Image files into normal file bytes")

    choice = int(input("Enter your choice: "))

    if choice == 1:
        file_to_images()
    elif choice == 2:
        images_to_file()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
