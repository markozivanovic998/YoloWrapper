import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .FastApiConfig import config
from .yolo_handler import yolo_model
from . import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YOLOv12 WebSocket Inference Server",
    description="Server for object detection via WebSocket with class filtering."
)

@app.on_event("startup")
async def startup_event():
    """Logic executed when the server starts up."""
    logger.info("Server is starting...")
    logger.info("YOLO model is ready.")

@app.get("/", summary="Check server status")
async def read_root():
    """Endpoint to check if the server is running."""
    return {"status": "YOLO Inference Server is running"}

@app.websocket("/ws/detect")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for receiving images and returning results.
    """
    await websocket.accept()
    logger.info(f"Client {websocket.client.host}:{websocket.client.port} connected.")
    
    try:
        while True:
            data = await websocket.receive_json()

            image_b64 = data.get("image")
            provided_hash = data.get("hash")

            if not image_b64 or not provided_hash:
                await websocket.send_json({"status": "error", "message": "Message must contain 'image' and 'hash' keys."})
                continue

            if not utils.verify_image_hash(image_b64, provided_hash):
                logger.warning(f"Hash verification failed for client {websocket.client.host}")
                await websocket.send_json({"status": "error", "message": "Image integrity compromised (hash mismatch)."})
                continue
            
            image = utils.base64_to_image(image_b64)
            if image is None:
                logger.error("Failed to decode Base64 image.")
                await websocket.send_json({"status": "error", "message": "Could not decode Base64 image."})
                continue
            try:
                detections = yolo_model.detect(image)
                await websocket.send_json({
                    "status": "success",
                    "detections": detections
                })
                logger.info(f"Successfully processed image, found {len(detections)} active objects.")
            except Exception as e:
                logger.error(f"Error during inference: {e}")
                await websocket.send_json({"status": "error", "message": f"Server error during detection: {e}"})

    except WebSocketDisconnect:
        logger.info(f"Client {websocket.client.host}:{websocket.client.port} disconnected.")
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket connection: {e}")
        try:
            await websocket.send_json({"status": "error", "message": "An internal server error occurred."})
        except RuntimeError:
            pass