"""
Supplier Invoice API Routes
Module 5: Készletkezelés és AI OCR

Ez a modul tartalmazza a szállítói számlák feldolgozásához kapcsolódó FastAPI végpontokat.
Implementálja az OCR-alapú számlafeldolgozást Google Cloud Document AI használatával.

Fázis 5.3: OCR Upload Router - POST /inventory/invoices/upload végpont
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from backend.service_inventory.services.ocr_service import OcrService
from backend.service_inventory.schemas.supplier_invoice import (
    SupplierInvoiceCreate,
    SupplierInvoiceResponse,
)
from backend.service_inventory.models.database import get_db
from backend.service_inventory.models.supplier_invoice import SupplierInvoice


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
    response_model=SupplierInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process supplier invoice with OCR",
    description="""
    Upload egy szállítói számla képfájl (PDF, JPG, PNG, TIFF) OCR feldolgozásra és adatbázisba mentésre.

    A szolgáltatás a következőket végzi:
    1. Validálja a fájl típusát (támogatott: PDF, JPG, PNG, TIFF)
    2. Feldolgozza a Google Cloud Document AI Invoice Parser processzorral
    3. Kinyeri a strukturált számlaadatokat (beszállító, dátum, összeg, tételek)
    4. Menti az új SupplierInvoice rekordot az Inventory DB-be FELDOLGOZÁSRA VÁR státusszal
    5. Visszaadja a mentett számla adatokat

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
    - 201: Sikeresen feldolgozott és mentett számla OCR adatokkal
    - 400: Érvénytelen fájltípus vagy üres fájl
    - 500: Feldolgozási vagy adatbázis hiba
    """,
)
async def upload_invoice(
    file: UploadFile = File(
        ...,
        description="Szállítói számla fájl (PDF, JPG, PNG, TIFF formátumban)"
    ),
    db: Session = Depends(get_db),
    ocr_service: OcrService = Depends(get_ocr_service)
):
    """
    Szállítói számla feltöltése, feldolgozása OCR-rel és mentése az adatbázisba.

    Ez a végpont fogadja a feltöltött számlafájlt, elküldi a Google Cloud
    Document AI szolgáltatásnak elemzésre, majd elmenti a felismert adatokat
    az Inventory adatbázisba FELDOLGOZÁSRA VÁR státusszal.

    Args:
        file (UploadFile): Feltöltött számlafájl (multipart/form-data)
        db (Session): SQLAlchemy adatbázis session (dependency injection)
        ocr_service (OcrService): OCR szolgáltatás instance (dependency injection)

    Returns:
        SupplierInvoiceResponse: Az adatbázisba mentett számla adatai, beleértve:
            - id: Egyedi azonosító (auto-generated)
            - supplier_name: Beszállító neve
            - invoice_date: Számla dátuma
            - total_amount: Végösszeg (HUF)
            - status: Feldolgozási állapot ("FELDOLGOZÁSRA VÁR")
            - ocr_data: Teljes OCR adat JSONB formátumban

    Raises:
        HTTPException 400: Érvénytelen fájltípus vagy üres fájl
        HTTPException 500: OCR feldolgozási vagy adatbázis hiba

    Example:
        curl -X POST "http://localhost:8003/inventory/invoices/upload" \\
             -H "accept: application/json" \\
             -H "Content-Type: multipart/form-data" \\
             -F "file=@invoice.pdf"
    """
    try:
        # 1. OCR feldolgozás indítása - Document AI elemzés
        invoice_data: SupplierInvoiceCreate = await ocr_service.process_invoice_upload(file)

        # 2. OCR adatok konvertálása dictionary-vá (JSONB tároláshoz)
        ocr_data_dict = None
        if invoice_data.ocr_data:
            ocr_data_dict = invoice_data.ocr_data.model_dump(mode='json')

        # 3. Új SupplierInvoice rekord létrehozása az Inventory DB-ben
        db_invoice = SupplierInvoice(
            supplier_name=invoice_data.supplier_name,
            invoice_date=invoice_data.invoice_date,
            total_amount=invoice_data.total_amount,
            status=invoice_data.status,  # Default: "FELDOLGOZÁSRA VÁR"
            ocr_data=ocr_data_dict
        )

        # 4. Mentés az adatbázisba
        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)

        # 5. Visszatérés a mentett rekorddal
        return db_invoice

    except HTTPException:
        # OcrService már dobott HTTPException-t (validációs hiba)
        raise

    except Exception as e:
        # Rollback tranzakció hiba esetén
        db.rollback()

        # Egyéb nem várt hibák kezelése
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Váratlan hiba történt a számla feldolgozása során: {str(e)}"
        )
