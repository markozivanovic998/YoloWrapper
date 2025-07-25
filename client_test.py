# client_test.py
import asyncio
import websockets
import base64
import json
import hashlib
import time
import cv2 
import numpy as np
import os

IMAGE_PATH = "test_image.jpg"
SERVER_URL = "ws://127.0.0.1:8000/ws/detect"

def prepare_payload(image_path: str, settings: dict) -> dict:
    """Loads the image, encodes it, calculates its hash, and bundles it with settings."""
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    
    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    hash_object = hashlib.sha256(base64_string.encode('utf-8'))
    hex_hash = hash_object.hexdigest()
    
    return {
        "image": base64_string,
        "hash": hex_hash,
        "settings": settings 
    }
    
def draw_detections(image_path, detections):
    """Draws detection boxes on the image and displays it."""
    if not detections:
        print("No objects detected to draw.")
        return
        
    img = cv2.imread(image_path)
    for det in detections:
        box = det['box']
        label = f"{det['label']} {det['confidence']:.2f}"
        

        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
        
        cv2.putText(img, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
    cv2.imshow("Detections", img)
    print("\nPress any key on the image window to close it.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


async def run_test():
    """Main function for testing the client."""

    client_settings = {
        "confidence_threshold": 0.55,
        "active_classes": ["person", "car"] 
    }
    
    print(f"Connecting to server: {SERVER_URL}")
    print(f"Sending image '{IMAGE_PATH}' with custom settings:")
    print(json.dumps(client_settings, indent=2))
    
    try:
        async with websockets.connect(SERVER_URL, ping_interval=None, max_size=10_000_000) as websocket:
            print("\nConnection successful. ✅")
            
            payload = prepare_payload(IMAGE_PATH, client_settings)
            
            start_time = time.time()
            await websocket.send(json.dumps(payload))
            response = await websocket.recv()
            end_time = time.time()
            
            print("\n--- Response from server ---")
            response_data = json.loads(response)
            print(json.dumps(response_data, indent=2))
            print("----------------------------")
            print(f"Total time (send + process + receive): {end_time - start_time:.4f} seconds")

            if response_data.get("status") == "success":
                draw_detections(IMAGE_PATH, response_data.get("detections", []))

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed: {e}")
    except ConnectionRefusedError:
        print("Connection refused. Is the server running?")
    except FileNotFoundError:
        print(f"Error: Image at path '{IMAGE_PATH}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if not os.path.exists(IMAGE_PATH):
        print(f"'{IMAGE_PATH}' not found. Creating a dummy image.")
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(dummy_image, "Test Image", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imwrite(IMAGE_PATH, dummy_image)
        
    asyncio.run(run_test())