import cv2
import numpy as np

# Video settings
WIDTH, HEIGHT = 1920, 1080
BLOCK_W, BLOCK_H = 48, 27
FPS = 60

COLS = WIDTH // BLOCK_W   # 40
ROWS = HEIGHT // BLOCK_H  # 40
BLOCKS_PER_FRAME = COLS * ROWS  # 1600
BYTES_PER_FRAME = BLOCKS_PER_FRAME // 3  # 533

# 7 colors (BGR)
colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255)
]

def byte_to_base7(byte):
    return [
        byte // 49,
        (byte % 49) // 7,
        byte % 7
    ]

# Load file
fileName = input("Enter file name: ")
with open(fileName, "rb") as f:
    data = f.read()

# Video writer
out = cv2.VideoWriter(
    "output.avi",
    cv2.VideoWriter_fourcc(*'XVID'),
    FPS,
    (WIDTH, HEIGHT)
)

index = 0

while index < len(data):
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    block_idx = 0

    for i in range(BYTES_PER_FRAME):
        if index >= len(data):
            break

        digits = byte_to_base7(data[index])
        index += 1

        for d in digits:
            row = block_idx // COLS
            col = block_idx % COLS

            y1 = row * BLOCK_H
            y2 = y1 + BLOCK_H
            x1 = col * BLOCK_W
            x2 = x1 + BLOCK_W

            frame[y1:y2, x1:x2] = colors[d]

            block_idx += 1

    out.write(frame)

out.release()
print("Video encoding complete.")
