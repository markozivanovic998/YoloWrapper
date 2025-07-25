import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .FastApiConfig import config
from .yolo_handler import yolo_model
from . import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YOLOv12 WebSocket Inference Server",
    description="Server za detekciju objekata preko WebSocket-a sa filtriranjem klasa."
)

@app.on_event("startup")
async def startup_event():
    """Logika koja se izvršava pri pokretanju servera."""
    logger.info("Server se pokreće...")
    logger.info("YOLO model je spreman.")

@app.get("/", summary="Provera statusa servera")
async def read_root():
    """Endpoint za proveru da li server radi."""
    return {"status": "YOLO Inference Server is running"}

@app.websocket("/ws/detect")
async def websocket_endpoint(websocket: WebSocket):
    """
    Glavni WebSocket endpoint za primanje slika i vraćanje rezultata.
    """
    await websocket.accept()
    logger.info(f"Klijent {websocket.client.host}:{websocket.client.port} se povezao.")
    
    try:
        while True:
            data = await websocket.receive_json()

            image_b64 = data.get("image")
            provided_hash = data.get("hash")

            if not image_b64 or not provided_hash:
                await websocket.send_json({"status": "error", "message": "Poruka mora sadržati 'image' i 'hash' ključeve."})
                continue

            if not utils.verify_image_hash(image_b64, provided_hash):
                logger.warning(f"Neuspešna provera heša za klijenta {websocket.client.host}")
                await websocket.send_json({"status": "error", "message": "Integritet slike je narušen (hash mismatch)."})
                continue
            
            image = utils.base64_to_image(image_b64)
            if image is None:
                logger.error("Neuspešno dekodiranje Base64 slike.")
                await websocket.send_json({"status": "error", "message": "Nije moguće dekodirati Base64 sliku."})
                continue
            try:
                detections = yolo_model.detect(image)
                await websocket.send_json({
                    "status": "success",
                    "detections": detections
                })
                logger.info(f"Uspešno obrađena slika, pronađeno {len(detections)} aktivnih objekata.")
            except Exception as e:
                logger.error(f"Greška prilikom inference: {e}")
                await websocket.send_json({"status": "error", "message": f"Greška na serveru prilikom detekcije: {e}"})

    except WebSocketDisconnect:
        logger.info(f"Klijent {websocket.client.host}:{websocket.client.port} se diskonektovao.")
    except Exception as e:
        logger.error(f"Neočekivana greška u WebSocket konekciji: {e}")
        try:
            await websocket.send_json({"status": "error", "message": "Došlo je do interne greške na serveru."})
        except RuntimeError:
            pass