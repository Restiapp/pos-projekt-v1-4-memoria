"""
OCR Service for Invoice Processing using Google Cloud Document AI.

This service handles the AI-based invoice reading functionality for Module 5.
It uses the Google Cloud Document AI Invoice Parser to extract structured data
from supplier invoice images (PDF, JPG, PNG).
"""

import logging
from typing import Optional
from datetime import datetime
from decimal import Decimal

from fastapi import UploadFile, HTTPException
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions

from backend.service_inventory.config import settings
from backend.service_inventory.schemas.supplier_invoice import (
    OCRData,
    OCRLineItem,
    SupplierInvoiceCreate
)

# Configure logging
logger = logging.getLogger(__name__)


class OcrService:
    """
    Service for processing invoice uploads using Google Cloud Document AI.

    This service integrates with the Document AI Invoice Parser processor
    to extract structured data from supplier invoices, including:
    - Supplier information
    - Invoice metadata (number, date, total)
    - Line items with quantities, prices, and descriptions

    Attributes:
        project_id (str): Google Cloud project ID
        location (str): Document AI processor location (e.g., 'eu', 'us')
        processor_id (str): Document AI processor ID for invoice parsing
        client (documentai.DocumentProcessorServiceClient): Document AI client
    """

    def __init__(self):
        """
        Initialize the OCR Service with Google Cloud Document AI client.

        Raises:
            ValueError: If required configuration is missing
        """
        self.project_id = settings.gcp_project_id
        self.location = settings.documentai_location
        self.processor_id = settings.documentai_processor_id

        # Initialize Document AI client with location-specific endpoint
        opts = ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
        self.client = documentai.DocumentProcessorServiceClient(client_options=opts)

        # Build processor resource name
        self.processor_name = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )

        logger.info(
            f"OcrService initialized with processor: {self.processor_name}"
        )

    async def process_invoice_upload(
        self,
        file: UploadFile
    ) -> SupplierInvoiceCreate:
        """
        Process an uploaded invoice file using Document AI.

        This method:
        1. Reads the uploaded file content
        2. Sends it to Document AI Invoice Parser
        3. Extracts structured invoice data
        4. Returns a SupplierInvoiceCreate schema with OCR data

        Args:
            file (UploadFile): The uploaded invoice file (PDF, JPG, PNG)

        Returns:
            SupplierInvoiceCreate: Schema containing extracted invoice data

        Raises:
            HTTPException: If file processing fails or invalid file type
        """
        try:
            # Validate file type
            allowed_mime_types = [
                "application/pdf",
                "image/jpeg",
                "image/jpg",
                "image/png",
                "image/tiff"
            ]

            if file.content_type not in allowed_mime_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.content_type}. "
                           f"Allowed types: {', '.join(allowed_mime_types)}"
                )

            # Read file content
            file_content = await file.read()

            if not file_content:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is empty"
                )

            logger.info(
                f"Processing invoice: {file.filename} "
                f"({len(file_content)} bytes, {file.content_type})"
            )

            # Create Document AI request
            raw_document = documentai.RawDocument(
                content=file_content,
                mime_type=file.content_type
            )

            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )

            # Call Document AI API
            result = self.client.process_document(request=request)
            document = result.document

            logger.info(
                f"Document AI processing completed. "
                f"Confidence: {document.text if hasattr(document, 'text') else 'N/A'}"
            )

            # Extract structured data from Document AI response
            ocr_data = self._extract_ocr_data(document)

            # Create SupplierInvoiceCreate schema
            supplier_invoice = SupplierInvoiceCreate(
                supplier_name=ocr_data.supplier_name,
                invoice_date=ocr_data.invoice_date,
                total_amount=ocr_data.total_amount,
                status="FELDOLGOZÁSRA VÁR",  # Default status
                ocr_data=ocr_data
            )

            logger.info(
                f"Invoice processed successfully: "
                f"Supplier={ocr_data.supplier_name}, "
                f"Invoice#={ocr_data.invoice_number}, "
                f"Total={ocr_data.total_amount}"
            )

            return supplier_invoice

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing invoice: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process invoice: {str(e)}"
            )

    def _extract_ocr_data(self, document: documentai.Document) -> OCRData:
        """
        Extract structured OCR data from Document AI response.

        This internal method parses the Document AI Document object and
        extracts relevant invoice fields using the entities detected by
        the Invoice Parser processor.

        Args:
            document (documentai.Document): Document AI processed document

        Returns:
            OCRData: Structured OCR data schema
        """
        # Initialize OCR data
        ocr_data = OCRData(
            raw_text=document.text if hasattr(document, 'text') else None,
            line_items=[],
            additional_data={}
        )

        # Calculate overall confidence score
        if hasattr(document, 'pages') and document.pages:
            confidences = []
            for page in document.pages:
                if hasattr(page, 'tokens'):
                    for token in page.tokens:
                        if hasattr(token, 'layout') and hasattr(token.layout, 'confidence'):
                            confidences.append(token.layout.confidence)

            if confidences:
                ocr_data.confidence_score = sum(confidences) / len(confidences)

        # Extract entities from Document AI
        if hasattr(document, 'entities'):
            for entity in document.entities:
                entity_type = entity.type_
                entity_value = self._get_entity_text(entity)
                confidence = entity.confidence if hasattr(entity, 'confidence') else None

                # Map Document AI entity types to our schema
                if entity_type == "supplier_name":
                    ocr_data.supplier_name = entity_value

                elif entity_type == "invoice_id" or entity_type == "invoice_number":
                    ocr_data.invoice_number = entity_value

                elif entity_type == "invoice_date":
                    ocr_data.invoice_date = self._parse_date(entity_value)

                elif entity_type == "total_amount" or entity_type == "net_amount":
                    ocr_data.total_amount = self._parse_decimal(entity_value)

                elif entity_type == "line_item":
                    # Extract line item details
                    line_item = self._extract_line_item(entity)
                    if line_item:
                        ocr_data.line_items.append(line_item)

                else:
                    # Store other entities in additional_data
                    if entity_value:
                        ocr_data.additional_data[entity_type] = {
                            "value": entity_value,
                            "confidence": confidence
                        }

        return ocr_data

    def _extract_line_item(self, entity: documentai.Document.Entity) -> Optional[OCRLineItem]:
        """
        Extract a single line item from Document AI entity.

        Args:
            entity (documentai.Document.Entity): Line item entity

        Returns:
            Optional[OCRLineItem]: Parsed line item or None if parsing fails
        """
        line_item = OCRLineItem()

        # Extract properties from line item entity
        if hasattr(entity, 'properties'):
            for prop in entity.properties:
                prop_type = prop.type_
                prop_value = self._get_entity_text(prop)

                if prop_type == "line_item/description":
                    line_item.item_name = prop_value

                elif prop_type == "line_item/quantity":
                    line_item.quantity = self._parse_decimal(prop_value)

                elif prop_type == "line_item/unit":
                    line_item.unit = prop_value

                elif prop_type == "line_item/unit_price":
                    line_item.unit_price = self._parse_decimal(prop_value)

                elif prop_type == "line_item/amount" or prop_type == "line_item/total_price":
                    line_item.total_price = self._parse_decimal(prop_value)

        # Return line item only if it has at least a name or quantity
        if line_item.item_name or line_item.quantity:
            return line_item

        return None

    def _get_entity_text(self, entity: documentai.Document.Entity) -> Optional[str]:
        """
        Extract text value from Document AI entity.

        Args:
            entity (documentai.Document.Entity): Document entity

        Returns:
            Optional[str]: Entity text value or None
        """
        if hasattr(entity, 'mention_text') and entity.mention_text:
            return entity.mention_text.strip()

        if hasattr(entity, 'text_anchor') and entity.text_anchor:
            # Fallback to text anchor if mention_text is not available
            # This would require reconstructing text from segments
            pass

        return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime.date]:
        """
        Parse date string to datetime.date object.

        Attempts multiple date formats commonly found in invoices.

        Args:
            date_str (Optional[str]): Date string from OCR

        Returns:
            Optional[datetime.date]: Parsed date or None if parsing fails
        """
        if not date_str:
            return None

        # Common date formats to try
        date_formats = [
            "%Y-%m-%d",      # 2024-01-15
            "%d/%m/%Y",      # 15/01/2024
            "%d.%m.%Y",      # 15.01.2024
            "%Y.%m.%d",      # 2024.01.15
            "%m/%d/%Y",      # 01/15/2024
            "%d-%m-%Y",      # 15-01-2024
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.date()
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_str}")
        return None

    def _parse_decimal(self, value_str: Optional[str]) -> Optional[Decimal]:
        """
        Parse numeric string to Decimal.

        Handles various number formats including currency symbols,
        thousands separators, and different decimal separators.

        Args:
            value_str (Optional[str]): Numeric string from OCR

        Returns:
            Optional[Decimal]: Parsed decimal value or None if parsing fails
        """
        if not value_str:
            return None

        try:
            # Remove common currency symbols and whitespace
            cleaned = value_str.strip()
            for symbol in ['$', '€', '£', 'Ft', 'HUF', 'USD', 'EUR']:
                cleaned = cleaned.replace(symbol, '')

            # Remove whitespace
            cleaned = cleaned.replace(' ', '')

            # Handle different thousands and decimal separators
            # European format: 1.234.567,89 or 1 234 567,89
            if ',' in cleaned and '.' in cleaned:
                # If both present, assume European format
                if cleaned.rindex(',') > cleaned.rindex('.'):
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    # US format
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Could be European decimal separator
                # Check if there are digits after comma
                parts = cleaned.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Likely decimal separator
                    cleaned = cleaned.replace(',', '.')
                else:
                    # Likely thousands separator
                    cleaned = cleaned.replace(',', '')

            return Decimal(cleaned)

        except (ValueError, TypeError, ArithmeticError) as e:
            logger.warning(f"Could not parse decimal: {value_str} - {str(e)}")
            return None


# Create singleton instance
ocr_service = OcrService()
