import os
from pathlib import Path
from PIL import Image
from transformers import pipeline

from logger import logger


class VisionAnalyzer:
    def __init__(self, model_name: str = "google/vit-base-patch16-224"):
        """
        Initializes the local vision model pipeline.
        Uses a standard Vision Transformer by default, but can be swapped
        for an iNaturalist-specific model if needed.
        """
        self.model_name = model_name
        logger.info(f"Loading local vision model: {self.model_name}")
        
        try:
            # Load the pipeline. It will download the model the first time and cache it locally.
            self.classifier = pipeline("image-classification", model=self.model_name)
            logger.info("Vision model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load vision model: {e}")
            self.classifier = None

    def identify_species(self, image_path: str, top_k: int = 3) -> list:
        """
        Runs the image classification pipeline on the provided image and returns the top_k predictions.
        """
        if not self.classifier:
            logger.error("Classifier pipeline is not available.")
            return []

        path = Path(image_path)
        if not path.exists():
            logger.error(f"Image not found at path: {image_path}")
            return []

        try:
            # We open the image with PIL as the pipeline expects an Image object
            image = Image.open(path).convert("RGB")
            
            # The pipeline returns a list of dicts: [{'score': 0.9, 'label': 'golden retriever'}, ...]
            results = self.classifier(image, top_k=top_k)
            return results
        except Exception as e:
            logger.error(f"Error classifying image {image_path}: {e}")
            return []
