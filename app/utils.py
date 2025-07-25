# app/utils.py
import base64
import hashlib
import numpy as np
import cv2

def base64_to_image(base64_string: str) -> np.ndarray:
    """Decodes a Base64 string into an OpenCV (Numpy) image."""
    try:
        img_bytes = base64.b64decode(base64_string)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return image
    except Exception:
        return None

def verify_image_hash(image_base64_string: str, provided_hash: str) -> bool:
    """
    Verifies image integrity by comparing SHA-256 hashes.
    
    Args:
        image_base64_string (str): The image encoded in Base64.
        provided_hash (str): The expected SHA-256 hash (hex digest).
    
    Returns:
        bool: True if the hashes match, otherwise False.
    """
    image_bytes = image_base64_string.encode('utf-8')
    calculated_hash = hashlib.sha256(image_bytes).hexdigest()
    
    return calculated_hash == provided_hash