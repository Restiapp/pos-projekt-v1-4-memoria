"""
Services module for Inventory Service (Module 5).

This module exports business logic services including:
- OCR Service for invoice processing using Google Cloud Document AI
"""

from backend.service_inventory.services.ocr_service import OcrService, ocr_service

__all__ = ["OcrService", "ocr_service"]
