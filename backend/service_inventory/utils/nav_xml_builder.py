"""
NAV OSA XML Builder
Generates XML documents for NAV Online Számlázó API v3.0

NAV API Documentation: https://onlineszamla.nav.gov.hu/dokumentaciok
XML Schema: invoiceData.xsd (NAV OSA v3.0)
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class NAVXMLBuilder:
    """
    NAV OSA XML Builder for Invoice Data

    This class generates XML documents according to NAV OSA v3.0 schema
    for invoice submission (manageInvoice operation).

    NAV XML Structure:
    - InvoiceData (root)
      ├── invoiceNumber
      ├── invoiceIssueDate
      ├── completenessIndicator
      ├── invoiceMain
      │   ├── invoice
      │   │   ├── invoiceHead
      │   │   │   ├── supplierInfo
      │   │   │   ├── customerInfo
      │   │   │   ├── invoiceDetail
      │   │   │   └── ...
      │   │   └── invoiceLines
      │   │       └── line (multiple)
      │   └── ...
      └── ...
    """

    # NAV XML Namespaces (OSA v3.0)
    NAMESPACE = "http://schemas.nav.gov.hu/OSA/3.0/data"
    NAMESPACE_MAP = {
        "": NAMESPACE,
        "common": "http://schemas.nav.gov.hu/OSA/3.0/base"
    }

    @classmethod
    def build_invoice_xml(
        cls,
        invoice_data: Dict[str, Any],
        supplier_tax_number: str
    ) -> str:
        """
        Build complete NAV invoice XML from invoice data

        Args:
            invoice_data: Invoice data dictionary with structure:
                {
                    'invoice_number': str,
                    'invoice_date': datetime,
                    'completion_date': datetime,
                    'payment_method': str,
                    'currency': str,
                    'customer_name': str,
                    'customer_tax_number': str (optional),
                    'customer_address': str (optional),
                    'total_net_amount': Decimal,
                    'total_vat_amount': Decimal,
                    'total_gross_amount': Decimal,
                    'invoice_lines': List[Dict],
                    'notes': str (optional)
                }
            supplier_tax_number: Company tax number (11 digits)

        Returns:
            XML string (UTF-8 encoded)

        Example:
            xml = build_invoice_xml({
                'invoice_number': 'INV-2025-001',
                'invoice_date': datetime(2025, 1, 18),
                ...
            }, '12345678-1-01')
        """
        # Register namespaces
        for prefix, uri in cls.NAMESPACE_MAP.items():
            ET.register_namespace(prefix, uri)

        # Create root element: InvoiceData
        root = ET.Element(
            f"{{{cls.NAMESPACE}}}InvoiceData",
            attrib={"xmlns": cls.NAMESPACE}
        )

        # 1. Invoice Number
        invoice_number_elem = ET.SubElement(root, "invoiceNumber")
        invoice_number_elem.text = invoice_data['invoice_number']

        # 2. Invoice Issue Date (YYYY-MM-DD format)
        issue_date_elem = ET.SubElement(root, "invoiceIssueDate")
        issue_date_elem.text = invoice_data['invoice_date'].strftime("%Y-%m-%d")

        # 3. Completeness Indicator (true = complete invoice)
        completeness_elem = ET.SubElement(root, "completenessIndicator")
        completeness_elem.text = "true"

        # 4. Invoice Main
        invoice_main = ET.SubElement(root, "invoiceMain")

        # 4.1. Invoice
        invoice_elem = ET.SubElement(invoice_main, "invoice")

        # 4.1.1. Invoice Head
        invoice_head = cls._build_invoice_head(
            invoice_elem,
            invoice_data,
            supplier_tax_number
        )

        # 4.1.2. Invoice Lines
        invoice_lines = cls._build_invoice_lines(
            invoice_elem,
            invoice_data['invoice_lines']
        )

        # 4.2. Invoice Reference (optional, for corrections/modifications)
        # Not implemented in this basic version

        # Convert to string
        xml_string = ET.tostring(
            root,
            encoding='utf-8',
            method='xml',
            xml_declaration=True
        ).decode('utf-8')

        logger.debug(f"Generated NAV invoice XML: {len(xml_string)} bytes")
        return xml_string

    @classmethod
    def _build_invoice_head(
        cls,
        parent: ET.Element,
        invoice_data: Dict[str, Any],
        supplier_tax_number: str
    ) -> ET.Element:
        """
        Build invoiceHead section (supplier, customer, invoice details)

        Args:
            parent: Parent XML element (invoice)
            invoice_data: Invoice data dictionary
            supplier_tax_number: Company tax number

        Returns:
            invoiceHead element
        """
        head = ET.SubElement(parent, "invoiceHead")

        # 1. Supplier Info
        supplier_info = ET.SubElement(head, "supplierInfo")

        # 1.1. Supplier Tax Number
        supplier_tax_number_elem = ET.SubElement(supplier_info, "supplierTaxNumber")
        cls._build_tax_number(supplier_tax_number_elem, supplier_tax_number)

        # 1.2. Supplier Name (optional, can be added later)
        # supplier_name_elem = ET.SubElement(supplier_info, "supplierName")
        # supplier_name_elem.text = "Resti Bistro Kft."

        # 2. Customer Info
        customer_info = ET.SubElement(head, "customerInfo")

        # 2.1. Customer Tax Number (if available)
        if invoice_data.get('customer_tax_number'):
            customer_tax_number_elem = ET.SubElement(customer_info, "customerTaxNumber")
            cls._build_tax_number(customer_tax_number_elem, invoice_data['customer_tax_number'])
        else:
            # Non-taxable customer (simplified invoice)
            customer_name_elem = ET.SubElement(customer_info, "customerName")
            customer_name_elem.text = invoice_data.get('customer_name', 'Kiskereskedelmi értékesítés')

        # 3. Invoice Detail
        invoice_detail = ET.SubElement(head, "invoiceDetail")

        # 3.1. Invoice Category (NORMAL, SIMPLIFIED, AGGREGATE)
        invoice_category_elem = ET.SubElement(invoice_detail, "invoiceCategory")
        invoice_category_elem.text = "NORMAL"

        # 3.2. Invoice Delivery Date (teljesítés dátuma)
        delivery_date_elem = ET.SubElement(invoice_detail, "invoiceDeliveryDate")
        delivery_date_elem.text = invoice_data['completion_date'].strftime("%Y-%m-%d")

        # 3.3. Currency Code
        currency_elem = ET.SubElement(invoice_detail, "currencyCode")
        currency_elem.text = invoice_data.get('currency', 'HUF')

        # 3.4. Invoice Appearance (PAPER or ELECTRONIC)
        appearance_elem = ET.SubElement(invoice_detail, "invoiceAppearance")
        appearance_elem.text = "ELECTRONIC"

        # 3.5. Payment Method
        payment_method_elem = ET.SubElement(invoice_detail, "paymentMethod")
        payment_method = cls._map_payment_method(invoice_data.get('payment_method', 'CASH'))
        payment_method_elem.text = payment_method

        return head

    @classmethod
    def _build_invoice_lines(
        cls,
        parent: ET.Element,
        lines: List[Dict[str, Any]]
    ) -> ET.Element:
        """
        Build invoiceLines section (line items)

        Args:
            parent: Parent XML element (invoice)
            lines: List of invoice line dictionaries

        Returns:
            invoiceLines element
        """
        invoice_lines = ET.SubElement(parent, "invoiceLines")

        for line_data in lines:
            line = ET.SubElement(invoice_lines, "line")

            # 1. Line Number
            line_number_elem = ET.SubElement(line, "lineNumber")
            line_number_elem.text = str(line_data['line_number'])

            # 2. Line Modification Reference (optional, for corrections)
            # Not implemented in this basic version

            # 3. Product/Service Description
            line_description = ET.SubElement(line, "lineDescription")
            line_description.text = line_data['product_name']

            # 4. Quantity
            quantity_elem = ET.SubElement(line, "quantity")
            quantity_elem.text = str(line_data['quantity'])

            # 5. Unit of Measure
            unit_elem = ET.SubElement(line, "unitOfMeasure")
            unit_elem.text = line_data.get('unit', 'PIECE')

            # 6. Unit Price (net)
            unit_price_elem = ET.SubElement(line, "unitPrice")
            unit_price_elem.text = cls._format_amount(line_data['unit_price'])

            # 7. Line Amounts
            line_amounts_normal = ET.SubElement(line, "lineAmountsNormal")

            # 7.1. Line Net Amount
            line_net_amount_elem = ET.SubElement(line_amounts_normal, "lineNetAmount")
            line_net_amount_elem.text = cls._format_amount(line_data['net_amount'])

            # 7.2. Line VAT Rate
            line_vat_rate = ET.SubElement(line_amounts_normal, "lineVatRate")

            # VAT Rate can be percentage or exempt
            vat_rate_value = line_data.get('vat_rate', Decimal('27'))
            if vat_rate_value > 0:
                vat_percentage_elem = ET.SubElement(line_vat_rate, "vatPercentage")
                vat_percentage_elem.text = cls._format_vat_rate(vat_rate_value)
            else:
                # Exempt from VAT (e.g., 0%)
                vat_exempt_elem = ET.SubElement(line_vat_rate, "vatExemption")
                case_elem = ET.SubElement(vat_exempt_elem, "case")
                case_elem.text = "AAM"  # Example: Margin scheme

            # 7.3. Line VAT Amount
            line_vat_amount_elem = ET.SubElement(line_amounts_normal, "lineVatAmount")
            line_vat_amount_elem.text = cls._format_amount(line_data['vat_amount'])

            # 7.4. Line Gross Amount (optional but recommended)
            line_gross_amount_elem = ET.SubElement(line_amounts_normal, "lineGrossAmountNormal")
            line_gross_amount_elem.text = cls._format_amount(line_data['gross_amount'])

        return invoice_lines

    @classmethod
    def _build_tax_number(cls, parent: ET.Element, tax_number: str) -> None:
        """
        Build tax number sub-elements (taxpayerId, vatCode, countyCode)

        Hungarian tax number format: XXXXXXXX-Y-ZZ
        - XXXXXXXX: Taxpayer ID (8 digits)
        - Y: VAT code (1 digit)
        - ZZ: County code (2 digits)

        Args:
            parent: Parent XML element (supplierTaxNumber or customerTaxNumber)
            tax_number: Full tax number (11 digits with dashes)
        """
        # Remove dashes and extract components
        cleaned = tax_number.replace("-", "").strip()

        if len(cleaned) != 11 or not cleaned.isdigit():
            logger.warning(f"Invalid tax number format: {tax_number}. Using as-is.")
            # Fallback: use first 8 chars as taxpayerId
            taxpayer_id_elem = ET.SubElement(parent, "taxpayerId")
            taxpayer_id_elem.text = cleaned[:8] if len(cleaned) >= 8 else cleaned.ljust(8, '0')

            vat_code_elem = ET.SubElement(parent, "vatCode")
            vat_code_elem.text = cleaned[8:9] if len(cleaned) > 8 else "1"

            county_code_elem = ET.SubElement(parent, "countyCode")
            county_code_elem.text = cleaned[9:11] if len(cleaned) > 9 else "01"
        else:
            taxpayer_id_elem = ET.SubElement(parent, "taxpayerId")
            taxpayer_id_elem.text = cleaned[:8]

            vat_code_elem = ET.SubElement(parent, "vatCode")
            vat_code_elem.text = cleaned[8:9]

            county_code_elem = ET.SubElement(parent, "countyCode")
            county_code_elem.text = cleaned[9:11]

    @staticmethod
    def _format_amount(amount: Decimal) -> str:
        """
        Format monetary amount for NAV XML (2 decimal places)

        Args:
            amount: Decimal amount

        Returns:
            Formatted string (e.g., '12345.67')
        """
        return f"{amount:.2f}"

    @staticmethod
    def _format_vat_rate(vat_rate: Decimal) -> str:
        """
        Format VAT rate for NAV XML (2 decimal places)

        Args:
            vat_rate: VAT percentage (e.g., 27, 18, 5)

        Returns:
            Formatted string (e.g., '0.27' for 27%)
        """
        # NAV expects VAT rate as decimal (e.g., 0.27 for 27%)
        return f"{(vat_rate / 100):.2f}"

    @staticmethod
    def _map_payment_method(method: str) -> str:
        """
        Map internal payment method to NAV payment method code

        NAV Payment Methods:
        - TRANSFER: Bank transfer
        - CASH: Cash payment
        - CARD: Card payment
        - VOUCHER: Voucher
        - OTHER: Other

        Args:
            method: Internal payment method (e.g., 'CASH', 'CARD', 'BANK_TRANSFER')

        Returns:
            NAV payment method code
        """
        method_upper = method.upper()

        if 'CASH' in method_upper or 'KÉSZPÉNZ' in method_upper:
            return 'CASH'
        elif 'CARD' in method_upper or 'KÁRTYA' in method_upper:
            return 'CARD'
        elif 'TRANSFER' in method_upper or 'ÁTUTALÁS' in method_upper:
            return 'TRANSFER'
        elif 'VOUCHER' in method_upper or 'UTALVÁNY' in method_upper:
            return 'VOUCHER'
        else:
            return 'OTHER'

    @classmethod
    def build_manage_invoice_request(
        cls,
        technical_user: str,
        request_signature: str,
        invoice_operations: List[Dict[str, Any]]
    ) -> str:
        """
        Build complete manageInvoice request XML (wrapper for invoiceData)

        This is the top-level XML sent to NAV /manageInvoice endpoint.

        Args:
            technical_user: NAV technical user (8 digits)
            request_signature: Request signature (from NAVCrypto)
            invoice_operations: List of invoice operations with XML data

        Returns:
            Complete manageInvoice XML request string

        Example:
            xml = build_manage_invoice_request(
                technical_user='12345678',
                request_signature='ABC123...',
                invoice_operations=[{
                    'index': 1,
                    'operation': 'CREATE',
                    'invoice_data': '<InvoiceData>...</InvoiceData>'
                }]
            )
        """
        # This is a simplified version
        # Real implementation would include full NAV request wrapper
        # with header, user, software, invoiceOperations, etc.

        logger.info("Building manageInvoice request XML")
        logger.warning(
            "Full manageInvoice wrapper not implemented. "
            "Using basic invoice XML only. "
            "For production, implement complete NAV request structure."
        )

        # For now, return just the invoice XML
        # TODO: Implement full NAV request wrapper in production
        if invoice_operations:
            return invoice_operations[0].get('invoice_data', '')

        return ''
