import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import csv

from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.product_mapping import ProductMapping
from app.models.order_mapping import OrderMapping
from app.services.moysklad import get_ms1_client, get_ms2_client
from app.services.product_sync import ProductSyncService


class ReportService:
    """Service for report generation."""

    def __init__(self, db_session: Session):
        """
        Initialize the report service.

        Args:
            db_session: Database session
        """
        self.db = db_session
        self.logger = logging.getLogger("report")

        # Create directory for report files if it doesn't exist
        os.makedirs("./report_files", exist_ok=True)

    async def generate_report(self, report_type: str, parameters: Dict[str, Any], user_id: int) -> str:
        """
        Generate a report.

        Args:
            report_type: Type of report to generate
            parameters: Report parameters
            user_id: User ID

        Returns:
            Path to the generated report file
        """
        try:
            # Create report entry
            report = Report(
                report_type=report_type,
                status="processing",
                parameters=parameters,
                user_id=user_id
            )
            self.db.add(report)
            self.db.commit()

            # Generate report based on type
            if report_type == "product_discrepancies":
                result, file_path = await self._generate_product_discrepancies_report(parameters)
            elif report_type == "sync_status":
                result, file_path = await self._generate_sync_status_report(parameters)
            else:
                raise ValueError(f"Unsupported report type: {report_type}")

            # Update report
            report.status = "completed"
            report.result = result
            report.file_path = file_path
            report.completed_at = datetime.now()
            self.db.commit()

            return file_path

        except Exception as e:
            # Update report with error
            if 'report' in locals():
                report.status = "failed"
                report.error_message = str(e)
                report.completed_at = datetime.now()
                self.db.commit()

            self.logger.error(f"Report generation failed: {str(e)}")
            raise

    async def _generate_product_discrepancies_report(self, parameters: Dict[str, Any]) -> tuple:
        """
        Generate a report of product discrepancies between MS1 and MS2.

        Args:
            parameters: Report parameters

        Returns:
            Tuple of (result summary, file path)
        """
        # Initialize MoySklad clients
        ms1_client = get_ms1_client()
        ms2_client = get_ms2_client()

        # Create sync service
        sync_service = ProductSyncService(ms1_client, ms2_client, self.db)

        # Get discrepancies
        discrepancies = sync_service.find_discrepancies(limit=1000)

        # Create file path
        filename = f"product_discrepancies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = os.path.join("./report_files", filename)

        # Write to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['product_id', 'product_name', 'ms1_id', 'ms2_id', 'field', 'ms1_value', 'ms2_value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for discrepancy in discrepancies:
                for field, values in discrepancy['differences'].items():
                    writer.writerow({
                        'product_id': discrepancy['product_id'],
                        'product_name': discrepancy['product_name'],
                        'ms1_id': discrepancy['ms1_id'],
                        'ms2_id': discrepancy['ms2_id'],
                        'field': field,
                        'ms1_value': values.get('ms1', ''),
                        'ms2_value': values.get('ms2', '')
                    })

        # Create result summary
        result = {
            "total_discrepancies": len(discrepancies),
            "fields_with_discrepancies": {}
        }

        # Count discrepancies by field
        for discrepancy in discrepancies:
            for field in discrepancy['differences'].keys():
                if field in result["fields_with_discrepancies"]:
                    result["fields_with_discrepancies"][field] += 1
                else:
                    result["fields_with_discrepancies"][field] = 1

        return result, file_path

    async def _generate_sync_status_report(self, parameters: Dict[str, Any]) -> tuple:
        """
        Generate a report of sync status.

        Args:
            parameters: Report parameters

        Returns:
            Tuple of (result summary, file path)
        """
        # Get sync statistics
        product_mappings = self.db.query(ProductMapping).all()
        order_mappings = self.db.query(OrderMapping).all()

        # Get sync logs
        from app.models.sync_log import SyncLog
        sync_logs = self.db.query(SyncLog).order_by(SyncLog.started_at.desc()).limit(50).all()

        # Create result summary
        result = {
            "products": {
                "total_mapped": len(product_mappings),
                "last_sync": max([m.last_synced_at for m in product_mappings if m.last_synced_at], default=None)
            },
            "orders": {
                "total_mapped": len(order_mappings),
                "last_sync": max([m.last_synced_at for m in order_mappings if m.last_synced_at], default=None)
            },
            "sync_logs": [
                {
                    "id": log.id,
                    "type": log.type,
                    "status": log.status,
                    "started_at": log.started_at.isoformat(),
                    "completed_at": log.completed_at.isoformat() if log.completed_at else None
                }
                for log in sync_logs
            ]
        }

        # Create file path
        filename = f"sync_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = os.path.join("./report_files", filename)

        # Write to JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)

        return result, file_path