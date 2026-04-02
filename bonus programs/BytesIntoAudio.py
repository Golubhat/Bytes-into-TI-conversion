import wave
import numpy as np

# --- CONFIG ---
SAMPLE_RATE = 44100
HEADER_SIZE = 4  # only file size


# --- ENCODE ---
def file_to_audio():
    input_file = input("Enter input file: ")
    output_audio = input("Enter output WAV file (e.g., out.wav): ")

    with open(input_file, "rb") as f:
        data = f.read()

    file_size = len(data)

    # --- HEADER (only file size) ---
    header = file_size.to_bytes(4, 'big')

    full_data = header + data
    byte_array = np.frombuffer(full_data, dtype=np.uint8)

    # Convert to signed audio
    audio = byte_array.astype(np.int16) - 128

    with wave.open(output_audio, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())

    print("Encoding complete!")


# --- DECODE ---
def audio_to_file():
    input_audio = input("Enter input WAV file: ")
    output_file = input("Enter output file name: ")

    with wave.open(input_audio, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16)

    # Convert back to bytes
    byte_array = (audio + 128).astype(np.uint8)
    data = byte_array.tobytes()

    # --- READ HEADER ---
    file_size = int.from_bytes(data[0:4], 'big')

    file_data = data[4:4+file_size]

    with open(output_file, "wb") as f:
        f.write(file_data)

    print(f"Decoding complete! File saved as: {output_file}")


# --- MAIN ---
def main():
    print("1. File → Audio")
    print("2. Audio → File")

    choice = int(input("Enter choice: "))

    if choice == 1:
        file_to_audio()
    elif choice == 2:
        audio_to_file()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
