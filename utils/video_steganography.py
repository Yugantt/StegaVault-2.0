"""
Video LSB steganography.

The message is written into the least significant bits of the first
frames; the remaining frames are copied through untouched.

Both functions accept an optional progress_callback(percent).
"""

import cv2
import numpy as np

END_MARKER = "1111111111111110"

# The hidden bits live in the least significant bit of each pixel, so the
# output MUST use a lossless codec (FFV1 in an AVI container). Re-encoding
# with a lossy codec such as mp4v destroys the message.
CODEC = "FFV1"
CONTAINER = ".avi"


def encode_video(input_path, output_path, message, progress_callback=None):
    """
    Hide a secret message inside a video using LSB steganography.
    """
    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        raise ValueError("Could not open the video file.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

    binary = "".join(format(ord(c), "08b") for c in message) + END_MARKER
    bits = np.array([int(b) for b in binary], dtype=np.uint8)

    capacity_per_frame = width * height * 3
    if capacity_per_frame <= 0:
        cap.release()
        raise ValueError("Invalid video dimensions.")

    fourcc = cv2.VideoWriter_fourcc(*CODEC)
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        cap.release()
        raise ValueError(
            "Could not create the output video. "
            f"The {CODEC} codec is not available in your OpenCV build."
        )

    written = 0
    frame_index = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if written < len(bits):
                flat = frame.flatten()
                chunk = bits[written:written + len(flat)]
                flat[:len(chunk)] = (flat[:len(chunk)] & 0xFE) | chunk
                frame = flat.reshape(frame.shape)
                written += len(chunk)

            out.write(frame)
            frame_index += 1

            if progress_callback and total_frames > 0:
                progress_callback(int(frame_index / total_frames * 99))
    finally:
        cap.release()
        out.release()

    if written < len(bits):
        raise ValueError(
            "Message too long for this video! "
            f"Capacity: {written} bits, needed: {len(bits)} bits"
        )

    if progress_callback:
        progress_callback(100)

    return True


def decode_video(input_path, progress_callback=None):
    """
    Recover a hidden message from a video encoded with encode_video().
    """
    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        raise ValueError("Could not open the video file.")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

    marker = np.array([int(b) for b in END_MARKER], dtype=np.uint8)
    collected = []
    found = False
    frame_index = 0

    try:
        while not found:
            ret, frame = cap.read()
            if not ret:
                break

            frame_bits = (frame.flatten() & 1).astype(np.uint8)
            collected.append(frame_bits)
            frame_index += 1

            if progress_callback and total_frames > 0:
                progress_callback(int(frame_index / total_frames * 95))

            joined = np.concatenate(collected)
            for i in range(max(0, len(joined) - len(frame_bits) - 16), len(joined) - 15):
                if np.array_equal(joined[i:i + 16], marker):
                    collected = [joined[:i]]
                    found = True
                    break
    finally:
        cap.release()

    if progress_callback:
        progress_callback(98)

    bits = np.concatenate(collected) if collected else np.array([], dtype=np.uint8)

    message = ""
    for i in range(0, len(bits) - 7, 8):
        byte = "".join(str(b) for b in bits[i:i + 8])
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
