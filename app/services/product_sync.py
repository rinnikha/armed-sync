import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from moysklad_api import MoySklad
from moysklad_api.entities.products import Product
from moysklad_api.entities.base import Meta
from sqlalchemy.orm import Session

from app.models.product_mapping import ProductMapping
from app.models.sync_log import SyncLog


class ProductSyncService:
    """Service for product synchronization between MS1 and MS2."""

    def __init__(self, ms1_client: MoySklad, ms2_client: MoySklad, db_session: Session):
        """
        Initialize the product sync service.

        Args:
            ms1_client: MoySklad client for MS1
            ms2_client: MoySklad client for MS2
            db_session: Database session
        """
        self.ms1 = ms1_client
        self.ms2 = ms2_client
        self.db = db_session
        self.logger = logging.getLogger("product_sync")

    async def sync_all_products(self) -> Dict[str, Any]:
        """
        Sync all products from MS1 to MS2.

        Returns:
            Dictionary with sync results
        """
        try:
            # Create sync log entry
            sync_log = SyncLog(
                type="product",
                status="processing"
            )
            self.db.add(sync_log)
            self.db.commit()

            # Get products from MS1
            ms1_query = self.ms1.assortment.query()
            ms1_query.filter().eq("archived", False)
            ms1_products, _ = self.ms1.assortment.find_all(ms1_query)

            # Get products from MS2 for comparison
            ms2_query = self.ms2.assortment.query()
            ms2_query.filter().eq("archived", False)
            ms2_products, _ = self.ms2.assortment.find_all(ms2_query)

            # Create lookup dict for MS2 products by external code
            ms2_products_dict = {p.externalCode: p for p in ms2_products if p.externalCode}

            # Process each product from MS1
            results = {
                "created": 0,
                "updated": 0,
                "skipped": 0,
                "failed": 0,
                "discrepancies": []
            }

            for product in ms1_products:
                await self._process_single_product(product, ms2_products_dict, results)

            # Update sync log
            sync_log.status = "completed" if results["failed"] == 0 else "partial"
            sync_log.completed_at = datetime.now()
            sync_log.summary = results
            self.db.commit()

            return results

        except Exception as e:
            # Update sync log with error
            if 'sync_log' in locals():
                sync_log.status = "failed"
                sync_log.completed_at = datetime.now()
                sync_log.errors = str(e)
                self.db.commit()

            self.logger.error(f"Product sync failed: {str(e)}")
            raise

    async def _process_single_product(self, ms1_product, ms2_products_dict, results):
        """
        Process a single product and sync it to MS2.

        Args:
            ms1_product: Product from MS1
            ms2_products_dict: Dictionary of MS2 products by external code
            results: Dictionary to store sync results
        """
        try:
            # Use externalCode as the matching key
            external_code = ms1_product.externalCode or f"ms1_{ms1_product.id}"

            # Check if product exists in DB mapping
            product_mapping = self.db.query(ProductMapping).filter(
                ProductMapping.ms1_id == ms1_product.id
            ).first()

            if product_mapping:
                # Product exists in mapping, check if it exists in MS2
                try:
                    ms2_product = self.ms2.products.find_by_id(product_mapping.ms2_id)

                    # Product exists in MS2, check for differences
                    discrepancies = self._find_discrepancies(ms1_product, ms2_product)

                    if discrepancies:
                        # Update product in MS2
                        updated_product = self._prepare_product_update(ms1_product, ms2_product)
                        self.ms2.products.update(updated_product)
                        results["updated"] += 1

                        # Log discrepancies for reporting
                        results["discrepancies"].append({
                            "product_id": ms1_product.id,
                            "product_name": ms1_product.name,
                            "ms1_id": ms1_product.id,
                            "ms2_id": ms2_product.id,
                            "differences": discrepancies
                        })
                    else:
                        results["skipped"] += 1

                    # Update last synced timestamp
                    product_mapping.last_synced_at = datetime.now()
                    self.db.commit()

                except Exception as e:
                    # MS2 product not found or error occurred, create it
                    self.logger.warning(f"Error with mapped product {ms1_product.name}: {str(e)}")

                    # Create new product in MS2
                    new_product = self._prepare_new_product(ms1_product, external_code)
                    created_product = self.ms2.products.create(new_product)
                    results["created"] += 1

                    # Update mapping with new MS2 ID
                    product_mapping.ms2_id = created_product.id
                    product_mapping.ms2_name = created_product.name
                    product_mapping.ms2_external_code = created_product.externalCode
                    product_mapping.last_synced_at = datetime.now()
                    self.db.commit()

            elif external_code in ms2_products_dict:
                # Product exists in MS2 but not in mapping, update it
                ms2_product = ms2_products_dict[external_code]

                # Create mapping
                product_mapping = ProductMapping(
                    ms1_id=ms1_product.id,
                    ms2_id=ms2_product.id,
                    ms1_name=ms1_product.name,
                    ms2_name=ms2_product.name,
                    ms1_external_code=ms1_product.externalCode,
                    ms2_external_code=ms2_product.externalCode,
                    last_synced_at=datetime.now()
                )
                self.db.add(product_mapping)
                self.db.commit()

                # Check for differences
                discrepancies = self._find_discrepancies(ms1_product, ms2_product)

                if discrepancies:
                    # Update product in MS2
                    updated_product = self._prepare_product_update(ms1_product, ms2_product)
                    self.ms2.products.update(updated_product)
                    results["updated"] += 1

                    # Log discrepancies for reporting
                    results["discrepancies"].append({
                        "product_id": ms1_product.id,
                        "product_name": ms1_product.name,
                        "ms1_id": ms1_product.id,
                        "ms2_id": ms2_product.id,
                        "differences": discrepancies
                    })
                else:
                    results["skipped"] += 1

            else:
                # Product doesn't exist in MS2, create it
                new_product = self._prepare_new_product(ms1_product, external_code)
                created_product = self.ms2.products.create(new_product)
                results["created"] += 1

                # Create mapping
                product_mapping = ProductMapping(
                    ms1_id=ms1_product.id,
                    ms2_id=created_product.id,
                    ms1_name=ms1_product.name,
                    ms2_name=created_product.name,
                    ms1_external_code=ms1_product.externalCode,
                    ms2_external_code=created_product.externalCode,
                    last_synced_at=datetime.now()
                )
                self.db.add(product_mapping)
                self.db.commit()

        except Exception as e:
            self.logger.error(f"Failed to sync product {ms1_product.name}: {str(e)}")
            results["failed"] += 1

    def _find_discrepancies(self, ms1_product, ms2_product):
        """
        Find differences between MS1 and MS2 products.

        Args:
            ms1_product: Product from MS1
            ms2_product: Product from MS2

        Returns:
            Dictionary of differences
        """
        discrepancies = {}

        # Check basic fields
        for field in ["name", "description", "code", "article"]:
            ms1_value = getattr(ms1_product, field, None)
            ms2_value = getattr(ms2_product, field, None)

            if ms1_value != ms2_value:
                discrepancies[field] = {
                    "ms1": ms1_value,
                    "ms2": ms2_value
                }

        # Check prices
        if ms1_product.salePrices and ms2_product.salePrices:
            # Compare first price for simplicity
            ms1_price = ms1_product.salePrices[0]["value"]
            ms2_price = ms2_product.salePrices[0]["value"]

            if ms1_price != ms2_price:
                discrepancies["price"] = {
                    "ms1": str(ms1_price),
                    "ms2": str(ms2_price)
                }

        return discrepancies

    def _prepare_new_product(self, ms1_product, external_code):
        """
        Prepare a new product for MS2 based on MS1 product.

        Args:
            ms1_product: Product from MS1
            external_code: External code for new product

        Returns:
            New product ready for creation in MS2
        """
        # Get currency and price type from MS2
        default_currency = self.ms2.currencies.get_default()
        default_price_type = self.ms2.price_types.get_default()

        # Prepare sale prices with default currency and price type
        sale_prices = []
        if ms1_product.salePrices:
            sale_prices = [
                {
                    "value": price["value"],
                    "currency": default_currency,
                    "priceType": default_price_type
                }
                for price in ms1_product.salePrices
            ]

        # Create product based on MS1 product
        new_product = Product(
            meta=Meta.create_default(),
            name=ms1_product.name,
            description=ms1_product.description,
            code=ms1_product.code,
            article=ms1_product.article,
            vat=ms1_product.vat,
            externalCode=external_code,
            salePrices=sale_prices
        )

        return new_product

    def _prepare_product_update(self, ms1_product, ms2_product):
        """
        Prepare product update for MS2 based on MS1 product.

        Args:
            ms1_product: Product from MS1
            ms2_product: Existing product in MS2

        Returns:
            Updated product for MS2
        """
        # Keep MS2 product as base
        updated_product = ms2_product

        # Update basic fields
        updated_product.name = ms1_product.name
        updated_product.description = ms1_product.description
        updated_product.code = ms1_product.code
        updated_product.article = ms1_product.article
        updated_product.vat = ms1_product.vat

        # Update prices if they exist
        if ms1_product.salePrices and len(ms1_product.salePrices) > 0:
            # Keep the original price type and currency
            if ms2_product.salePrices and len(ms2_product.salePrices) > 0:
                for i, price in enumerate(ms1_product.salePrices):
                    if i < len(ms2_product.salePrices):
                        updated_product.salePrices[i]["value"] = price["value"]
            else:
                # If no prices in MS2, create new ones with default settings
                default_currency = self.ms2.currencies.get_default()
                default_price_type = self.ms2.price_types.get_default()

                updated_product.salePrices = [
                    {
                        "value": price["value"],
                        "currency": default_currency,
                        "priceType": default_price_type
                    }
                    for price in ms1_product.salePrices
                ]

        return updated_product

    def find_discrepancies(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find discrepancies between products in MS1 and MS2.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of products with discrepancies
        """
        # Get product mappings
        mappings = self.db.query(ProductMapping).offset(skip).limit(limit).all()

        discrepancies = []

        for mapping in mappings:
            try:
                # Get products from both systems
                ms1_product = self.ms1.products.find_by_id(mapping.ms1_id)
                ms2_product = self.ms2.products.find_by_id(mapping.ms2_id)

                # Find differences
                diffs = self._find_discrepancies(ms1_product, ms2_product)

                if diffs:
                    discrepancies.append({
                        "product_id": ms1_product.id,
                        "product_name": ms1_product.name,
                        "ms1_id": ms1_product.id,
                        "ms2_id": ms2_product.id,
                        "differences": diffs
                    })

            except Exception as e:
                self.logger.error(f"Error checking discrepancies for product {mapping.ms1_id}: {str(e)}")
                # Add to discrepancies with error
                discrepancies.append({
                    "product_id": mapping.ms1_id,
                    "product_name": mapping.ms1_name or "Unknown",
                    "ms1_id": mapping.ms1_id,
                    "ms2_id": mapping.ms2_id,
                    "differences": {
                        "error": {
                            "ms1": "Error checking product",
                            "ms2": str(e)
                        }
                    }
                })

        return discrepancies