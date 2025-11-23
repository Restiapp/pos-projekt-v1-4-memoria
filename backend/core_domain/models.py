from dataclasses import dataclass
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from .enums import OrderStatus, OrderType
from .typing import OrderId, TableId, CustomerId

@dataclass
class OrderStub:
    """
    Pure domain model for Order (no ORM).
    Used for business logic layer decoupling.
    """
    id: OrderId
    status: OrderStatus
    order_type: OrderType
    table_id: Optional[TableId]
    customer_id: Optional[CustomerId]
    total_amount: Decimal
    created_at: datetime
