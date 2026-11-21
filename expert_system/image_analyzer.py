"""
CropCare AI - Image Analyzer & Vision AI Connector
Bridge to the VisionDiseaseClassifier providing leaf image validation,
color space feature extraction, and disease classification.
"""

from typing import Dict, Any, Optional
try:
    from .vision_ai import VisionDiseaseClassifier
except (ImportError, ValueError):
    from vision_ai import VisionDiseaseClassifier

class ImageAnalyzer:
    """
    Image Analysis and Vision Classifier Adapter.
    """

    def __init__(self, upload_folder: str = "static/uploads"):
        self.classifier = VisionDiseaseClassifier(upload_folder=upload_folder)
        self.upload_folder = upload_folder

    def is_allowed_file(self, filename: str) -> bool:
        return self.classifier.is_allowed_file(filename)

    def analyze_image(
        self,
        image_path: str,
        target_crop: Optional[str] = None,
        lang: str = "en",
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes vision classification and returns metrics.
        """
        result = self.classifier.classify(
            image_path=image_path,
            target_crop=target_crop,
            lang=lang,
            api_key=api_key
        )

        metrics = result.get("visual_metrics", {})
        return {
            "success": result.get("success", True),
            "engine": result.get("engine", "Local Vision Engine"),
            "healthy_ratio": metrics.get("healthy_ratio", 0.0),
            "chlorosis_ratio": metrics.get("chlorosis_ratio", 0.0),
            "necrosis_ratio": metrics.get("necrosis_ratio", 0.0),
            "assessment": result.get("explanation", {}).get("why_selected", ""),
            "suggested_symptoms": result.get("visual_symptoms", []),
            "vision_result": result
        }
