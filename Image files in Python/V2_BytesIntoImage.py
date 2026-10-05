import cv2
import numpy as np
import os
import struct


# ============================================================
# CONFIGURATION
# ============================================================

WIDTH = 1800
HEIGHT = 1800

LABEL_SIZE = 10

TOTAL_PIXELS = WIDTH * HEIGHT
LABEL_PIXELS = LABEL_SIZE * LABEL_SIZE

USABLE_PIXELS = TOTAL_PIXELS - LABEL_PIXELS

# 3 bytes per RGB pixel
BYTES_PER_IMAGE = USABLE_PIXELS * 3


# ============================================================
# HEADER
#
# 0-3   : image number       uint32
# 4-7   : total images       uint32
# 8-15  : original file size uint64
#
# Total = 16 bytes
# ============================================================

HEADER_SIZE = 16

MAX_UINT32 = 0xFFFFFFFF
MAX_UINT64 = 0xFFFFFFFFFFFFFFFF


# ============================================================
# MASK
# ============================================================

def get_mask():

    mask = np.ones(
        (HEIGHT, WIDTH),
        dtype=bool
    )

    # Reserve 10 × 10 pixels
    mask[
        0:LABEL_SIZE,
        0:LABEL_SIZE
    ] = False

    return mask.flatten()


# ============================================================
# CREATE HEADER
# ============================================================

def create_header(
    image_number,
    total_images,
    file_size
):

    if image_number > MAX_UINT32:
        raise ValueError(
            "Image number exceeds uint32 limit."
        )

    if total_images > MAX_UINT32:
        raise ValueError(
            "Total image count exceeds uint32 limit."
        )

    if file_size > MAX_UINT64:
        raise ValueError(
            "File size exceeds uint64 limit."
        )

    return struct.pack(
        ">IIQ",
        image_number,
        total_images,
        file_size
    )


# ============================================================
# READ HEADER
# ============================================================

def read_header(image):

    # Flatten RGB image
    pixels = image.reshape(
        (-1, 3)
    )

    # First 16 pixels, red channel
    header = pixels[
        :HEADER_SIZE,
        0
    ].tobytes()

    if len(header) != HEADER_SIZE:
        raise ValueError(
            "Invalid header."
        )

    return struct.unpack(
        ">IIQ",
        header
    )


# ============================================================
# ENCODE
# ============================================================

def file_to_images():

    file_name = input(
        "\nEnter file name for input: "
    ).strip()

    if not os.path.isfile(file_name):

        print(
            "File not found!"
        )

        return


    # --------------------------------------------------------
    # Get file size
    # --------------------------------------------------------

    file_size = os.path.getsize(
        file_name
    )


    # --------------------------------------------------------
    # Calculate image count
    # --------------------------------------------------------

    if file_size == 0:

        num_images = 0

    else:

        num_images = (
            file_size +
            BYTES_PER_IMAGE -
            1
        ) // BYTES_PER_IMAGE


    if num_images > MAX_UINT32:

        print(
            "Too many images!"
        )

        return


    print()
    print("=" * 60)
    print("                     ENCODING")
    print("=" * 60)

    print(
        f"Input file      : {file_name}"
    )

    print(
        f"File size       : {file_size:,} bytes"
    )

    print(
        f"Bytes/image     : {BYTES_PER_IMAGE:,}"
    )

    print(
        f"Images required : {num_images:,}"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # Create mask once
    # --------------------------------------------------------

    mask_flat = get_mask()


    # --------------------------------------------------------
    # Reusable image buffer
    #
    # Shape:
    #     (1800 × 1800, 3)
    # --------------------------------------------------------

    image = np.zeros(
        (
            TOTAL_PIXELS,
            3
        ),
        dtype=np.uint8
    )


    # --------------------------------------------------------
    # Process file in chunks
    # --------------------------------------------------------

    with open(
        file_name,
        "rb"
    ) as file:

        for k in range(
            1,
            num_images + 1
        ):

            # ------------------------------------------------
            # Read chunk
            # ------------------------------------------------

            chunk = file.read(
                BYTES_PER_IMAGE
            )


            if not chunk:

                break


            chunk_array = np.frombuffer(
                chunk,
                dtype=np.uint8
            )


            # ------------------------------------------------
            # Clear image
            # ------------------------------------------------

            image.fill(0)


            # ------------------------------------------------
            # Pad final chunk
            # ------------------------------------------------

            if (
                len(chunk_array)
                < BYTES_PER_IMAGE
            ):

                padded = np.zeros(
                    BYTES_PER_IMAGE,
                    dtype=np.uint8
                )

                padded[
                    :len(chunk_array)
                ] = chunk_array

                chunk_array = padded


            # ------------------------------------------------
            # Convert bytes to RGB pixels
            # ------------------------------------------------

            chunk_pixels = chunk_array.reshape(
                (-1, 3)
            )


            # ------------------------------------------------
            # Put data into usable pixels
            # ------------------------------------------------

            image[
                mask_flat
            ] = chunk_pixels


            # ------------------------------------------------
            # Create header
            # ------------------------------------------------

            header = create_header(
                k,
                num_images,
                file_size
            )


            header_array = np.frombuffer(
                header,
                dtype=np.uint8
            )


            # ------------------------------------------------
            # Store header
            #
            # First 16 pixels
            # Red channel
            # ------------------------------------------------

            image[
                :HEADER_SIZE,
                0
            ] = header_array


            # ------------------------------------------------
            # Convert to 1800 × 1800 RGB
            # ------------------------------------------------

            output_image = image.reshape(
                (
                    HEIGHT,
                    WIDTH,
                    3
                )
            )


            # ------------------------------------------------
            # Write PNG
            # ------------------------------------------------

            output_name = (
                f"{k}.png"
            )


            success = cv2.imwrite(
                output_name,
                output_image
            )


            if not success:

                print(
                    f"\nFailed to write "
                    f"{output_name}"
                )

                return


            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            print(
                f"\rCreated "
                f"{k:,} / "
                f"{num_images:,}",
                end="",
                flush=True
            )


    print()
    print()
    print("=" * 60)
    print("                     COMPLETE")
    print("=" * 60)

    print(
        f"Images created : {num_images:,}"
    )

    print("=" * 60)


# ============================================================
# DECODE
# ============================================================

def images_to_file():

    output_file = input(
        "\nEnter output file name: "
    ).strip()


    # --------------------------------------------------------
    # Check first PNG
    # --------------------------------------------------------

    first_file = "1.png"


    if not os.path.exists(
        first_file
    ):

        print(
            "1.png was not found!"
        )

        return


    # --------------------------------------------------------
    # Read first PNG
    # --------------------------------------------------------

    image = cv2.imread(
        first_file,
        cv2.IMREAD_COLOR
    )


    if image is None:

        print(
            "Unable to read 1.png"
        )

        return


    # --------------------------------------------------------
    # Check dimensions
    # --------------------------------------------------------

    if (
        image.shape[1] != WIDTH or
        image.shape[0] != HEIGHT
    ):

        print(
            "Invalid image dimensions!"
        )

        print(
            f"Expected: "
            f"{WIDTH} x {HEIGHT}"
        )

        print(
            f"Found: "
            f"{image.shape[1]} x "
            f"{image.shape[0]}"
        )

        return


    # --------------------------------------------------------
    # Read first header
    # --------------------------------------------------------

    try:

        first_index, num_images, file_size = (
            read_header(image)
        )

    except Exception as e:

        print(
            f"Invalid header: {e}"
        )

        return


    # --------------------------------------------------------
    # Validate header
    # --------------------------------------------------------

    if first_index != 1:

        print(
            "Invalid first image number!"
        )

        return


    if num_images == 0:

        print(
            "Invalid image count!"
        )

        return


    print()
    print("=" * 60)
    print("                     DECODING")
    print("=" * 60)

    print(
        f"Images expected : {num_images:,}"
    )

    print(
        f"Original size   : {file_size:,} bytes"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # Create mask
    # --------------------------------------------------------

    mask_flat = get_mask()


    # --------------------------------------------------------
    # Open output file
    # --------------------------------------------------------

    try:

        output = open(
            output_file,
            "wb"
        )

    except OSError as e:

        print(
            f"Unable to create output file: {e}"
        )

        return


    # --------------------------------------------------------
    # Decode images
    # --------------------------------------------------------

    with output:

        for k in range(
            1,
            num_images + 1
        ):

            filename = (
                f"{k}.png"
            )


            # ------------------------------------------------
            # Check file
            # ------------------------------------------------

            if not os.path.exists(
                filename
            ):

                print(
                    f"\nMissing image: "
                    f"{filename}"
                )

                return


            # ------------------------------------------------
            # Read PNG
            # ------------------------------------------------

            image = cv2.imread(
                filename,
                cv2.IMREAD_COLOR
            )


            if image is None:

                print(
                    f"\nUnable to read "
                    f"{filename}"
                )

                return


            # ------------------------------------------------
            # Check dimensions
            # ------------------------------------------------

            if (
                image.shape[1] != WIDTH or
                image.shape[0] != HEIGHT
            ):

                print(
                    f"\nInvalid dimensions: "
                    f"{filename}"
                )

                return


            # ------------------------------------------------
            # Read header
            # ------------------------------------------------

            try:

                index, total, current_file_size = (
                    read_header(image)
                )

            except Exception as e:

                print(
                    f"\nInvalid header in "
                    f"{filename}: {e}"
                )

                return


            # ------------------------------------------------
            # Validate image number
            # ------------------------------------------------

            if index != k:

                print(
                    f"\nWrong image number "
                    f"in {filename}"
                )

                return


            # ------------------------------------------------
            # Validate total image count
            # ------------------------------------------------

            if total != num_images:

                print(
                    f"\nImage count mismatch "
                    f"in {filename}"
                )

                return


            # ------------------------------------------------
            # Validate original file size
            # ------------------------------------------------

            if current_file_size != file_size:

                print(
                    f"\nFile size mismatch "
                    f"in {filename}"
                )

                return


            # ------------------------------------------------
            # Flatten image
            # ------------------------------------------------

            flat = image.reshape(
                (-1, 3)
            )


            # ------------------------------------------------
            # Extract usable pixels
            # ------------------------------------------------

            valid_pixels = flat[
                mask_flat
            ]


            chunk = valid_pixels.flatten()


            # ------------------------------------------------
            # Determine actual bytes
            # ------------------------------------------------

            offset = (
                (k - 1) *
                BYTES_PER_IMAGE
            )


            if offset >= file_size:

                chunk_size = 0

            else:

                remaining = (
                    file_size -
                    offset
                )

                chunk_size = min(
                    BYTES_PER_IMAGE,
                    remaining
                )


            # ------------------------------------------------
            # Write bytes
            # ------------------------------------------------

            if chunk_size > 0:

                output.write(
                    chunk[
                        :chunk_size
                    ].tobytes()
                )


            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            print(
                f"\rDecoded "
                f"{k:,} / "
                f"{num_images:,}",
                end="",
                flush=True
            )


    print()
    print()
    print("=" * 60)
    print("                     COMPLETE")
    print("=" * 60)

    print(
        f"Output file : {output_file}"
    )

    print(
        f"File size   : {file_size:,} bytes"
    )

    print("=" * 60)


# ============================================================
# WAIT FOR USER
# ============================================================

def wait_for_enter():

    input(
        "\nPress ENTER to return to menu..."
    )


# ============================================================
# MAIN MENU
# ============================================================

def main():

    while True:

        print()
        print()
        print("=" * 60)
        print("              PNG FILE ENCODER / DECODER")
        print("=" * 60)

        print(
            "1. File -> PNG images"
        )

        print(
            "2. PNG images -> File"
        )

        print(
            "3. Exit"
        )

        print("=" * 60)


        choice = input(
            "Enter choice: "
        ).strip()


        if choice == "1":

            file_to_images()

            wait_for_enter()


        elif choice == "2":

            images_to_file()

            wait_for_enter()


        elif choice == "3":

            print(
                "\nExiting..."
            )

            break


        else:

            print(
                "\nInvalid choice!"
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
