import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
import tempfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.price_list import PriceList
from app.models.product_mapping import ProductMapping
from app.services.moysklad import get_ms1_client


class PriceListService:
    """Service for price list generation."""

    def __init__(self, db_session: Session):
        """
        Initialize the price list service.

        Args:
            db_session: Database session
        """
        self.db = db_session
        self.logger = logging.getLogger("price_list")

        # Create directory for PDF files if it doesn't exist
        os.makedirs("./pdf_files", exist_ok=True)

    async def generate_pdf(self, price_list_id: int, user_id: int) -> str:
        """
        Generate a PDF price list.

        Args:
            price_list_id: Price list ID
            user_id: User ID

        Returns:
            Path to the generated PDF file
        """
        try:
            # Get price list configuration
            price_list = self.db.query(PriceList).filter(PriceList.id == price_list_id).first()
            if not price_list:
                raise ValueError(f"Price list with ID {price_list_id} not found")

            # Get products from MS1 with minimum quantity
            ms1_client = get_ms1_client()
            query = ms1_client.assortment.query()
            query.filter().eq("archived", False)
            products, _ = ms1_client.assortment.find_all(query)

            # Filter products by minimum quantity
            filtered_products = []
            for product in products:
                # Check if product has stock information
                try:
                    stock = ms1_client.products.get_stock(product.id)
                    if stock and stock.get('stock') and stock.get('stock') >= price_list.min_quantity:
                        filtered_products.append(product)
                except:
                    # Skip products that don't have stock information
                    continue

            # Generate PDF
            pdf_path = self._generate_pdf_file(price_list, filtered_products)

            # Update price list
            price_list.pdf_path = pdf_path
            price_list.last_generated_at = datetime.now()
            self.db.commit()

            return pdf_path

        except Exception as e:
            self.logger.error(f"Price list generation failed: {str(e)}")
            raise

    def _generate_pdf_file(self, price_list: PriceList, products: list) -> str:
        """
        Generate a PDF file for the price list.

        Args:
            price_list: Price list configuration
            products: List of products

        Returns:
            Path to the generated PDF file
        """
        # Create PDF file path
        filename = f"price_list_{price_list.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join("./pdf_files", filename)

        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        heading_style = styles["Heading2"]
        normal_style = styles["Normal"]

        # Create document elements
        elements = []

        # Add title
        elements.append(Paragraph(price_list.name, title_style))
        elements.append(Spacer(1, 12))

        # Add description if available
        if price_list.description:
            elements.append(Paragraph(price_list.description, normal_style))
            elements.append(Spacer(1, 12))

        # Add date
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
        elements.append(Spacer(1, 24))

        # Add products table
        table_data = [
            ["#", "Name", "Code", "Price", "Quantity"]
        ]

        for i, product in enumerate(products, 1):
            price = product.salePrices[0]["value"] if product.salePrices else 0
            stock = 0
            try:
                stock_info = get_ms1_client().products.get_stock(product.id)
                stock = stock_info.get('stock', 0)
            except:
                pass

            table_data.append([
                i,
                product.name,
                product.code or "",
                f"{price:,.2f}",
                stock
            ])

        # Create table
        table = Table(table_data, repeatRows=1)

        # Style table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),
        ]))

        elements.append(table)

        # Build PDF
        doc.build(elements)

        return pdf_path