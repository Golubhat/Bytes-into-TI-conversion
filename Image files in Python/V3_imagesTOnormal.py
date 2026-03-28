import cv2
import numpy as np
import os

# --- CONFIG ---
width, height = 1800, 1800
label_size = 10

output_file = input("Enter output file name: ")

data_chunks = {}
file_size = None
num_images = None

# --- MASK ---
mask = np.ones((height, width), dtype=bool)
mask[0:label_size, 0:label_size] = False
mask_flat = mask.flatten()

# --- READ IMAGES ---
files = [f for f in os.listdir() if f.endswith(".png")]

for file in files:
    image = cv2.imread(file)

    if image is None:
        continue

    # --- HEADER ---
    header_bytes = image[0, 0:8, 0]
    header = bytes(header_bytes)

    k = int.from_bytes(header[0:2], 'big')
    total = int.from_bytes(header[2:4], 'big')
    fsize = int.from_bytes(header[4:8], 'big')

    if file_size is None:
        file_size = fsize
        num_images = total

    flat = image.reshape((-1, 3))
    valid_pixels = flat[mask_flat]

    data_chunks[k] = valid_pixels.flatten()

# --- REBUILD ---
data = bytearray()
for k in range(1, num_images + 1):
    if k not in data_chunks:
        print(f"❌ Missing chunk {k}")
        break
    data.extend(data_chunks[k])

data = data[:file_size]

with open(output_file, "wb") as f:
    f.write(data)

print("\n✅ Reconstruction complete!")