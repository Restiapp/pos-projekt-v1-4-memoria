"""
SzamlazzHuService - Számlázz.hu Integráció
Module 8: Admin - Számlázz.hu Integration (V3.0 Phase 1)

DUMMY/MOCK implementáció a Számlázz.hu API integrációhoz.
Ez a service később cserélhető valódi API hívásokra.

A Számlázz.hu API dokumentáció:
https://docs.szamlazz.hu/
"""

from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import logging
import uuid

from backend.service_admin.schemas.finance import (
    SzamlazzHuInvoiceRequest,
    SzamlazzHuInvoiceResponse
)

logger = logging.getLogger(__name__)


class SzamlazzHuService:
    """
    Service osztály a Számlázz.hu API integrációhoz.

    DUMMY/MOCK implementáció - Nem végez valódi API hívásokat.

    Felelősségek:
    - Számla létrehozása
    - PDF generálás (mock)
    - Stornózás (mock)
    - Számlák lekérdezése (mock)
    """

    def __init__(self, api_key: Optional[str] = None, test_mode: bool = True):
        """
        Inicializálja a SzamlazzHuService-t.

        Args:
            api_key: Számlázz.hu API kulcs (jelenleg nem használt a mock-ban)
            test_mode: Teszt mód (alapértelmezett: True)
        """
        self.api_key = api_key or "MOCK_API_KEY"
        self.test_mode = test_mode
        logger.info(
            f"SzamlazzHuService initialized in "
            f"{'TEST' if test_mode else 'PRODUCTION'} mode (MOCK implementation)"
        )

    def create_invoice(
        self,
        invoice_request: SzamlazzHuInvoiceRequest
    ) -> SzamlazzHuInvoiceResponse:
        """
        Számla létrehozása a Számlázz.hu rendszerben.

        MOCK IMPLEMENTÁCIÓ - Nem végez valódi API hívást.
        Visszaad egy szimulált választ generált számlaszámmal.

        Args:
            invoice_request: Számla adatok (SzamlazzHuInvoiceRequest)

        Returns:
            SzamlazzHuInvoiceResponse: Számla létrehozás eredménye

        Note:
            A valódi implementációban itt történne:
            - XML generálás a Számlázz.hu formátumban
            - HTTPS POST kérés a Számlázz.hu API-ra
            - Válasz feldolgozás és PDF letöltés
        """
        try:
            # Generálunk egy egyedi számlaszámot
            invoice_number = self._generate_mock_invoice_number()

            # Számítjuk ki a teljes összeget (mock)
            total_amount = sum(
                item.unit_price * item.quantity
                for item in invoice_request.items
            )

            # Mock PDF URL generálása
            pdf_url = self._generate_mock_pdf_url(invoice_number)

            # Logoljuk a mock műveletet
            logger.info(
                f"MOCK: Invoice created - Number: {invoice_number}, "
                f"Order ID: {invoice_request.order_id}, "
                f"Customer: {invoice_request.customer_name}, "
                f"Total: {total_amount} HUF"
            )

            # Visszaadjuk a mock választ
            return SzamlazzHuInvoiceResponse(
                success=True,
                invoice_number=invoice_number,
                pdf_url=pdf_url,
                message=f"Számla sikeresen létrehozva (MOCK): {invoice_number}",
                order_id=invoice_request.order_id
            )

        except Exception as e:
            logger.error(f"MOCK: Invoice creation failed - Error: {str(e)}")
            return SzamlazzHuInvoiceResponse(
                success=False,
                invoice_number=None,
                pdf_url=None,
                message=f"Hiba történt a számla létrehozása során: {str(e)}",
                order_id=invoice_request.order_id
            )

    def cancel_invoice(self, invoice_number: str) -> Dict[str, Any]:
        """
        Számla stornózása.

        MOCK IMPLEMENTÁCIÓ - Nem végez valódi API hívást.

        Args:
            invoice_number: Számla azonosító

        Returns:
            Dict[str, Any]: Stornózás eredménye
        """
        logger.info(f"MOCK: Invoice cancelled - Number: {invoice_number}")

        return {
            "success": True,
            "invoice_number": invoice_number,
            "cancellation_number": self._generate_mock_invoice_number(prefix="STORNO"),
            "message": f"Számla sikeresen sztornózva (MOCK): {invoice_number}"
        }

    def get_invoice_pdf(self, invoice_number: str) -> Optional[str]:
        """
        Számla PDF letöltése.

        MOCK IMPLEMENTÁCIÓ - Visszaad egy mock URL-t.

        Args:
            invoice_number: Számla azonosító

        Returns:
            Optional[str]: PDF URL vagy None
        """
        pdf_url = self._generate_mock_pdf_url(invoice_number)
        logger.info(f"MOCK: PDF generated - URL: {pdf_url}")
        return pdf_url

    def check_connection(self) -> bool:
        """
        Számlázz.hu API kapcsolat ellenőrzése.

        MOCK IMPLEMENTÁCIÓ - Mindig True-t ad vissza.

        Returns:
            bool: True ha a kapcsolat rendben van (mock: mindig True)
        """
        logger.info("MOCK: Connection check - Status: OK")
        return True

    # ========================================================================
    # Private Helper Methods (Mock)
    # ========================================================================

    def _generate_mock_invoice_number(self, prefix: str = "MOCK-INV") -> str:
        """
        Mock számlaszám generálása.

        Args:
            prefix: Számlaszám előtag

        Returns:
            str: Generált számlaszám
        """
        # Formátum: MOCK-INV-YYYYMMDD-XXXX
        date_str = datetime.now().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"{prefix}-{date_str}-{random_suffix}"

    def _generate_mock_pdf_url(self, invoice_number: str) -> str:
        """
        Mock PDF URL generálása.

        Args:
            invoice_number: Számlaszám

        Returns:
            str: Mock PDF URL
        """
        # Mock URL a Számlázz.hu formátumban
        return f"https://www.szamlazz.hu/mock/invoices/{invoice_number}.pdf"

    def _build_invoice_xml(self, invoice_request: SzamlazzHuInvoiceRequest) -> str:
        """
        XML építése a Számlázz.hu formátumban.

        MOCK IMPLEMENTÁCIÓ - Placeholder a valódi XML generáláshoz.

        Args:
            invoice_request: Számla adatok

        Returns:
            str: XML string (mock)

        Note:
            A valódi implementációban itt kellene az XML-t generálni
            a Számlázz.hu API specifikáció szerint.
        """
        # Placeholder - a valódi implementációban itt építenénk az XML-t
        return f"<!-- MOCK XML for invoice: {invoice_request.order_id} -->"


# ============================================================================
# Service Factory
# ============================================================================

def get_szamlazz_hu_service(
    api_key: Optional[str] = None,
    test_mode: bool = True
) -> SzamlazzHuService:
    """
    Factory függvény a SzamlazzHuService létrehozásához.

    Args:
        api_key: Számlázz.hu API kulcs (opcionális, környezeti változóból is jöhet)
        test_mode: Teszt mód (alapértelmezett: True)

    Returns:
        SzamlazzHuService: Inicializált service instance
    """
    return SzamlazzHuService(api_key=api_key, test_mode=test_mode)
