Here's the English translation of your project description:

-----

## FastAPI YOLO WebSocket Server

This project provides a high-performance server wrapper for YOLOv8 models, built using the FastAPI framework. The server listens for connections over the WebSocket protocol, receives Base64-encoded images, verifies their integrity using SHA-256 hashes, performs object detection, and returns the results to the client in real-time.

A key feature is the ability to dynamically activate only specific classes for detection via a central `config.yaml` file, without needing to modify the code.

-----

### Key Features

  * **Real-time Communication**: Utilizes WebSockets for fast, bi-directional communication with clients.
  * **Dynamic Configuration**: All key settings (server address, model path, confidence threshold, active classes) are defined in the `config.yaml` file.
  * **Class Filtering**: Returns detections only for classes listed in the `active_classes` list within the configuration.
  * **Integrity Check**: Every received image is verified by comparing its hash with the hash sent by the client, ensuring data authenticity.
  * **Asynchronous Processing**: Built on FastAPI and Uvicorn, enabling efficient processing of a large number of parallel connections.
  * **GPU Support**: Automatically uses a CUDA-enabled GPU if available, significantly accelerating the detection process.

-----

### Project Structure

The project is organized as follows for easy navigation and maintenance:

```
yolo_socket_server/
├── models/
│   └── yolov8n.pt            # Place your downloaded YOLO model here
├── app/
│   ├── __init__.py
│   ├── main.py               # Main FastAPI file with WebSocket logic
│   ├── yolo_handler.py       # Class for managing the YOLO model
│   ├── utils.py              # Helper functions (base64, hashing)
│   └── config.py             # Logic for loading and validating configuration
├── config.yaml               # Central configuration file
├── requirements.txt          # List of required Python libraries
└── client_test.py            # Example client for testing the server
```

-----

### Configuration (`config.yaml`)

This is the heart of the application where you customize server behavior. Based on the code in `app/config.py`, the file should have the following structure:

```yaml
# Configuration for FastAPI YOLO Server
server:
  host: "127.0.0.1"
  port: 8000

yolo:
  # Path to the .pt model weights file.
  model_path: "models/yolov8n.pt"

  # Confidence threshold. Detections below this value are ignored.
  confidence_threshold: 0.4

  # List of classes to activate.
  # Names must exactly match those in the model (e.g., COCO dataset).
  active_classes:
    - "person"
    - "car"
    - "bus"
    - "truck"
    - "traffic light"
```

  * **`server`**: Defines the network address (`host`) and port on which the server will run.
  * **`yolo.model_path`**: Path to the YOLO model's `.pt` file.
  * **`yolo.confidence_threshold`**: Minimum confidence level (from 0.0 to 1.0) for a detection to be considered.
  * **`yolo.active_classes`**: A list of class names you want to detect. All other detected classes will be ignored.

-----

### Installation and Running

1.  **Clone the repository (optional)**

    ```bash
    git clone <REPOSITORY_URL>
    cd yolo_socket_server
    ```

2.  **Create and activate a virtual environment**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install required libraries**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Download YOLO model**
    Download your desired YOLOv8 model (e.g., `yolov8n.pt`) from the Ultralytics repository and place it in the `models/` folder.

5.  **Configure `config.yaml`**
    Modify the file according to your needs as described above.

6.  **Run the server**
    From the main project directory (`yolo_socket_server/`), run the following command:

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

    The `--reload` option is useful during development as it automatically restarts the server after any code changes.

-----

### Testing

To test the server, use the provided `client_test.py`.

1.  Place a test image (e.g., `test_image.jpg`) in the main directory.

2.  Update the `IMAGE_PATH` variable within the `client_test.py` script.

3.  In a new terminal, run the client:

    ```bash
    python client_test.py
    ```

    The client will read the image, encode it, calculate the hash, send it to the server, and print the received response.

-----

### WebSocket API

**Endpoint**: `ws://<host>:<port>/ws/detect`

**Message from client (JSON format)**:

```json
{
  "image": "<base64_encoded_image>",
  "hash": "<sha256_hash_of_base64_string>"
}
```

**Response from server (Success)**:

```json
{
  "status": "success",
  "detections": [
    {
      "label": "car",
      "confidence": 0.8765,
      "box": [120, 345, 310, 500]
    }
  ]
}
```

**Response from server (Error)**:

```json
{
  "status": "error",
  "message": "Error description (e.g., Image integrity compromised)."
}
```