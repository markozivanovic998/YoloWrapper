# app/config.py
import yaml
from pydantic import BaseModel, Field
from typing import List
import os

class ServerConfig(BaseModel):
    """Konfiguracioni model za postavke servera."""
    host: str
    port: int

class YoloConfig(BaseModel):
    """Konfiguracioni model za YOLO postavke."""
    model_path: str
    confidence_threshold: float = Field(..., ge=0.0, le=1.0)
    active_classes: List[str]

class AppConfig(BaseModel):
    """Glavni konfiguracioni model koji objedinjuje sve ostale."""
    server: ServerConfig
    yolo: YoloConfig

def load_config(path: str = "FastAPI.yaml") -> AppConfig:
    """
    Učitava konfiguraciju iz YAML fajla, validira je koristeći Pydantic modele
    i vraća konfiguracioni objekat.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Konfiguracioni fajl nije pronađen na putanji: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    return AppConfig(**config_data)

try:
    config = load_config()
except Exception as e:
    print(f"KRITIČNA GREŠKA: Nije moguće učitati konfiguraciju. Proverite 'FastAPI.yaml'. Greška: {e}")
    exit(1)

