import cv2
import numpy as np
import math
import os

# --- CONFIG ---
width, height = 1800, 1800
label_size = 10

total_pixels = width * height
label_pixels = label_size * label_size
usable_pixels = total_pixels - label_pixels
pixels_per_image = usable_pixels * 3


# --- MASK (shared) ---
def get_mask():
    mask = np.ones((height, width), dtype=bool)
    mask[0:label_size, 0:label_size] = False
    return mask.flatten()


# --- ENCODE ---
def file_to_images():
    fileName = input("Enter file name for input: ")

    with open(fileName, "rb") as file:
        data = np.frombuffer(file.read(), dtype=np.uint8)

    file_size = len(data)

    if file_size > 0xFFFFFFFF:
        raise ValueError("File too large for 4-byte size limit!")

    num_images = math.ceil(file_size / pixels_per_image)

    if num_images > 0xFFFF:
        raise ValueError("Too many images!")

    print(f"Generating {num_images} images...")

    mask_flat = get_mask()

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

        # --- HEADER ---
        header = (
            k.to_bytes(2, 'big') +
            num_images.to_bytes(2, 'big') +
            file_size.to_bytes(4, 'big')
        )

        header_array = np.frombuffer(header, dtype=np.uint8)

        # Store header in label area (blue channel)
        image[0, 0:8, 0] = header_array

        cv2.imwrite(f"{k}.png", image)

    print(f"Done! Images created: {num_images}")


# --- DECODE ---
def images_to_file():
    output_file = input("Enter output file name: ")

    mask_flat = get_mask()

    data_chunks = {}
    file_size = None
    num_images = None

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
            print(f"Missing chunk {k}")
            return
        data.extend(data_chunks[k])

    data = data[:file_size]

    with open(output_file, "wb") as f:
        f.write(data)

    print("Done!")


# --- MAIN MENU ---
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
