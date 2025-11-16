"""
Supplier Invoice API Routes
Module 5: Készletkezelés és AI OCR

Ez a modul tartalmazza a szállítói számlák feldolgozásához kapcsolódó FastAPI végpontokat.
Implementálja az OCR-alapú számlafeldolgozást Google Cloud Document AI használatával.

Fázis 5.3: OCR Upload Router - POST /inventory/invoices/upload végpont
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from backend.service_inventory.services.ocr_service import OcrService
from backend.service_inventory.schemas.supplier_invoice import (
    SupplierInvoiceCreate,
)


# Router létrehozása
router = APIRouter(
    prefix="/invoices",
    tags=["invoices"]
)


def get_ocr_service() -> OcrService:
    """
    Dependency function az OcrService injektálásához.

    Returns:
        OcrService: OCR service instance
    """
    return OcrService()


@router.post(
    "/upload",
    response_model=SupplierInvoiceCreate,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process supplier invoice with OCR",
    description="""
    Upload egy szállítói számla képfájl (PDF, JPG, PNG, TIFF) OCR feldolgozásra.

    A szolgáltatás a következőket végzi:
    1. Validálja a fájl típusát (támogatott: PDF, JPG, PNG, TIFF)
    2. Feldolgozza a Google Cloud Document AI Invoice Parser processzorral
    3. Kinyeri a strukturált számlaadatokat (beszállító, dátum, összeg, tételek)
    4. Visszaadja az OCR által felismert számlaadatokat

    **OCR Funkciók:**
    - Automatikus szövegfelismerés és elemzés
    - Beszállító név, számlaszám, dátum kinyerése
    - Számlatételek és árak felismerése
    - Megbízhatósági pontszám (confidence score)

    **Támogatott fájltípusok:**
    - PDF dokumentumok (application/pdf)
    - JPEG/JPG képek (image/jpeg, image/jpg)
    - PNG képek (image/png)
    - TIFF képek (image/tiff)

    **Követelmények:**
    - Maximum fájlméret: korlátlan (Document AI kezeli)
    - Érvényes fájlformátum kötelező
    - Google Cloud Document AI konfiguráció szükséges

    **Visszatérési értékek:**
    - 201: Sikeresen feldolgozott számla OCR adatokkal
    - 400: Érvénytelen fájltípus vagy üres fájl
    - 500: Feldolgozási hiba (Document AI hiba, hálózati probléma, stb.)
    """,
)
async def upload_invoice(
    file: UploadFile = File(
        ...,
        description="Szállítói számla fájl (PDF, JPG, PNG, TIFF formátumban)"
    ),
    ocr_service: OcrService = Depends(get_ocr_service)
):
    """
    Szállítói számla feltöltése és feldolgozása OCR-rel.

    Ez a végpont fogadja a feltöltött számlafájlt, elküldi a Google Cloud
    Document AI szolgáltatásnak elemzésre, majd visszaadja a felismert
    strukturált adatokat.

    Args:
        file (UploadFile): Feltöltött számlafájl (multipart/form-data)
        ocr_service (OcrService): OCR szolgáltatás instance (dependency injection)

    Returns:
        SupplierInvoiceCreate: OCR által kinyert számlaadatok, beleértve:
            - supplier_name: Beszállító neve
            - invoice_date: Számla dátuma
            - total_amount: Végösszeg (HUF)
            - status: Feldolgozási állapot ("FELDOLGOZÁSRA VÁR")
            - ocr_data: Teljes OCR adat (nyers szöveg, tételek, megbízhatóság)

    Raises:
        HTTPException 400: Érvénytelen fájltípus vagy üres fájl
        HTTPException 500: OCR feldolgozási hiba

    Example:
        curl -X POST "http://localhost:8003/inventory/invoices/upload" \\
             -H "accept: application/json" \\
             -H "Content-Type: multipart/form-data" \\
             -F "file=@invoice.pdf"
    """
    try:
        # OCR feldolgozás indítása
        invoice_data = await ocr_service.process_invoice_upload(file)
        return invoice_data

    except HTTPException:
        # OcrService már dobott HTTPException-t (validációs hiba)
        raise

    except Exception as e:
        # Egyéb nem várt hibák kezelése
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Váratlan hiba történt a számla feldolgozása során: {str(e)}"
        )
