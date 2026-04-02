import cv2
import numpy as np

# Video settings
WIDTH, HEIGHT = 1920, 1080
BLOCK_W, BLOCK_H = 48, 27

COLS = WIDTH // BLOCK_W   # 40
ROWS = HEIGHT // BLOCK_H  # 40
BLOCKS_PER_FRAME = COLS * ROWS  # 1600

# Same colors (BGR)
colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255)
]

# Convert colors to numpy for fast comparison
colors_np = np.array(colors)

def get_digit_from_color(block):
    avg_color = block.mean(axis=(0, 1)).astype(np.float32)
    palette = np.array(colors, dtype=np.float32)

    # Manhattan distance (robust + fast)
    distances = np.sum(np.abs(palette - avg_color), axis=1)

    return int(np.argmin(distances))

def base7_to_byte(d1, d2, d3):
    return d1 * 49 + d2 * 7 + d3

# Open video
video_path = input("Enter video file: ")
cap = cv2.VideoCapture(video_path)

decoded_bytes = bytearray()

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    block_digits = []

    # Traverse blocks
    for row in range(ROWS):
        for col in range(COLS):
            y1 = row * BLOCK_H
            y2 = y1 + BLOCK_H
            x1 = col * BLOCK_W
            x2 = x1 + BLOCK_W

            block = frame[y1:y2, x1:x2]

            digit = get_digit_from_color(block)
            block_digits.append(digit)

    # Convert digits → bytes
    for i in range(0, len(block_digits) - 2, 3):
        d1, d2, d3 = block_digits[i], block_digits[i+1], block_digits[i+2]
        byte = base7_to_byte(d1, d2, d3)
        decoded_bytes.append(byte)

cap.release()

# Save output
output_file = input("Enter output file: ")
with open(output_file, "wb") as f:
    f.write(decoded_bytes)

print("Decoding complete.")
print("Saved as:", output_file)
