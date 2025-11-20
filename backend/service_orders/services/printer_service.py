"""
Printer Service - Receipt Formatting and Printing
Module: Thermal Receipt Printing [D-PRN]

Ez a service felelős a blokkok generálásáért és nyomtatásáért.
Fejlesztői környezetben fájlba írja a blokkokat, amit később
lecserélhető ESC/POS driverre.

Fázis: [D-PRN] - Thermal Receipt Printing Implementation
"""

import os
import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.service_orders.models.order import Order
from backend.service_orders.models.order_item import OrderItem
from backend.service_orders.models.payment import Payment

logger = logging.getLogger(__name__)

# Receipt configuration
RECEIPT_WIDTH = 48  # Characters width for thermal printer (80mm paper)
RESTAURANT_NAME = "POS Étterem"
RESTAURANT_ADDRESS = "1051 Budapest, Alkotmány utca 12."
RESTAURANT_TAX_ID = "12345678-1-42"
RESTAURANT_PHONE = "+36 1 234 5678"


class PrinterService:
    """
    Service osztály a blokkok generálásához és nyomtatásához.

    Felelősségek:
    - Formázott szöveg generálása (fejléc, tételek, összesítő, lábléc)
    - Blokkot fájlba írása (printer_output könyvtár)
    - ESC/POS formátumra előkészített szöveg generálása
    """

    def __init__(self):
        """Inicializálja a printer service-t és létrehozza az output könyvtárat."""
        self.output_dir = Path(__file__).parent.parent / "printer_output"
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Printer output directory initialized: {self.output_dir}")

    @staticmethod
    def _center_text(text: str, width: int = RECEIPT_WIDTH) -> str:
        """Szöveget középre igazít."""
        padding = (width - len(text)) // 2
        return " " * padding + text

    @staticmethod
    def _left_right_text(left: str, right: str, width: int = RECEIPT_WIDTH) -> str:
        """Bal és jobb oldali szöveget formáz."""
        spacing = width - len(left) - len(right)
        if spacing < 1:
            spacing = 1
        return left + " " * spacing + right

    @staticmethod
    def _separator(char: str = "-", width: int = RECEIPT_WIDTH) -> str:
        """Elválasztó vonal generálása."""
        return char * width

    def _format_header(self, order: Order) -> str:
        """
        Blokk fejléc formázása.

        Args:
            order: Order objektum

        Returns:
            str: Formázott fejléc
        """
        lines = []
        lines.append(self._separator("="))
        lines.append(self._center_text(RESTAURANT_NAME))
        lines.append(self._center_text(RESTAURANT_ADDRESS))
        lines.append(self._center_text(f"Tel: {RESTAURANT_PHONE}"))
        lines.append(self._center_text(f"Adószám: {RESTAURANT_TAX_ID}"))
        lines.append(self._separator("="))
        lines.append("")
        lines.append(self._center_text("SZÁMLA / RECEIPT"))
        lines.append("")
        lines.append(f"Rendelés száma: {order.id}")
        lines.append(f"Típus: {order.order_type}")
        if order.table_id:
            lines.append(f"Asztal: {order.table_id}")
        lines.append(f"Dátum: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(self._separator("-"))

        return "\n".join(lines)

    def _format_items(self, items: List[OrderItem], products_info: Dict[int, Dict[str, Any]]) -> str:
        """
        Rendelési tételek formázása.

        Args:
            items: OrderItem lista
            products_info: Termék információk dict {product_id: {name, ...}}

        Returns:
            str: Formázott tételek
        """
        lines = []
        lines.append(self._left_right_text("Tétel", "Összeg"))
        lines.append(self._separator("-"))

        for item in items:
            # Termék neve
            product_name = products_info.get(item.product_id, {}).get("name", f"Termék #{item.product_id}")
            lines.append(product_name)

            # Mennyiség x Egységár = Összeg
            unit_price = float(item.unit_price)
            item_total = unit_price * item.quantity
            price_line = f"  {item.quantity} x {unit_price:,.0f} Ft"
            total_line = f"{item_total:,.0f} Ft"
            lines.append(self._left_right_text(price_line, total_line))

            # Módosítók (ha vannak)
            if item.selected_modifiers:
                for modifier in item.selected_modifiers:
                    mod_name = modifier.get('modifier_name', '')
                    mod_price = modifier.get('price', 0)
                    if mod_price > 0:
                        lines.append(f"    + {mod_name} (+{mod_price:,.0f} Ft)")
                    else:
                        lines.append(f"    + {mod_name}")

            # Megjegyzések (ha vannak)
            if item.notes:
                lines.append(f"    Megjegyzés: {item.notes}")

            lines.append("")

        return "\n".join(lines)

    def _format_totals(self, order: Order, payments: List[Payment]) -> str:
        """
        Összesítő formázása (végösszeg, ÁFA, fizetési módok).

        Args:
            order: Order objektum
            payments: Payment lista

        Returns:
            str: Formázott összesítő
        """
        lines = []
        lines.append(self._separator("="))

        # Végösszeg
        total = float(order.total_amount or 0)
        lines.append(self._left_right_text("VÉGÖSSZEG:", f"{total:,.0f} Ft"))

        # ÁFA bontás
        vat_rate = float(order.final_vat_rate or 27)
        net_amount = total / (1 + vat_rate / 100)
        vat_amount = total - net_amount

        lines.append(self._separator("-"))
        lines.append(f"ÁFA kulcs: {vat_rate:.0f}%")
        lines.append(self._left_right_text("  Nettó:", f"{net_amount:,.0f} Ft"))
        lines.append(self._left_right_text("  ÁFA:", f"{vat_amount:,.0f} Ft"))
        lines.append(self._left_right_text("  Bruttó:", f"{total:,.0f} Ft"))

        # Fizetési módok
        if payments:
            lines.append(self._separator("-"))
            lines.append("Fizetési módok:")
            for payment in payments:
                payment_amount = float(payment.amount)
                lines.append(self._left_right_text(
                    f"  {payment.payment_method}",
                    f"{payment_amount:,.0f} Ft"
                ))

            # Összes befizetett összeg
            total_paid = sum(float(p.amount) for p in payments)
            lines.append(self._separator("-"))
            lines.append(self._left_right_text("Befizetett:", f"{total_paid:,.0f} Ft"))

            # Visszajáró (ha van)
            change = total_paid - total
            if change > 0:
                lines.append(self._left_right_text("Visszajáró:", f"{change:,.0f} Ft"))

        return "\n".join(lines)

    def _format_footer(self) -> str:
        """
        Blokk lábléc formázása.

        Returns:
            str: Formázott lábléc
        """
        lines = []
        lines.append(self._separator("="))
        lines.append("")
        lines.append(self._center_text("Köszönjük a vásárlást!"))
        lines.append(self._center_text("Thank you!"))
        lines.append("")
        lines.append(self._center_text(f"Nyomtatva: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))
        lines.append(self._separator("="))

        return "\n".join(lines)

    async def print_receipt(
        self,
        db: Session,
        order_id: int,
        products_info: Optional[Dict[int, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Blokk nyomtatása (fájlba írás).

        Args:
            db: SQLAlchemy session
            order_id: Rendelés azonosítója
            products_info: Opcionális termék információk (ha nincs megadva, akkor alapértelmezett neveket használ)

        Returns:
            Dict: Nyomtatás eredménye (file_path, success, message)

        Raises:
            HTTPException 404: Ha a rendelés nem található
            HTTPException 400: Ha a nyomtatás sikertelen
        """
        try:
            # Rendelés lekérdezése
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Rendelés nem található: ID={order_id}"
                )

            # Rendelési tételek lekérdezése
            items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            if not items:
                logger.warning(f"Order {order_id} has no items. Printing empty receipt.")

            # Fizetések lekérdezése
            payments = db.query(Payment).filter(
                Payment.order_id == order_id,
                Payment.status == "SIKERES"
            ).all()

            # Termék információk alapértelmezett értékekkel (ha nincs megadva)
            if products_info is None:
                products_info = {}

            # Blokk összeállítása
            receipt_lines = []
            receipt_lines.append(self._format_header(order))
            receipt_lines.append("")
            receipt_lines.append(self._format_items(items, products_info))
            receipt_lines.append(self._format_totals(order, payments))
            receipt_lines.append("")
            receipt_lines.append(self._format_footer())

            receipt_text = "\n".join(receipt_lines)

            # Fájlba írás
            file_name = f"receipt_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file_path = self.output_dir / file_name

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(receipt_text)

            logger.info(f"Receipt printed successfully: {file_path}")

            # Konzolra is kiírás (fejlesztői célra)
            print("\n" + "=" * 50)
            print("RECEIPT PRINTED:")
            print("=" * 50)
            print(receipt_text)
            print("=" * 50 + "\n")

            return {
                "success": True,
                "message": f"Blokk sikeresen kinyomtatva: {file_name}",
                "file_path": str(file_path),
                "order_id": order_id
            }

        except HTTPException:
            # HTTPException-öket tovább dobni
            raise
        except Exception as e:
            logger.error(f"Error printing receipt for order {order_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a blokk nyomtatása során: {str(e)}"
            )
