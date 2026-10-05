import cv2
import numpy as np
import os
import time

# ============================================================
# CONFIG
# ============================================================

WIDTH, HEIGHT = 1920, 1080
BLOCK_W, BLOCK_H = 48, 27
FPS = 60

COLS = WIDTH // BLOCK_W
ROWS = HEIGHT // BLOCK_H

BLOCKS_PER_FRAME = COLS * ROWS
BYTES_PER_FRAME = BLOCKS_PER_FRAME // 3

# 7 colors (BGR)
COLORS = np.array([
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255)
], dtype=np.float32)


# ============================================================
# PROGRESS BAR
# ============================================================

def show_progress(current, total, prefix="Progress"):
    """Display a simple terminal progress bar."""

    if total <= 0:
        return

    percent = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)

    bar = "█" * filled + "░" * (bar_length - filled)

    print(
        f"\r{prefix}: |{bar}| "
        f"{percent:6.2f}% "
        f"({current}/{total})",
        end="",
        flush=True
    )

    if current >= total:
        print()


# ============================================================
# BASE-7 HELPERS
# ============================================================

def byte_to_base7(byte):
    return (
        byte // 49,
        (byte % 49) // 7,
        byte % 7
    )


def base7_to_byte(d1, d2, d3):
    return d1 * 49 + d2 * 7 + d3


# ============================================================
# ENCODE: FILE → VIDEO
# ============================================================

def file_to_video():
    file_name = input("Enter input file name: ").strip()
    output_video = input("Enter output video file name: ").strip()

    if not os.path.isfile(file_name):
        print("Error: Input file does not exist.")
        return

    if not output_video:
        print("Error: Output video file name cannot be empty.")
        return

    # Add .avi automatically if no extension is provided
    if not os.path.splitext(output_video)[1]:
        output_video += ".avi"

    file_size = os.path.getsize(file_name)

    if file_size == 0:
        print("Error: File is empty.")
        return

    total_frames = (
        file_size + BYTES_PER_FRAME - 1
    ) // BYTES_PER_FRAME

    print()
    print("========== FILE → VIDEO ==========")
    print(f"Input file       : {file_name}")
    print(f"Output video     : {output_video}")
    print(f"File size        : {file_size:,} bytes")
    print(f"Resolution       : {WIDTH}x{HEIGHT}")
    print(f"FPS              : {FPS}")
    print(f"Blocks/frame     : {BLOCKS_PER_FRAME:,}")
    print(f"Bytes/frame      : {BYTES_PER_FRAME:,}")
    print(f"Total frames     : {total_frames:,}")
    print()

    out = cv2.VideoWriter(
        output_video,
        cv2.VideoWriter_fourcc(*"XVID"),
        FPS,
        (WIDTH, HEIGHT)
    )

    if not out.isOpened():
        print("Error: Could not create output video.")
        return

    index = 0
    frame_number = 0

    start_time = time.time()

    with open(file_name, "rb") as f:

        while index < file_size:

            frame = np.zeros(
                (HEIGHT, WIDTH, 3),
                dtype=np.uint8
            )

            bytes_this_frame = min(
                BYTES_PER_FRAME,
                file_size - index
            )

            data = f.read(bytes_this_frame)

            digits = np.empty(
                bytes_this_frame * 3,
                dtype=np.uint8
            )

            for i, byte in enumerate(data):
                pos = i * 3

                digits[pos] = byte // 49
                digits[pos + 1] = (byte % 49) // 7
                digits[pos + 2] = byte % 7

            for block_idx, digit in enumerate(digits):

                row = block_idx // COLS
                col = block_idx % COLS

                y1 = row * BLOCK_H
                y2 = y1 + BLOCK_H

                x1 = col * BLOCK_W
                x2 = x1 + BLOCK_W

                frame[y1:y2, x1:x2] = COLORS[digit]

            out.write(frame)

            index += bytes_this_frame
            frame_number += 1

            show_progress(
                frame_number,
                total_frames,
                "Encoding"
            )

    out.release()

    elapsed = time.time() - start_time

    print()
    print("Video encoding complete.")
    print(f"Output video : {output_video}")
    print(f"Time         : {elapsed:.2f} seconds")
    print(f"Frames       : {frame_number:,}")

# ============================================================
# DECODE: VIDEO → FILE
# ============================================================

def video_to_file():

    video_path = input("Enter video file: ").strip()
    output_file = input("Enter output file: ").strip()

    if not os.path.isfile(video_path):
        print("Error: Video file does not exist.")
        return

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    video_width = int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    video_height = int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    print()
    print("========== VIDEO → FILE ==========")
    print(f"Input video      : {video_path}")
    print(f"Video resolution : {video_width}x{video_height}")
    print(f"Total frames     : {total_frames:,}")
    print()

    decoded_bytes = bytearray()

    frame_number = 0

    start_time = time.time()

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # Make sure frame is large enough
        if (
            frame.shape[1] < COLS * BLOCK_W
            or frame.shape[0] < ROWS * BLOCK_H
        ):
            print("\nError: Video resolution is too small.")
            cap.release()
            return

        # ----------------------------------------------------
        # Decode each block
        # ----------------------------------------------------

        block_digits = []

        for row in range(ROWS):

            y1 = row * BLOCK_H
            y2 = y1 + BLOCK_H

            for col in range(COLS):

                x1 = col * BLOCK_W
                x2 = x1 + BLOCK_W

                block = frame[y1:y2, x1:x2]

                # Average BGR color
                avg_color = block.mean(
                    axis=(0, 1)
                )

                # Find closest color
                distances = np.sum(
                    np.abs(COLORS - avg_color),
                    axis=1
                )

                digit = int(
                    np.argmin(distances)
                )

                block_digits.append(digit)

        # ----------------------------------------------------
        # Base-7 digits → bytes
        # ----------------------------------------------------

        for i in range(
            0,
            len(block_digits) - 2,
            3
        ):
            d1 = block_digits[i]
            d2 = block_digits[i + 1]
            d3 = block_digits[i + 2]

            decoded_bytes.append(
                d1 * 49 + d2 * 7 + d3
            )

        frame_number += 1

        show_progress(
            frame_number,
            total_frames,
            "Decoding"
        )

    cap.release()

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    with open(output_file, "wb") as f:
        f.write(decoded_bytes)

    elapsed = time.time() - start_time

    print()
    print("Decoding complete.")
    print(f"Saved as     : {output_file}")
    print(f"Output size  : {len(decoded_bytes):,} bytes")
    print(f"Time         : {elapsed:.2f} seconds")
    print(f"Frames       : {frame_number:,}")


# ============================================================
# MAIN MENU
# ============================================================

def main():

    print()
    print("===================================")
    print("       FILE ↔ VIDEO ENCODER")
    print("===================================")
    print()
    print("1. File → Video")
    print("2. Video → File")
    print()

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        file_to_video()

    elif choice == "2":
        video_to_file()

    else:
        print("Invalid choice!")


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    main()
