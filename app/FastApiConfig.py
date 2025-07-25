# app/config.py
import yaml
from pydantic import BaseModel, Field
from typing import List
import os

class ServerConfig(BaseModel):
    """Configuration model for server settings."""
    host: str
    port: int

class YoloConfig(BaseModel):
    """Configuration model for YOLO settings."""
    model_path: str
    confidence_threshold: float = Field(..., ge=0.0, le=1.0)
    active_classes: List[str]

class AppConfig(BaseModel):
    """Main configuration model that consolidates all others."""
    server: ServerConfig
    yolo: YoloConfig

def load_config(path: str = "FastAPI.yaml") -> AppConfig:
    """
    Loads the configuration from a YAML file, validates it using Pydantic models,
    and returns the configuration object.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found at path: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    return AppConfig(**config_data)

try:
    config = load_config()
except Exception as e:
    print(f"CRITICAL ERROR: Unable to load configuration. Check 'FastAPI.yaml'. Error: {e}")
    exit(1)