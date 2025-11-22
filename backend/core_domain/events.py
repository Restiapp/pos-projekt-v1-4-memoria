from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from .enums import OrderStatus, KdsState

@dataclass
class DomainEvent:
    event_id: str
    occurred_at: datetime

@dataclass
class OrderPlaced(DomainEvent):
    order_id: int
    table_id: Optional[int]
    order_type: str

@dataclass
class OrderItemAdded(DomainEvent):
    order_id: int
    product_id: int
    quantity: int
    name: str

@dataclass
class OrderSentToKds(DomainEvent):
    order_id: int
    items: List[int] # List of OrderItem IDs

@dataclass
class KdsTicketStatusChanged(DomainEvent):
    ticket_id: int
    old_status: KdsState
    new_status: KdsState

@dataclass
class PaymentCaptured(DomainEvent):
    order_id: int
    amount: float
    method: str
