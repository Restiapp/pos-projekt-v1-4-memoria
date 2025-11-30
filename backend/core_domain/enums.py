from enum import Enum

class OrderStatus(str, Enum):
    """
    Rendelés státuszok.
    Keys: English (Code)
    Values: Hungarian (Database)
    """
    OPEN = "NYITOTT"
    IN_PROGRESS = "FELDOLGOZVA" # Matches service_orders schema
    CLOSED = "LEZART"
    CANCELLED = "SZTORNÓ"

class OrderType(str, Enum):
    """
    Rendelés típusok.
    """
    DINE_IN = "Helyben"
    TAKEAWAY = "Elvitel"
    DELIVERY = "Kiszállítás"

class KdsState(str, Enum):
    """
    KDS Jegy státuszok.
    """
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    URGENT = "URGENT"
    READY = "READY"
    TAKEN = "TAKEN"
    CANCELLED = "CANCELLED"

class PaymentMethod(str, Enum):
    """
    Fizetési módok.
    """
    CASH = "Készpénz"
    CARD = "Bankkártya"
    SZEP_CARD = "SZÉP kártya"
    TRANSFER = "Átutalás"
    LOYALTY = "Hűségpont"

class VatRate(str, Enum):
    """
    ÁFA kulcsok.
    """
    VAT_27 = "27.00"
    VAT_5 = "5.00"

class RoomType(str, Enum):
    """
    Helyiség típusok.
    """
    BAR = "BAR"
    INDOOR = "INDOOR"
    TERRACE_SMOKING = "TERRACE_SMOKING"
    TERRACE_NONSMOKING = "TERRACE_NONSMOKING"
    VIP = "VIP"

class TableShape(str, Enum):
    """
    Asztal formák.
    """
    ROUND = "ROUND"
    SQUARE = "SQUARE"
    RECTANGLE = "RECTANGLE"

class ServiceRound(int, Enum):
    """
    Szerviz hullámok (D5).
    """
    IMMEDIATE = 1 # Red
    NEXT = 2      # Yellow
    LAST = 3      # Unmarked
