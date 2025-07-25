# app/yolo_handler.py
import torch
from ultralytics import YOLO
from typing import List, Dict, Any
import numpy as np

from .FastApiConfig import config # Uvozimo konfiguraciju

class YoloHandler:
    """
    Klasa koja upravlja YOLO modelom, uključujući učitavanje,
    konfiguraciju i izvršavanje detekcije.
    """
    def __init__(self):
        """
        Inicijalizator učitava model i postavlja aktivne klase.
        """
        self.model_path = config.yolo.model_path
        self.conf_threshold = config.yolo.confidence_threshold
        self.active_classes_names = set(config.yolo.active_classes)

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"YOLO model koristi uređaj: {self.device}")

        self.model = YOLO(self.model_path)
        self.model.to(self.device)
        
        self.model_classes = self.model.names
        print(f"Model uspešno učitan sa {len(self.model_classes)} klasa.")
        print(f"Aktivne klase za detekciju: {list(self.active_classes_names)}")

    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:

        results = self.model(image, conf=self.conf_threshold, verbose=False)
        
        processed_results = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = self.model_classes[class_id]

                if class_name in self.active_classes_names:
                    xyxy = box.xyxy[0].cpu().numpy() 
                    confidence = float(box.conf[0])
                    
                    processed_results.append({
                        "label": class_name,
                        "confidence": round(confidence, 4),
                        "box": [int(coord) for coord in xyxy]
                    })
                    
        return processed_results

yolo_model = YoloHandler()