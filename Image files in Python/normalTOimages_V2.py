import cv2
import numpy as np
import math

# --- CONFIG ---
width, height = 1800, 1800
pixels_per_image = width * height * 3  # 3 bytes per pixel (BGR)
# 1800x1800x3 = 9,720,000 bytes per image

# --- INPUT ---
fileName = input("Enter file name for input: ")

with open(fileName, "rb") as file:
    data = np.frombuffer(file.read(), dtype=np.uint8)

file_size = len(data)
num_images = math.ceil(file_size / pixels_per_image)

print(f"Total file size: {file_size} bytes")
print(f"Will generate {num_images} image(s) of {width}x{height}")

# --- PROCESSING ---
for k in range(1, num_images + 1):
    start = (k - 1) * pixels_per_image
    end = min(k * pixels_per_image, file_size)
    chunk = data[start:end]

    # If chunk not full, pad with zeros to fit image size
    if len(chunk) < pixels_per_image:
        chunk = np.pad(chunk, (0, pixels_per_image - len(chunk)), 'constant')

    # Reshape to (height, width, 3)
    image = chunk.reshape((height, width, 3))
    cv2.imwrite(f"{k}.png", image)

print("\n✅ Conversion complete!")
print(f"Generated {num_images} images total.")
