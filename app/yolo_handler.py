# app/yolo_handler.py
import torch
from ultralytics import YOLO
from typing import List, Dict, Any, Set
import numpy as np

from FastApiConfig import config 

class YoloHandler:
    """
    Class that manages the YOLO model, including loading,
    configuration, and performing detection.
    """
    def __init__(self):
        """
        The initializer loads the model and sets up the device.
        Default settings are not stored here anymore for detection,
        but loaded from config as fallback in main.py.
        """
        self.model_path = config.yolo.model_path
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"YOLO model is using device: {self.device}")

        self.model = YOLO(self.model_path)
        self.model.to(self.device)
        
        self.model_classes = self.model.names
        print(f"Model successfully loaded with {len(self.model_classes)} classes.")
        print(f"Default active classes: {config.yolo.active_classes}")
        print(f"Default confidence threshold: {config.yolo.confidence_threshold}")


    def detect(self, image: np.ndarray, conf_threshold: float, active_classes: List[str]) -> List[Dict[str, Any]]:
        """
        Performs object detection on the given image using provided parameters.

        Args:
            image (np.ndarray): The input image as a NumPy array.
            conf_threshold (float): The confidence threshold for this specific detection.
            active_classes (List[str]): A list of class names to detect for this request.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a detection.
        """

        results = self.model(image, conf=conf_threshold, verbose=False)
        
        processed_results = []
        active_classes_set: Set[str] = set(active_classes)
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = self.model_classes[class_id]

                if class_name in active_classes_set:
                    xyxy = box.xyxy[0].cpu().numpy() 
                    confidence = float(box.conf[0])
                    
                    processed_results.append({
                        "label": class_name,
                        "confidence": round(confidence, 4),
                        "box": [int(coord) for coord in xyxy]
                    })
                    
        return processed_results

yolo_model = YoloHandler()