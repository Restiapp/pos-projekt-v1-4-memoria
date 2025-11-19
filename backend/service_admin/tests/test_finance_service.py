"""
Unit Tests - FinanceService
Module 8 (A8): Cash Drawer and Daily Closure API

Teszteli a következő funkciókat:
- Készpénz befizetés (deposit)
- Készpénz kivétel (withdraw)
- Napi zárás létrehozása és bevétel aggregálás
"""

import pytest
from decimal import Decimal
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.service_admin.models.database import Base
from backend.service_admin.models.finance import (
    CashMovement,
    CashMovementType,
    DailyClosure,
    ClosureStatus
)
from backend.service_admin.models.employee import Employee
from backend.service_admin.services.finance_service import FinanceService
from backend.service_orders.models.order import Order
from backend.service_orders.models.payment import Payment


# ============================================================================
# Test Database Setup (In-Memory SQLite)
# ============================================================================

@pytest.fixture(scope="function")
def db_session():
    """
    Creates an in-memory SQLite database for testing.
    Each test gets a fresh database.
    """
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def finance_service(db_session: Session):
    """Creates a FinanceService instance with test database."""
    return FinanceService(db_session)


@pytest.fixture(scope="function")
def test_employee(db_session: Session):
    """Creates a test employee."""
    employee = Employee(
        name="Test Employee",
        username="testuser",
        pin_code_hash="$2b$12$test_hash",  # Dummy hash
        email="test@example.com",
        is_active=True
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee


# ============================================================================
# Unit Tests - Cash Deposit (Befizetés)
# ============================================================================

def test_record_cash_deposit_success(finance_service: FinanceService, test_employee: Employee):
    """Test: Sikeres készpénz befizetés rögzítése."""
    # Given
    amount = Decimal("5000.00")
    description = "Nyitó egyenleg"

    # When
    movement = finance_service.record_cash_deposit(
        amount=amount,
        description=description,
        employee_id=test_employee.id
    )

    # Then
    assert movement is not None
    assert movement.id is not None
    assert movement.movement_type == CashMovementType.CASH_IN
    assert movement.amount == amount
    assert movement.description == description
    assert movement.employee_id == test_employee.id
    assert movement.created_at is not None


def test_record_cash_deposit_negative_amount_fails(finance_service: FinanceService):
    """Test: Negatív összeggel történő befizetés hibát dob."""
    # Given
    amount = Decimal("-100.00")

    # When / Then
    with pytest.raises(ValueError, match="pozitívnak kell lennie"):
        finance_service.record_cash_deposit(amount=amount)


def test_record_cash_deposit_zero_amount_fails(finance_service: FinanceService):
    """Test: Nulla összeggel történő befizetés hibát dob."""
    # Given
    amount = Decimal("0.00")

    # When / Then
    with pytest.raises(ValueError, match="pozitívnak kell lennie"):
        finance_service.record_cash_deposit(amount=amount)


def test_record_cash_deposit_updates_balance(finance_service: FinanceService):
    """Test: Befizetés után az egyenleg nő."""
    # Given
    initial_balance = finance_service.get_current_cash_balance()
    deposit_amount = Decimal("10000.00")

    # When
    finance_service.record_cash_deposit(amount=deposit_amount)

    # Then
    final_balance = finance_service.get_current_cash_balance()
    assert final_balance == initial_balance + deposit_amount


# ============================================================================
# Unit Tests - Cash Withdrawal (Kivétel)
# ============================================================================

def test_record_cash_withdrawal_success(finance_service: FinanceService, test_employee: Employee):
    """Test: Sikeres készpénz kivétel rögzítése."""
    # Given - Először befizetünk, hogy legyen egyenleg
    finance_service.record_cash_deposit(amount=Decimal("10000.00"))

    withdrawal_amount = Decimal("2000.00")
    description = "Költségek kifizetése"

    # When
    movement = finance_service.record_cash_withdrawal(
        amount=withdrawal_amount,
        description=description,
        employee_id=test_employee.id
    )

    # Then
    assert movement is not None
    assert movement.id is not None
    assert movement.movement_type == CashMovementType.CASH_OUT
    assert movement.amount == -withdrawal_amount  # Negatív érték!
    assert movement.description == description
    assert movement.employee_id == test_employee.id


def test_record_cash_withdrawal_insufficient_balance_fails(finance_service: FinanceService):
    """Test: Nincs elegendő egyenleg a kivételhez - hiba."""
    # Given - Egyenleg 0
    current_balance = finance_service.get_current_cash_balance()
    assert current_balance == Decimal("0.00")

    withdrawal_amount = Decimal("1000.00")

    # When / Then
    with pytest.raises(ValueError, match="Nincs elegendő készpénz"):
        finance_service.record_cash_withdrawal(amount=withdrawal_amount)


def test_record_cash_withdrawal_negative_amount_fails(finance_service: FinanceService):
    """Test: Negatív összeggel történő kivétel hibát dob."""
    # Given
    amount = Decimal("-100.00")

    # When / Then
    with pytest.raises(ValueError, match="pozitívnak kell lennie"):
        finance_service.record_cash_withdrawal(amount=amount)


def test_record_cash_withdrawal_updates_balance(finance_service: FinanceService):
    """Test: Kivétel után az egyenleg csökken."""
    # Given - Befizetünk 10000 Ft-ot
    finance_service.record_cash_deposit(amount=Decimal("10000.00"))
    initial_balance = finance_service.get_current_cash_balance()

    withdrawal_amount = Decimal("3000.00")

    # When
    finance_service.record_cash_withdrawal(amount=withdrawal_amount)

    # Then
    final_balance = finance_service.get_current_cash_balance()
    assert final_balance == initial_balance - withdrawal_amount


# ============================================================================
# Unit Tests - Cash Balance (Egyenleg)
# ============================================================================

def test_get_current_cash_balance_initial_zero(finance_service: FinanceService):
    """Test: Kezdeti egyenleg nulla."""
    # When
    balance = finance_service.get_current_cash_balance()

    # Then
    assert balance == Decimal("0.00")


def test_get_current_cash_balance_multiple_movements(finance_service: FinanceService):
    """Test: Egyenleg számítás több pénzmozgással."""
    # Given - Több tranzakció
    finance_service.record_cash_deposit(amount=Decimal("5000.00"))
    finance_service.record_cash_deposit(amount=Decimal("3000.00"))
    finance_service.record_cash_withdrawal(amount=Decimal("1500.00"))
    finance_service.record_cash_deposit(amount=Decimal("2500.00"))

    # When
    balance = finance_service.get_current_cash_balance()

    # Then
    # 5000 + 3000 - 1500 + 2500 = 9000
    assert balance == Decimal("9000.00")


# ============================================================================
# Unit Tests - Cash Movements Query (Mozgások lekérdezése)
# ============================================================================

def test_get_cash_movements_all(finance_service: FinanceService):
    """Test: Összes pénzmozgás lekérdezése."""
    # Given - 3 tranzakció
    finance_service.record_cash_deposit(amount=Decimal("1000.00"))
    finance_service.record_cash_deposit(amount=Decimal("2000.00"))
    finance_service.record_cash_withdrawal(amount=Decimal("500.00"))

    # When
    movements = finance_service.get_cash_movements()

    # Then
    assert len(movements) == 3


def test_get_cash_movements_by_type(finance_service: FinanceService):
    """Test: Pénzmozgások szűrése típus szerint."""
    # Given
    finance_service.record_cash_deposit(amount=Decimal("1000.00"))
    finance_service.record_cash_deposit(amount=Decimal("2000.00"))
    finance_service.record_cash_withdrawal(amount=Decimal("500.00"))

    # When
    deposits = finance_service.get_cash_movements(movement_type=CashMovementType.CASH_IN)
    withdrawals = finance_service.get_cash_movements(movement_type=CashMovementType.CASH_OUT)

    # Then
    assert len(deposits) == 2
    assert len(withdrawals) == 1


def test_get_cash_movements_pagination(finance_service: FinanceService):
    """Test: Pénzmozgások lapozása."""
    # Given - 5 tranzakció
    for i in range(5):
        finance_service.record_cash_deposit(amount=Decimal(f"{1000 * (i+1)}.00"))

    # When
    page1 = finance_service.get_cash_movements(limit=2, offset=0)
    page2 = finance_service.get_cash_movements(limit=2, offset=2)

    # Then
    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id


# ============================================================================
# Unit Tests - Daily Closure Basic (Napi zárás alapok)
# ============================================================================

def test_create_daily_closure_success(finance_service: FinanceService, test_employee: Employee):
    """Test: Sikeres napi zárás létrehozása."""
    # Given
    opening_balance = Decimal("5000.00")
    notes = "Test closure"

    # When
    closure = finance_service.create_daily_closure(
        opening_balance=opening_balance,
        closed_by_employee_id=test_employee.id,
        notes=notes
    )

    # Then
    assert closure is not None
    assert closure.id is not None
    assert closure.opening_balance == opening_balance
    assert closure.status == ClosureStatus.OPEN
    assert closure.notes == notes
    assert closure.closed_by_employee_id == test_employee.id
    assert closure.created_at is not None


def test_create_daily_closure_duplicate_fails(finance_service: FinanceService):
    """Test: Már létező napi zárás esetén hiba."""
    # Given - Már van egy zárás ma
    finance_service.create_daily_closure(opening_balance=Decimal("5000.00"))

    # When / Then
    with pytest.raises(ValueError, match="Már van nyitott pénztárzárás"):
        finance_service.create_daily_closure(opening_balance=Decimal("6000.00"))


def test_get_daily_closure_by_date_success(finance_service: FinanceService):
    """Test: Napi zárás lekérdezése dátum alapján."""
    # Given
    today = date.today()
    closure = finance_service.create_daily_closure(opening_balance=Decimal("1000.00"))

    # When
    found_closure = finance_service.get_daily_closure_by_date(today)

    # Then
    assert found_closure is not None
    assert found_closure.id == closure.id


def test_get_daily_closure_by_date_not_found(finance_service: FinanceService):
    """Test: Nem létező dátumra None-t ad vissza."""
    # Given
    yesterday = date.today() - timedelta(days=1)

    # When
    found_closure = finance_service.get_daily_closure_by_date(yesterday)

    # Then
    assert found_closure is None


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
