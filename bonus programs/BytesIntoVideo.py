import cv2
import numpy as np

# --- CONFIG ---
WIDTH, HEIGHT = 1920, 1080
BLOCK_W, BLOCK_H = 48, 27
FPS = 60

COLS = WIDTH // BLOCK_W
ROWS = HEIGHT // BLOCK_H
BLOCKS_PER_FRAME = COLS * ROWS
BYTES_PER_FRAME = BLOCKS_PER_FRAME // 3

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

colors_np = np.array(colors, dtype=np.float32)


# --- BASE-7 HELPERS ---
def byte_to_base7(byte):
    return [
        byte // 49,
        (byte % 49) // 7,
        byte % 7
    ]


def base7_to_byte(d1, d2, d3):
    return d1 * 49 + d2 * 7 + d3


def get_digit_from_color(block):
    avg_color = block.mean(axis=(0, 1)).astype(np.float32)
    distances = np.sum(np.abs(colors_np - avg_color), axis=1)
    return int(np.argmin(distances))


# --- ENCODE: FILE → VIDEO ---
def file_to_video():
    fileName = input("Enter file name: ")

    with open(fileName, "rb") as f:
        data = f.read()

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

        for _ in range(BYTES_PER_FRAME):
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


# --- DECODE: VIDEO → FILE ---
def video_to_file():
    video_path = input("Enter video file: ")
    output_file = input("Enter output file: ")

    cap = cv2.VideoCapture(video_path)
    decoded_bytes = bytearray()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        block_digits = []

        for row in range(ROWS):
            for col in range(COLS):
                y1 = row * BLOCK_H
                y2 = y1 + BLOCK_H
                x1 = col * BLOCK_W
                x2 = x1 + BLOCK_W

                block = frame[y1:y2, x1:x2]
                digit = get_digit_from_color(block)
                block_digits.append(digit)

        for i in range(0, len(block_digits) - 2, 3):
            d1, d2, d3 = block_digits[i], block_digits[i+1], block_digits[i+2]
            decoded_bytes.append(base7_to_byte(d1, d2, d3))

    cap.release()

    with open(output_file, "wb") as f:
        f.write(decoded_bytes)

    print("Decoding complete.")
    print("Saved as:", output_file)


# --- MAIN MENU ---
def main():
    print("1. File → Video")
    print("2. Video → File")

    choice = int(input("Enter your choice: "))

    if choice == 1:
        file_to_video()
    elif choice == 2:
        video_to_file()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
