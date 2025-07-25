# app/yolo_handler.py
import torch
from ultralytics import YOLO
from typing import List, Dict, Any
import numpy as np

from .FastApiConfig import config # Import configuration

class YoloHandler:
    """
    Class that manages the YOLO model, including loading,
    configuration, and performing detection.
    """
    def __init__(self):
        """
        The initializer loads the model and sets active classes.
        """
        self.model_path = config.yolo.model_path
        self.conf_threshold = config.yolo.confidence_threshold
        self.active_classes_names = set(config.yolo.active_classes)

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"YOLO model is using device: {self.device}")

        self.model = YOLO(self.model_path)
        self.model.to(self.device)
        
        self.model_classes = self.model.names
        print(f"Model successfully loaded with {len(self.model_classes)} classes.")
        print(f"Active classes for detection: {list(self.active_classes_names)}")

    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Performs object detection on the given image.

        Args:
            image (np.ndarray): The input image as a NumPy array.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a detection.
                                  Each dictionary contains 'label', 'confidence', and 'box'.
        """
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