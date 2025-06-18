import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from alembic.script.write_hooks import console_scripts
from exceptiongroup import catch
from moysklad_api import MoySklad
from moysklad_api.entities import Store, Organization, Group, Counterparty
from moysklad_api.entities.documents import CustomerOrder, PurchaseOrder, Position, State
from moysklad_api.repositories.documents import CustomerOrderRepository

from moysklad_api.entities.base import Meta
from moysklad_api.utils.helpers import ms_datetime_to_string
from sqlalchemy.orm import Session

from src.models import OrderSync, OrderSyncConfig
from src.models.order_sync import OrderSyncStatus

MS_SYNC_STATES = [
    'https://api.moysklad.ru/api/remap/1.2/entity/customerorder/metadata/states/bce7e955-c139-11ee-0a80-0cc60001a087', # Отгружено
    'https://api.moysklad.ru/api/remap/1.2/entity/customerorder/metadata/states/ee533246-b442-11ee-0a80-16d90007f2eb', # Доставлено
]


class OrderSyncService:
    """Service for product synchronization between MS1 and MS2."""

    def __init__(self, ms1_client: MoySklad, ms2_client: MoySklad, db_session: Session):
        """
        Initialize the order sync service.

        Args:
            ms1_client: MoySklad client for MS1
            ms2_client: MoySklad client for MS2
            db_session: Database session
        """
        self.ms1 = ms1_client
        self.ms2 = ms2_client
        self.db = db_session
        self.logger = logging.getLogger("product_sync")


    def sync_pending_orders(self):
        pending_orders = self.db.query(OrderSync).filter(OrderSync.sync_status == OrderSyncStatus.PENDING).all()
        for pending_order in pending_orders:
            ms_order_positions, _ = self.ms1.customer_orders.get_positions(pending_order.ms1_order_id)

            assortment_map = self._load_assortments_map()

            positions = []

            errors = []

            for position in ms_order_positions:
                assortment = assortment_map.get(position.assortment['article'])
                if assortment is None:
                    errors.append(f"Unknown assortment: {position.assortment}")
                    continue

                new_pos = Position(
                    assortment={"meta": assortment },
                    quantity=position.quantity,
                    price=position.price,
                )

                positions.append(new_pos)

            if errors:
                pending_order.sync_status = OrderSyncStatus.PENDING
                pending_order.error_msg = "\n".join(errors)
                self.db.commit()
                continue


            new_purchase = PurchaseOrder(
                # TODO: add to OrderSync new column "moment" to store orders moment then use it here
                moment=pending_order.moment,
                store={"meta": {"href": Store.get_href(pending_order.config.ms2_store_id), "type": "store" } },
                agent={"meta": {"href": Organization.get_href(pending_order.config.ms2_organization_id), "type": "organization"} },
                group={"meta": {"href": Group.get_href(pending_order.config.ms2_group_id), "type": "group" } },
                organization={"meta": {"href": Organization.get_href(pending_order.config.ms2_organization_id), "type": "organization" } },
                positions=positions,
                description=f"Создано с помощью Armed-Sync. ID MC1 Заказа: {pending_order.ms1_order_id}; Дата: {pending_order.moment}",
            )

            new_purchase = self.ms2.purchase_orders.create(new_purchase)

            pending_order.sync_status = OrderSyncStatus.SYNCED
            pending_order.ms2_purchase_id = new_purchase.id

            self.db.commit()

    def sync_single_order(self, sync_order: OrderSync):
        ms_order_positions, _ = self.ms1.customer_orders.get_positions(sync_order.ms1_order_id)

        assortment_map = self._load_assortments_map()

        positions = []

        errors = []

        for position in ms_order_positions:
            assortment = assortment_map.get(position.assortment['article'])
            if assortment is None:
                errors.append(f"Unknown assortment: {position.assortment}")
                continue

            new_pos = Position(
                assortment={"meta": assortment},
                quantity=position.quantity,
                price=position.price,
            )

            positions.append(new_pos)

        if errors:
            sync_order.sync_status = OrderSyncStatus.PENDING
            sync_order.error_msg = "\n".join(errors)
            self.db.commit()
            return sync_order
        try:

            new_purchase = PurchaseOrder(
                # TODO: add to OrderSync new column "moment" to store orders moment then use it here
                moment=sync_order.moment,
                store={"meta": {"href": Store.get_href(sync_order.config.ms2_store_id), "type": "store"}},
                agent={"meta": {"href": Organization.get_href(sync_order.config.ms2_organization_id), "type": "organization"}},
                group={"meta": {"href": Group.get_href(sync_order.config.ms2_group_id), "type": "group"}},
                organization={"meta": {"href": Organization.get_href(sync_order.config.ms2_organization_id), "type": "organization"}},
                description=f"Создано с помощью Armed-Sync. ID MC1 Заказа: {sync_order.ms1_order_id}; Дата: {ms_datetime_to_string(sync_order.moment)}",
                positions=positions,
            )


            new_purchase = self.ms2.purchase_orders.create(new_purchase)

            sync_order.sync_status = OrderSyncStatus.SYNCED
            sync_order.ms2_purchase_id = new_purchase.id

            self.db.commit()
        except Exception as e:
            print(e)

        return sync_order


    def update_all_order_sync_status(self):
        try:
            sync_configs = self.db.query(OrderSyncConfig).all()

            for sync_config in sync_configs:
                query = self.ms1.customer_orders.query()
                query.filter().eq("agent", Counterparty.get_href(sync_config.ms1_cp_id))
                for state in MS_SYNC_STATES:
                    query.filter().eq("state", state)
                # query.filter().eq("state", ",".join(MS_SYNC_STATES))
                query.filter().gt("moment", ms_datetime_to_string(sync_config.start_sync_datetime))

                ms_orders, _ = self.ms1.customer_orders.find_all(query)

                self._add_sync_orders(ms_orders, sync_config)
                # self.logger("Loaded successfully")

        except Exception as e:
            self.logger.error(e)

    def _add_sync_orders(self, ms_orders: List[CustomerOrder], sync_config: OrderSyncConfig):
        for ms_order in ms_orders:
            existing_order_sync = self.db.query(OrderSync).filter(OrderSync.ms1_order_id == ms_order.id).first()

            if existing_order_sync:
                if existing_order_sync.sync_status == OrderSyncStatus.SYNCED:
                    self._check_for_modifications(existing_order_sync, ms_order)
                    continue
                elif existing_order_sync.sync_status == OrderSyncStatus.WAITING_FOR_CONFIRM:
                    self._recheck_ms_status(existing_order_sync, ms_order)
                    continue
                else:
                    continue

            sync_status = OrderSyncStatus.PENDING if ms_order.state['meta']['href'] in MS_SYNC_STATES else OrderSyncStatus.WAITING_FOR_CONFIRM

            new_sync_order = OrderSync(
                ms1_order_id=ms_order.id,
                ms1_state_href=ms_order.state['meta']['href'],
                order_amount=ms_order.sum / 100,
                moment=ms_order.moment,
                sync_status=sync_status,
                config_id=sync_config.id,
            )
            self.db.add(new_sync_order)

        self.db.commit()

    def _check_for_modifications(self, existing_order_sync: OrderSync, ms_order: CustomerOrder):
        # TODO: Check if order had changes after setting up confirm status (change of sum, change of positions)
        pass

    def _recheck_ms_status(self, existing_order_sync: OrderSync, ms_order: CustomerOrder):
        # TODO: Check is ms status updated and change sync status accordingly
        pass

    def _load_assortments_map(self):
        assortment_list, _ = self.ms2.assortment.get_all_active(True)

        meta_map = {
            assortment.article: assortment.meta
            for assortment in assortment_list
            if assortment.article and assortment.article.strip()
        }

        return meta_map
