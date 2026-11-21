"""
CropCare AI - Expert System Package
Contains Rule Base, Inference Engine, Explanation Facility, Vision AI, and Crop Recommender.
"""
from .engine import InferenceEngine
from .rules import KNOWLEDGE_BASE, CROPS, SYMPTOMS_VOCABULARY
from .image_analyzer import ImageAnalyzer
from .vision_ai import VisionDiseaseClassifier
from .crop_recommender import CropRecommender
from .advisories import SoilAdvisor, IrrigationAdvisor, AgriChatbot

__all__ = [
    'InferenceEngine',
    'KNOWLEDGE_BASE',
    'CROPS',
    'SYMPTOMS_VOCABULARY',
    'ImageAnalyzer',
    'VisionDiseaseClassifier',
    'CropRecommender',
    'SoilAdvisor',
    'IrrigationAdvisor',
    'AgriChatbot'
]
