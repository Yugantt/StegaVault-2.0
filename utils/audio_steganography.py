"""
WAV LSB steganography.

Both functions accept an optional progress_callback(percent) that is
called as the sample loop advances.
"""

import wave

import numpy as np

END_MARKER = "1111111111111110"
CHUNKS = 100


def encode_audio_lsb(input_path, message, output_path, progress_callback=None):
    """
    Hide a secret message inside a WAV file using LSB steganography.
    """
    try:
        with wave.open(input_path, "rb") as wav:
            params = wav.getparams()
            frames = wav.readframes(params.nframes)

        audio_data = np.frombuffer(frames, dtype=np.int16).copy()

        binary_message = "".join(format(ord(c), "08b") for c in message)
        binary_message += END_MARKER

        if len(binary_message) > len(audio_data):
            raise ValueError(
                f"Message too long! Maximum capacity: {len(audio_data)} bits, "
                f"Your message needs: {len(binary_message)} bits"
            )

        total = len(binary_message)
        step = max(1, total // CHUNKS)

        for i in range(total):
            bit = int(binary_message[i])
            audio_data[i] = (audio_data[i] & ~1) | bit

            if progress_callback and i % step == 0:
                progress_callback(int(i / total * 95))

        if progress_callback:
            progress_callback(97)

        with wave.open(output_path, "wb") as wav_out:
            wav_out.setparams(params)
            wav_out.writeframes(audio_data.tobytes())

        if progress_callback:
            progress_callback(100)

        return True

    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Encoding failed: {str(e)}")


def decode_audio_lsb(input_path, progress_callback=None):
    """
    Recover a hidden message from a WAV file encoded with encode_audio_lsb().
    """
    try:
        with wave.open(input_path, "rb") as wav:
            frames = wav.readframes(wav.getnframes())

        audio_data = np.frombuffer(frames, dtype=np.int16)

        total = len(audio_data)
        step = max(1, total // CHUNKS)

        bits = []
        for i in range(total):
            bits.append(str(audio_data[i] & 1))

            if len(bits) >= 16 and "".join(bits[-16:]) == END_MARKER:
                bits = bits[:-16]
                break

            if progress_callback and i % step == 0:
                progress_callback(int(i / total * 95))

        if progress_callback:
            progress_callback(98)

        message = ""
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte = "".join(bits[i:i + 8])
                try:
                    char = chr(int(byte, 2))
                    if char == "\x00":
                        break
                    message += char
                except ValueError:
                    continue

        if progress_callback:
            progress_callback(100)

        return message.strip()

    except Exception as e:
        raise Exception(f"Decoding failed: {str(e)}")
