"""
NAV OSA Cryptographic Utilities
Handles cryptographic operations for NAV API requests (SHA512, SHA256, Base64)

NAV API Documentation: https://onlineszamla.nav.gov.hu/dokumentaciok
Technical Specification: NAV OSA v3.0 Interface Specification
"""
import hashlib
import hmac
import base64
import secrets
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class NAVCrypto:
    """
    NAV OSA Cryptographic Utilities

    This class provides cryptographic operations required for NAV API authentication
    and request signing according to NAV OSA v3.0 specification.

    NAV Request Signature Components:
    1. requestId: Unique request identifier (30 characters, alphanumeric + '-')
    2. timestamp: ISO 8601 format with timezone (e.g., '2025-01-18T10:30:00.000Z')
    3. signatureKey: Technical user's signature key
    4. requestSignature: SHA512 hash of concatenated components

    Formula:
        requestSignature = SHA512(
            requestId +
            timestamp +
            signatureKey +
            SHA512(technicalPassword)
        )
    """

    @staticmethod
    def generate_request_id() -> str:
        """
        Generate a unique NAV request ID (RID)

        NAV Requirements:
        - Length: 1-30 characters
        - Allowed characters: [A-Za-z0-9_-]
        - Must be unique per request
        - Pattern: 'RID' + timestamp + random

        Returns:
            Unique request ID string

        Example:
            'RID20250118103000_A1B2C3D4'
        """
        timestamp_part = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(4).upper()  # 8 characters
        request_id = f"RID{timestamp_part}_{random_part}"

        # Ensure max 30 characters
        return request_id[:30]

    @staticmethod
    def get_timestamp() -> str:
        """
        Generate NAV-compliant timestamp

        NAV Requirements:
        - Format: ISO 8601 with milliseconds and timezone
        - Example: '2025-01-18T10:30:00.123Z'
        - Timezone: UTC (Z suffix)

        Returns:
            ISO 8601 formatted timestamp string
        """
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    @staticmethod
    def sha512_hash(data: str) -> str:
        """
        Calculate SHA512 hash of input data

        Args:
            data: Input string to hash

        Returns:
            Uppercase hexadecimal SHA512 hash (128 characters)

        Example:
            sha512_hash('password123') -> 'A1B2C3D4...' (128 chars)
        """
        hash_obj = hashlib.sha512(data.encode('utf-8'))
        return hash_obj.hexdigest().upper()

    @staticmethod
    def sha256_hash(data: str) -> str:
        """
        Calculate SHA256 hash of input data

        Args:
            data: Input string to hash

        Returns:
            Uppercase hexadecimal SHA256 hash (64 characters)
        """
        hash_obj = hashlib.sha256(data.encode('utf-8'))
        return hash_obj.hexdigest().upper()

    @staticmethod
    def base64_encode(data: bytes) -> str:
        """
        Base64 encode binary data

        Args:
            data: Binary data to encode

        Returns:
            Base64 encoded string
        """
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def base64_decode(encoded: str) -> bytes:
        """
        Base64 decode string to binary data

        Args:
            encoded: Base64 encoded string

        Returns:
            Decoded binary data
        """
        return base64.b64decode(encoded.encode('utf-8'))

    @classmethod
    def create_request_signature(
        cls,
        request_id: str,
        timestamp: str,
        signature_key: str,
        technical_password: str
    ) -> str:
        """
        Create NAV request signature (SHA512-based)

        NAV Signature Formula:
            requestSignature = SHA512(
                requestId + timestamp + signatureKey + SHA512(technicalPassword)
            )

        Args:
            request_id: Unique request ID (RID)
            timestamp: ISO 8601 timestamp
            signature_key: NAV technical user signature key
            technical_password: NAV technical user password (plain text)

        Returns:
            Uppercase hexadecimal SHA512 signature (128 characters)

        Example:
            create_request_signature(
                'RID20250118103000_A1B2C3D4',
                '2025-01-18T10:30:00.000Z',
                'my-signature-key',
                'my-password'
            ) -> 'F1A2B3C4...' (128 chars)
        """
        # Step 1: Hash the technical password
        password_hash = cls.sha512_hash(technical_password)

        # Step 2: Concatenate components
        signature_input = f"{request_id}{timestamp}{signature_key}{password_hash}"

        # Step 3: Hash the concatenated string
        request_signature = cls.sha512_hash(signature_input)

        logger.debug(
            f"NAV Signature Created: RID={request_id[:20]}... "
            f"Signature={request_signature[:20]}..."
        )

        return request_signature

    @classmethod
    def create_token_exchange_signature(
        cls,
        token: str,
        signature_key: str,
        technical_password: str
    ) -> str:
        """
        Create NAV token exchange signature

        Used for tokenExchange operation when requesting exchange token.

        Formula:
            tokenExchangeSignature = SHA512(
                token + signatureKey + SHA512(technicalPassword)
            )

        Args:
            token: Exchange token received from NAV
            signature_key: NAV technical user signature key
            technical_password: NAV technical user password

        Returns:
            Uppercase hexadecimal SHA512 signature
        """
        password_hash = cls.sha512_hash(technical_password)
        signature_input = f"{token}{signature_key}{password_hash}"
        return cls.sha512_hash(signature_input)

    @classmethod
    def generate_nav_headers(
        cls,
        signature_key: str,
        technical_password: str
    ) -> Dict[str, str]:
        """
        Generate NAV request headers with authentication

        Creates all required headers for NAV API authentication:
        - requestId: Unique request identifier
        - timestamp: Current timestamp (ISO 8601)
        - requestSignature: Cryptographic signature

        Args:
            signature_key: NAV technical user signature key
            technical_password: NAV technical user password

        Returns:
            Dictionary with NAV authentication headers

        Example:
            {
                'requestId': 'RID20250118103000_A1B2C3D4',
                'timestamp': '2025-01-18T10:30:00.123Z',
                'requestSignature': 'F1A2B3C4D5...' (128 chars)
            }
        """
        request_id = cls.generate_request_id()
        timestamp = cls.get_timestamp()
        signature = cls.create_request_signature(
            request_id=request_id,
            timestamp=timestamp,
            signature_key=signature_key,
            technical_password=technical_password
        )

        return {
            "requestId": request_id,
            "timestamp": timestamp,
            "requestSignature": signature
        }

    @classmethod
    def validate_invoice_hash(cls, invoice_xml: str, expected_hash: str) -> bool:
        """
        Validate invoice data hash (SHA256)

        NAV requires SHA256 hash of the compressed invoice XML data.

        Args:
            invoice_xml: Invoice XML string
            expected_hash: Expected SHA256 hash (uppercase hex)

        Returns:
            True if hash matches, False otherwise
        """
        actual_hash = cls.sha256_hash(invoice_xml)
        return actual_hash == expected_hash.upper()
