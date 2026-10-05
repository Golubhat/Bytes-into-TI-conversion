import wave
import numpy as np
import os
import struct


# ============================================================
# CONFIGURATION
# ============================================================

SAMPLE_RATE = 44100

# 8-byte file size
HEADER_SIZE = 8

# Process file in chunks to avoid loading huge files into RAM
CHUNK_SIZE = 16 * 1024 * 1024  # 16 MB


# ============================================================
# HEADER
#
# 8 bytes:
#
# uint64 = original file size
#
# Big endian
# ============================================================

MAX_FILE_SIZE = 0xFFFFFFFFFFFFFFFF


# ============================================================
# ENCODE
# ============================================================

def file_to_audio():

    input_file = input(
        "Enter input file: "
    ).strip()

    output_audio = input(
        "Enter output WAV file (e.g., out.wav): "
    ).strip()


    # --------------------------------------------------------
    # Check input file
    # --------------------------------------------------------

    if not os.path.isfile(input_file):

        print(
            "Input file not found!"
        )

        return


    # --------------------------------------------------------
    # Get file size
    # --------------------------------------------------------

    file_size = os.path.getsize(
        input_file
    )


    if file_size > MAX_FILE_SIZE:

        print(
            "File is too large for uint64!"
        )

        return


    print()
    print("=" * 60)
    print("                    ENCODING")
    print("=" * 60)

    print(
        f"Input file : {input_file}"
    )

    print(
        f"File size  : {file_size:,} bytes"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # WAV
    #
    # One input byte = one 16-bit sample
    #
    # Sample value:
    #
    # byte 0   -> -128
    # byte 255 -> 127
    #
    # --------------------------------------------------------

    try:

        with wave.open(
            output_audio,
            "wb"
        ) as wf:

            wf.setnchannels(1)

            wf.setsampwidth(2)

            wf.setframerate(
                SAMPLE_RATE
            )


            # ------------------------------------------------
            # Write 8-byte header
            # ------------------------------------------------

            header = struct.pack(
                ">Q",
                file_size
            )


            header_array = np.frombuffer(
                header,
                dtype=np.uint8
            )


            header_audio = (
                header_array.astype(
                    np.int16
                ) - 128
            )


            wf.writeframes(
                header_audio.tobytes()
            )


            # ------------------------------------------------
            # Process input file in chunks
            # ------------------------------------------------

            processed = 0


            with open(
                input_file,
                "rb"
            ) as f:

                while True:

                    data = f.read(
                        CHUNK_SIZE
                    )


                    if not data:

                        break


                    byte_array = np.frombuffer(
                        data,
                        dtype=np.uint8
                    )


                    # Convert uint8 -> signed int16
                    audio = (
                        byte_array.astype(
                            np.int16
                        ) - 128
                    )


                    wf.writeframes(
                        audio.tobytes()
                    )


                    processed += len(
                        data
                    )


                    percentage = (
                        processed /
                        file_size *
                        100
                    ) if file_size else 100


                    print(
                        f"\rProcessed: "
                        f"{processed:,} / "
                        f"{file_size:,} bytes "
                        f"({percentage:.2f}%)",
                        end="",
                        flush=True
                    )


    except Exception as e:

        print(
            f"\nEncoding error: {e}"
        )

        return


    print()
    print()
    print("=" * 60)
    print("                ENCODING COMPLETE")
    print("=" * 60)

    print(
        f"Output WAV : {output_audio}"
    )

    print(
        f"Original   : {file_size:,} bytes"
    )

    print("=" * 60)


# ============================================================
# DECODE
# ============================================================

def audio_to_file():

    input_audio = input(
        "Enter input WAV file: "
    ).strip()

    output_file = input(
        "Enter output file name: "
    ).strip()


    # --------------------------------------------------------
    # Check WAV
    # --------------------------------------------------------

    if not os.path.isfile(input_audio):

        print(
            "Input WAV file not found!"
        )

        return


    print()
    print("=" * 60)
    print("                    DECODING")
    print("=" * 60)


    try:

        with wave.open(
            input_audio,
            "rb"
        ) as wf:


            # ------------------------------------------------
            # Validate WAV
            # ------------------------------------------------

            channels = wf.getnchannels()

            sample_width = wf.getsampwidth()

            sample_rate = wf.getframerate()


            if channels != 1:

                print(
                    "Error: WAV must be mono."
                )

                return


            if sample_width != 2:

                print(
                    "Error: WAV must contain "
                    "16-bit samples."
                )

                return


            # ------------------------------------------------
            # Read 8-byte header
            # ------------------------------------------------

            header_frames = wf.readframes(
                HEADER_SIZE
            )


            header_audio = np.frombuffer(
                header_frames,
                dtype=np.int16
            )


            if len(header_audio) != HEADER_SIZE:

                print(
                    "Invalid or incomplete header!"
                )

                return


            header_bytes = (
                header_audio + 128
            ).astype(
                np.uint8
            ).tobytes()


            file_size = struct.unpack(
                ">Q",
                header_bytes
            )[0]


            print(
                f"Original file size : "
                f"{file_size:,} bytes"
            )


            # ------------------------------------------------
            # Decode remaining audio
            # ------------------------------------------------

            remaining = file_size

            processed = 0


            with open(
                output_file,
                "wb"
            ) as out:


                while remaining > 0:

                    frames_to_read = min(
                        CHUNK_SIZE,
                        remaining
                    )


                    frames = wf.readframes(
                        frames_to_read
                    )


                    if not frames:

                        print(
                            "\nUnexpected end "
                            "of WAV file!"
                        )

                        return


                    audio = np.frombuffer(
                        frames,
                        dtype=np.int16
                    )


                    # ------------------------------------------------
                    # Convert signed int16 -> uint8
                    # ------------------------------------------------

                    byte_array = (
                        audio + 128
                    ).astype(
                        np.uint8
                    )


                    # Only write required bytes
                    write_size = min(
                        len(byte_array),
                        remaining
                    )


                    out.write(
                        byte_array[
                            :write_size
                        ].tobytes()
                    )


                    processed += write_size

                    remaining -= write_size


                    percentage = (
                        processed /
                        file_size *
                        100
                    ) if file_size else 100


                    print(
                        f"\rProcessed: "
                        f"{processed:,} / "
                        f"{file_size:,} bytes "
                        f"({percentage:.2f}%)",
                        end="",
                        flush=True
                    )


    except Exception as e:

        print(
            f"\nDecoding error: {e}"
        )

        return


    print()
    print()
    print("=" * 60)
    print("                DECODING COMPLETE")
    print("=" * 60)

    print(
        f"Output file : {output_file}"
    )

    print(
        f"File size   : {file_size:,} bytes"
    )

    print("=" * 60)


# ============================================================
# WAIT
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
        print("             FILE <-> WAV ENCODER")
        print("=" * 60)

        print(
            "1. File -> Audio"
        )

        print(
            "2. Audio -> File"
        )

        print(
            "3. Exit"
        )

        print("=" * 60)


        choice = input(
            "Enter choice: "
        ).strip()


        if choice == "1":

            file_to_audio()

            wait_for_enter()


        elif choice == "2":

            audio_to_file()

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
