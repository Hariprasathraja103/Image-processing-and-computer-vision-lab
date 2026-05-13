"""
compressor.py
-------------
Core image compression logic using OpenCV and Pillow.
Handles loading, compressing, and saving images.
"""

import cv2
import numpy as np
from PIL import Image
import io
import os


def get_file_size_kb(data: bytes) -> float:
    """Return the size of a byte string in kilobytes."""
    return len(data) / 1024


def load_image_bytes(uploaded_file) -> bytes:
    """
    Read raw bytes from a Streamlit UploadedFile object.

    Args:
        uploaded_file: Streamlit file uploader result.

    Returns:
        Raw image bytes.
    """
    return uploaded_file.read()


def bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """
    Convert raw bytes to a PIL Image.

    Args:
        image_bytes: Raw bytes of the image file.

    Returns:
        PIL Image object (RGB).
    """
    img = Image.open(io.BytesIO(image_bytes))
    # Ensure consistent colour space for display & processing
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image to an OpenCV BGR numpy array.

    Pillow uses RGB; OpenCV uses BGR, so we flip the channels.
    """
    rgb_array = np.array(pil_img)
    bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    return bgr_array


def cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
    """
    Convert an OpenCV BGR numpy array back to a PIL RGB Image.
    """
    rgb_array = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_array)


def compress_image(
    image_bytes: bytes,
    quality: int = 75,
    resize_percent: int = 100,
) -> tuple[bytes, dict]:
    """
    Compress an image using JPEG encoding via OpenCV.

    Steps:
      1. Decode original bytes → OpenCV array
      2. Optionally resize the image
      3. Re-encode as JPEG with the requested quality level
      4. Return compressed bytes + stats dict

    Args:
        image_bytes:    Raw bytes of the source image.
        quality:        JPEG quality (1–95). Lower = smaller file, more artefacts.
        resize_percent: Scale factor 10–100 %. 100 keeps original dimensions.

    Returns:
        compressed_bytes: JPEG-encoded bytes of the compressed image.
        stats:            Dict with original_kb, compressed_kb, saving_pct, dimensions.
    """
    # --- Step 1: Decode ---
    np_arr = np.frombuffer(image_bytes, dtype=np.uint8)
    cv2_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # BGR array

    if cv2_img is None:
        raise ValueError("Could not decode the image. Please upload a valid file.")

    original_h, original_w = cv2_img.shape[:2]

    # --- Step 2: Optional resize ---
    if resize_percent < 100:
        scale = resize_percent / 100.0
        new_w = max(1, int(original_w * scale))
        new_h = max(1, int(original_h * scale))
        # INTER_AREA is best for downscaling (avoids aliasing)
        cv2_img = cv2.resize(cv2_img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    final_h, final_w = cv2_img.shape[:2]

    # --- Step 3: JPEG encode with chosen quality ---
    # cv2.imencode returns (success_flag, encoded_buffer)
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    success, buffer = cv2.imencode(".jpg", cv2_img, encode_params)

    if not success:
        raise RuntimeError("OpenCV failed to encode the image.")

    compressed_bytes = buffer.tobytes()

    # --- Step 4: Build stats ---
    original_kb = get_file_size_kb(image_bytes)
    compressed_kb = get_file_size_kb(compressed_bytes)
    saving_pct = max(0.0, (1 - compressed_kb / original_kb) * 100) if original_kb else 0.0

    stats = {
        "original_kb": round(original_kb, 2),
        "compressed_kb": round(compressed_kb, 2),
        "saving_pct": round(saving_pct, 1),
        "original_dims": (original_w, original_h),
        "compressed_dims": (final_w, final_h),
    }

    return compressed_bytes, stats
