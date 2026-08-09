"""
Image LSB steganography.

Both functions accept an optional progress_callback(percent).
"""

import numpy as np
from PIL import Image

END_MARKER = "1111111111111110"
CHUNKS = 100


def encode_message_in_image(input_path, message, output_path, progress_callback=None):
    """
    Hide a secret message inside an image using LSB steganography.
    Always written out as PNG so the pixels survive losslessly.
    """
    img = Image.open(input_path)

    if img.mode not in ("RGB", "RGBA", "L"):
        img = img.convert("RGB")

    pixels = np.array(img)
    flat = pixels.flatten()

    binary = "".join(format(ord(c), "08b") for c in message) + END_MARKER

    if len(binary) > len(flat):
        raise ValueError(
            f"Message too long! Maximum capacity: {len(flat)} bits, "
            f"Your message needs: {len(binary)} bits"
        )

    total = len(binary)
    step = max(1, total // CHUNKS)

    for i in range(total):
        flat[i] = (flat[i] & 0xFE) | int(binary[i])

        if progress_callback and i % step == 0:
            progress_callback(int(i / total * 95))

    if progress_callback:
        progress_callback(97)

    encoded = flat.reshape(pixels.shape)
    Image.fromarray(encoded.astype("uint8")).save(output_path)

    if progress_callback:
        progress_callback(100)

    return True


def decode_message_from_image(image_path, progress_callback=None):
    """
    Recover a hidden message from an image encoded with encode_message_in_image().
    """
    img = Image.open(image_path)
    pixels = np.array(img)
    flat = pixels.flatten()

    total = len(flat)
    step = max(1, total // CHUNKS)

    bits = []
    for i in range(total):
        bits.append(str(flat[i] & 1))

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
