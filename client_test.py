# client_test.py
import asyncio
import websockets
import base64
import json
import hashlib
import time


IMAGE_PATH = "test_image.jpg"  
SERVER_URL = "ws://127.0.0.1:8000/ws/detect"

def prepare_image_data(image_path: str) -> dict:
    """Loads the image, encodes it in Base64, and calculates its hash."""
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    

    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    hash_object = hashlib.sha256(base64_string.encode('utf-8'))
    hex_hash = hash_object.hexdigest()
    
    return {
        "image": base64_string,
        "hash": hex_hash
    }

async def run_test():
    """Main function for testing the client."""
    print(f"Connecting to server: {SERVER_URL}")
    try:
        async with websockets.connect(SERVER_URL, ping_interval=None) as websocket:
            print("Connection successful.")
            
            payload = prepare_image_data(IMAGE_PATH)
            print(f"Sending image '{IMAGE_PATH}' for processing...")
            
            start_time = time.time()
            
            await websocket.send(json.dumps(payload))
            
            response = await websocket.recv()
            
            end_time = time.time()
            
            print("\n--- Response from server ---")
            response_data = json.loads(response)
            print(json.dumps(response_data, indent=2))
            print("----------------------------")
            print(f"Total time (send + process + receive): {end_time - start_time:.4f} seconds")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed: {e}")
    except ConnectionRefusedError:
        print("Connection refused. Is the server running?")
    except FileNotFoundError:
        print(f"Error: Image at path '{IMAGE_PATH}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())