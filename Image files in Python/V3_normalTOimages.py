import cv2
import numpy as np
import math

# --- CONFIG ---
width, height = 1800, 1800
label_size = 10

total_pixels = width * height
label_pixels = label_size * label_size
usable_pixels = total_pixels - label_pixels

pixels_per_image = usable_pixels * 3

# --- INPUT ---
fileName = input("Enter file name for input: ")

with open(fileName, "rb") as file:
    data = np.frombuffer(file.read(), dtype=np.uint8)

file_size = len(data)

if file_size > 0xFFFFFFFF:
    raise ValueError("File too large for 4-byte size limit!")
# 0xFFFFFFFF = 2^32 - 1

num_images = math.ceil(file_size / pixels_per_image)

if num_images > 0xFFFF:
    raise ValueError("Too many images for 2-byte limit!")
# 0xFFFF = 2^16 - 1

print(f"Generating {num_images} images...")

# --- MASK ---
mask = np.ones((height, width), dtype=bool)
mask[0:label_size, 0:label_size] = False
mask_flat = mask.flatten()

# --- PROCESS ---
for k in range(1, num_images + 1):
    start = (k - 1) * pixels_per_image
    end = min(k * pixels_per_image, file_size)
    chunk = data[start:end]

    if len(chunk) < pixels_per_image:
        chunk = np.pad(chunk, (0, pixels_per_image - len(chunk)), 'constant')

    chunk_pixels = chunk.reshape((-1, 3))

    image = np.zeros((height * width, 3), dtype=np.uint8)
    image[mask_flat] = chunk_pixels
    image = image.reshape((height, width, 3))

    # --- HEADER (8 bytes) ---
    header = (
        k.to_bytes(2, 'big') +
        num_images.to_bytes(2, 'big') +
        file_size.to_bytes(4, 'big')
    )

    header_array = np.frombuffer(header, dtype=np.uint8)

    # Store header in label area (blue channel)
    image[0, 0:8, 0] = header_array

    cv2.imwrite(f"{k}.png", image)

print("\n✅ Encoding complete!")