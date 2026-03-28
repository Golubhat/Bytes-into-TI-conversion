import cv2
import numpy as np

width, height = 1800, 1800

fileName = input("Enter output file name (e.g., output.bin): ")
num_images = int(input("Enter number of images: "))

count = 0
data = bytearray()

# Loop through each image and extract pixels
for k in range(1, num_images + 1):
    image_path = f"{k}.png"
    image = cv2.imread(image_path)

    if image is None:
        print(f"⚠️ Warning: Could not read {image_path}, skipping.")
        continue

    # Flatten image pixels in BGR order
    b, g, r = cv2.split(image)
    flat = np.stack((b, g, r), axis=-1).flatten()
    data.extend(flat)

# Write all collected bytes to output file
with open(fileName, "wb") as file:
    file.write(data)

print(f"✅ Reconstruction complete! Total bytes written: {len(data)}")
