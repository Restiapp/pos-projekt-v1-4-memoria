"""
NAV OSA Configuration Module
Handles NAV Online Számlázó API configuration and environment variables

NAV API Documentation: https://onlineszamla.nav.gov.hu/dokumentaciok
API Version: 3.0
"""
import os
from typing import Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class NAVConfig:
    """
    NAV OSA API Configuration

    Attributes:
        technical_user: NAV technical user (8-digit tax ID)
        technical_password: NAV technical user password (hashed)
        signature_key: Signature key for cryptographic signing
        replacement_key: Replacement key for cryptographic signing
        tax_number: Company tax number (11 digits: XXXXXXXX-Y-ZZ)

        test_api_url: NAV test environment URL
        production_api_url: NAV production environment URL

        enable_real_api: Enable real NAV API calls (False = MOCK mode)
        default_test_mode: Default to test environment (True recommended)

        timeout_seconds: HTTP request timeout
        max_retries: Maximum retry attempts for failed requests
        retry_delay_seconds: Delay between retries (exponential backoff)
    """

    # NAV Technical User Credentials
    technical_user: Optional[str] = None
    technical_password: Optional[str] = None
    signature_key: Optional[str] = None
    replacement_key: Optional[str] = None

    # Company Tax Number
    tax_number: Optional[str] = None

    # NAV API Endpoints
    test_api_url: str = "https://api-test.onlineszamla.nav.gov.hu/invoiceService/v3"
    production_api_url: str = "https://api.onlineszamla.nav.gov.hu/invoiceService/v3"

    # Feature Flags
    enable_real_api: bool = False  # Default to MOCK mode for safety
    default_test_mode: bool = True

    # HTTP Configuration
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 2.0

    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.enable_real_api:
            missing_fields = []

            if not self.technical_user:
                missing_fields.append("NAV_TECHNICAL_USER")
            if not self.technical_password:
                missing_fields.append("NAV_TECHNICAL_PASSWORD")
            if not self.signature_key:
                missing_fields.append("NAV_SIGNATURE_KEY")
            if not self.replacement_key:
                missing_fields.append("NAV_REPLACEMENT_KEY")
            if not self.tax_number:
                missing_fields.append("NAV_TAX_NUMBER")

            if missing_fields:
                logger.warning(
                    f"NAV real API enabled but missing credentials: {', '.join(missing_fields)}. "
                    "Falling back to MOCK mode."
                )
                self.enable_real_api = False

        # Log configuration status
        if self.enable_real_api:
            env = "TEST" if self.default_test_mode else "PRODUCTION"
            logger.info(f"NAV OSA: Real API enabled ({env} environment)")
            logger.info(f"NAV OSA: Technical User = {self.technical_user}")
            logger.info(f"NAV OSA: Tax Number = {self.tax_number}")
        else:
            logger.info("NAV OSA: MOCK mode enabled (no real API calls)")

    def get_api_url(self, test_mode: bool = None) -> str:
        """
        Get the appropriate NAV API URL based on test mode

        Args:
            test_mode: Override default test mode. If None, uses default_test_mode

        Returns:
            NAV API base URL
        """
        use_test = test_mode if test_mode is not None else self.default_test_mode
        return self.test_api_url if use_test else self.production_api_url

    @property
    def is_configured(self) -> bool:
        """Check if NAV credentials are properly configured"""
        return all([
            self.technical_user,
            self.technical_password,
            self.signature_key,
            self.replacement_key,
            self.tax_number
        ])

    @classmethod
    def from_env(cls) -> "NAVConfig":
        """
        Load NAV configuration from environment variables

        Environment Variables:
            NAV_TECHNICAL_USER: NAV technical user (required for real API)
            NAV_TECHNICAL_PASSWORD: NAV technical password (required for real API)
            NAV_SIGNATURE_KEY: Signature key (required for real API)
            NAV_REPLACEMENT_KEY: Replacement key (required for real API)
            NAV_TAX_NUMBER: Company tax number (required for real API)

            NAV_ENABLE_REAL_API: Enable real API calls (default: False)
            NAV_DEFAULT_TEST_MODE: Default to test environment (default: True)
            NAV_TIMEOUT_SECONDS: Request timeout (default: 30)
            NAV_MAX_RETRIES: Max retry attempts (default: 3)

        Returns:
            NAVConfig instance
        """
        return cls(
            # Credentials
            technical_user=os.getenv("NAV_TECHNICAL_USER"),
            technical_password=os.getenv("NAV_TECHNICAL_PASSWORD"),
            signature_key=os.getenv("NAV_SIGNATURE_KEY"),
            replacement_key=os.getenv("NAV_REPLACEMENT_KEY"),
            tax_number=os.getenv("NAV_TAX_NUMBER"),

            # Feature Flags
            enable_real_api=os.getenv("NAV_ENABLE_REAL_API", "false").lower() == "true",
            default_test_mode=os.getenv("NAV_DEFAULT_TEST_MODE", "true").lower() == "true",

            # HTTP Configuration
            timeout_seconds=int(os.getenv("NAV_TIMEOUT_SECONDS", "30")),
            max_retries=int(os.getenv("NAV_MAX_RETRIES", "3")),
            retry_delay_seconds=float(os.getenv("NAV_RETRY_DELAY_SECONDS", "2.0")),
        )


# Singleton instance
_nav_config: Optional[NAVConfig] = None


def get_nav_config() -> NAVConfig:
    """
    Get NAV configuration singleton instance

    Returns:
        NAVConfig instance loaded from environment
    """
    global _nav_config
    if _nav_config is None:
        _nav_config = NAVConfig.from_env()
    return _nav_config
