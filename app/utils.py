# app/utils.py
import base64
import hashlib
import numpy as np
import cv2

def base64_to_image(base64_string: str) -> np.ndarray:
    """Dekodira Base64 string u OpenCV (Numpy) sliku."""
    try:
        img_bytes = base64.b64decode(base64_string)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return image
    except Exception:
        return None

def verify_image_hash(image_base64_string: str, provided_hash: str) -> bool:
    """
    Verifikuje integritet slike poređenjem SHA-256 heša.
    
    Args:
        image_base64_string (str): Slika enkodirana u Base64.
        provided_hash (str): Očekivani SHA-256 heš (hex digest).
    
    Returns:
        bool: True ako se heševi poklapaju, inače False.
    """
    image_bytes = image_base64_string.encode('utf-8')
    calculated_hash = hashlib.sha256(image_bytes).hexdigest()
    
    return calculated_hash == provided_hash