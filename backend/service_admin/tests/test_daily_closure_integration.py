"""
Integration Tests - Daily Closure Revenue Aggregation
Module 8 (A8): Cash Drawer and Daily Closure API

Integációs teszt amely ellenőrzi hogy a POST /daily-closures végpont
helyesen aggregálja a lezárt rendelésekből származó bevételeket
fizetési módok szerint.

Teszt forgatókönyv:
1. Létrehozunk több lezárt rendelést különböző fizetési módokkal
2. Hozzáadunk készpénzmozgásokat
3. Létrehozunk egy napi zárást
4. Ellenőrizzük hogy az összesítés helyes-e
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.service_admin.models.database import Base
from backend.service_admin.models.finance import DailyClosure, ClosureStatus
from backend.service_admin.models.employee import Employee
from backend.service_admin.services.finance_service import FinanceService
from backend.service_orders.models.order import Order
from backend.service_orders.models.payment import Payment


# ============================================================================
# Test Database Setup
# ============================================================================

@pytest.fixture(scope="function")
def db_session():
    """
    Creates an in-memory SQLite database for integration testing.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
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
        name="Test Manager",
        username="manager",
        pin_code_hash="$2b$12$test_hash",
        email="manager@example.com",
        is_active=True
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee


# ============================================================================
# Helper Functions
# ============================================================================

def create_closed_order_with_payment(
    db_session: Session,
    order_type: str,
    total_amount: Decimal,
    payment_method: str,
    created_at: datetime = None
) -> Order:
    """
    Helper: Létrehoz egy LEZART státuszú rendelést SIKERES fizetéssel.

    Args:
        db_session: Database session
        order_type: Rendelés típusa ('Helyben', 'Elvitel', 'Kiszállítás')
        total_amount: Rendelés összege
        payment_method: Fizetési mód ('KESZPENZ', 'KARTYA', 'SZEP_KARTYA')
        created_at: Létrehozás időpontja (opcionális)

    Returns:
        Order: Létrehozott rendelés
    """
    # Rendelés létrehozása
    order = Order(
        order_type=order_type,
        status='LEZART',
        total_amount=total_amount,
        final_vat_rate=Decimal("27.00"),
        created_at=created_at or datetime.now()
    )
    db_session.add(order)
    db_session.flush()  # Get order.id

    # Fizetés létrehozása
    payment = Payment(
        order_id=order.id,
        payment_method=payment_method,
        amount=total_amount,
        status='SIKERES',
        created_at=created_at or datetime.now()
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(order)

    return order


# ============================================================================
# Integration Tests - Daily Closure Revenue Aggregation
# ============================================================================

def test_daily_closure_aggregates_cash_payments(
    finance_service: FinanceService,
    db_session: Session,
    test_employee: Employee
):
    """
    Test: Napi zárás helyesen aggregálja a készpénzes fizetéseket.
    """
    # Given - Létrehozunk 3 lezárt rendelést készpénzes fizetéssel
    create_closed_order_with_payment(
        db_session,
        order_type='Helyben',
        total_amount=Decimal("5000.00"),
        payment_method='KESZPENZ'
    )
    create_closed_order_with_payment(
        db_session,
        order_type='Elvitel',
        total_amount=Decimal("3500.00"),
        payment_method='KESZPENZ'
    )
    create_closed_order_with_payment(
        db_session,
        order_type='Kiszállítás',
        total_amount=Decimal("7200.00"),
        payment_method='KESZPENZ'
    )

    # When - Létrehozunk egy napi zárást
    closure = finance_service.create_daily_closure(
        opening_balance=Decimal("10000.00"),
        closed_by_employee_id=test_employee.id,
        notes="Test closure - cash only"
    )

    # Then - Ellenőrizzük az összesítést
    assert closure.total_cash == Decimal("15700.00")  # 5000 + 3500 + 7200
    assert closure.total_card == Decimal("0.00")
    assert closure.total_szep_card == Decimal("0.00")
    assert closure.total_revenue == Decimal("15700.00")


def test_daily_closure_aggregates_card_payments(
    finance_service: FinanceService,
    db_session: Session,
    test_employee: Employee
):
    """
    Test: Napi zárás helyesen aggregálja a bankkártyás fizetéseket.
    """
    # Given - Létrehozunk 2 lezárt rendelést bankkártyás fizetéssel
    create_closed_order_with_payment(
        db_session,
        order_type='Helyben',
        total_amount=Decimal("12000.00"),
        payment_method='KARTYA'
    )
    create_closed_order_with_payment(
        db_session,
        order_type='Helyben',
        total_amount=Decimal("8500.00"),
        payment_method='KARTYA'
    )

    # When
    closure = finance_service.create_daily_closure(
        opening_balance=Decimal("5000.00"),
        closed_by_employee_id=test_employee.id
    )

    # Then
    assert closure.total_cash == Decimal("0.00")
    assert closure.total_card == Decimal("20500.00")  # 12000 + 8500
    assert closure.total_szep_card == Decimal("0.00")
    assert closure.total_revenue == Decimal("20500.00")


def test_daily_closure_aggregates_szep_card_payments(
    finance_service: FinanceService,
    db_session: Session,
    test_employee: Employee
):
    """
    Test: Napi zárás helyesen aggregálja a SZÉP kártyás fizetéseket.
    """
    # Given - Létrehozunk 2 lezárt rendelést SZÉP kártyás fizetéssel
    create_closed_order_with_payment(
        db_session,
        order_type='Helyben',
        total_amount=Decimal("6000.00"),
        payment_method='SZEP_KARTYA'
    )
    create_closed_order_with_payment(
        db_session,
        order_type='Elvitel',
        total_amount=Decimal("4500.00"),
        payment_method='SZEP_KARTYA'
    )

    # When
    closure = finance_service.create_daily_closure(
        opening_balance=Decimal("3000.00"),
        closed_by_employee_id=test_employee.id
    )

    # Then
    assert closure.total_cash == Decimal("0.00")
    assert closure.total_card == Decimal("0.00")
    assert closure.total_szep_card == Decimal("10500.00")  # 6000 + 4500
    assert closure.total_revenue == Decimal("10500.00")


def test_daily_closure_aggregates_mixed_payment_methods(
    finance_service: FinanceService,
    db_session: Session,
    test_employee: Employee
):
    """
    Test: Napi zárás helyesen aggregálja a vegyes fizetési módokat.

    Ez a FŐBB integrációs teszt - többféle fizetési móddal.
    """
    # Given - Létrehozunk különböző fizetési módokkal rendeléseket
    create_closed_order_with_payment(
        db_session,
        order_type='Helyben',
        total_amount=Decimal("10000.00"),
        payment_method='KESZPENZ'
    )
    create_closed_order_with_payment(
        db_session,
        order_type='Helyben',
        total_amount=Decimal("15000.00"),
        payment_method='KARTYA'
    )
    create_closed_order_with_payment(
        db_session,
        order_type='Elvitel',
        total_amount=Decimal("5000.00"),
        payment_method='SZEP_KARTYA'
    )
    create_closed_order_with_payment(
        db_session,
        order_type='Kiszállítás',
        total_amount=Decimal("8500.00"),
        payment_method='KESZPENZ'
    )
    create_closed_order_with_payment(
        db_session,
        order_type='Helyben',
        total_amount=Decimal("12000.00"),
        payment_method='KARTYA'
    )

    # Hozzáadunk készpénzmozgásokat is
    finance_service.record_cash_deposit(
        amount=Decimal("2000.00"),
        description="Nyitó kassza"
    )
    finance_service.record_cash_withdrawal(
        amount=Decimal("500.00"),
        description="Költségek"
    )

    # When - Létrehozunk egy napi zárást
    closure = finance_service.create_daily_closure(
        opening_balance=Decimal("5000.00"),
        closed_by_employee_id=test_employee.id,
        notes="Full day closure with mixed payments"
    )

    # Then - Ellenőrizzük az összesítést
    assert closure.total_cash == Decimal("18500.00")  # 10000 + 8500
    assert closure.total_card == Decimal("27000.00")  # 15000 + 12000
    assert closure.total_szep_card == Decimal("5000.00")  # 5000
    assert closure.total_revenue == Decimal("50500.00")  # 18500 + 27000 + 5000
    assert closure.opening_balance == Decimal("5000.00")
    assert closure.status == ClosureStatus.OPEN


def test_daily_closure_ignores_non_lezart_orders(
    finance_service: FinanceService,
    db_session: Session,
    test_employee: Employee
):
    """
    Test: Napi zárás NEM számítja az OPEN/FELDOLGOZVA státuszú rendeléseket.
    """
    # Given - Létrehozunk LEZART rendelést
    create_closed_order_with_payment(
        db_session,
        order_type='Helyben',
        total_amount=Decimal("5000.00"),
        payment_method='KESZPENZ'
    )

    # Létrehozunk NYITOTT rendelést (nem kerül aggregálásra)
    order_open = Order(
        order_type='Helyben',
        status='NYITOTT',
        total_amount=Decimal("3000.00"),
        final_vat_rate=Decimal("27.00")
    )
    db_session.add(order_open)
    db_session.flush()

    payment_open = Payment(
        order_id=order_open.id,
        payment_method='KESZPENZ',
        amount=Decimal("3000.00"),
        status='SIKERES'
    )
    db_session.add(payment_open)
    db_session.commit()

    # When
    closure = finance_service.create_daily_closure(
        opening_balance=Decimal("1000.00"),
        closed_by_employee_id=test_employee.id
    )

    # Then - Csak a LEZART rendelés számít
    assert closure.total_cash == Decimal("5000.00")  # NEM 8000!
    assert closure.total_revenue == Decimal("5000.00")


def test_daily_closure_ignores_failed_payments(
    finance_service: FinanceService,
    db_session: Session,
    test_employee: Employee
):
    """
    Test: Napi zárás NEM számítja a sikertelen fizetéseket.
    """
    # Given - Létrehozunk LEZART rendelést SIKERES fizetéssel
    create_closed_order_with_payment(
        db_session,
        order_type='Helyben',
        total_amount=Decimal("5000.00"),
        payment_method='KESZPENZ'
    )

    # Létrehozunk LEZART rendelést de SIKERTELEN fizetéssel
    order_failed = Order(
        order_type='Helyben',
        status='LEZART',
        total_amount=Decimal("3000.00"),
        final_vat_rate=Decimal("27.00")
    )
    db_session.add(order_failed)
    db_session.flush()

    payment_failed = Payment(
        order_id=order_failed.id,
        payment_method='KESZPENZ',
        amount=Decimal("3000.00"),
        status='SIKERTELEN'
    )
    db_session.add(payment_failed)
    db_session.commit()

    # When
    closure = finance_service.create_daily_closure(
        opening_balance=Decimal("1000.00"),
        closed_by_employee_id=test_employee.id
    )

    # Then - Csak a SIKERES fizetés számít
    assert closure.total_cash == Decimal("5000.00")  # NEM 8000!
    assert closure.total_revenue == Decimal("5000.00")


def test_daily_closure_with_no_orders(
    finance_service: FinanceService,
    test_employee: Employee
):
    """
    Test: Napi zárás üres napra (nincs rendelés) - minden nullázva.
    """
    # Given - Nincs rendelés

    # When
    closure = finance_service.create_daily_closure(
        opening_balance=Decimal("10000.00"),
        closed_by_employee_id=test_employee.id
    )

    # Then - Minden bevétel nulla
    assert closure.total_cash == Decimal("0.00")
    assert closure.total_card == Decimal("0.00")
    assert closure.total_szep_card == Decimal("0.00")
    assert closure.total_revenue == Decimal("0.00")
    assert closure.opening_balance == Decimal("10000.00")


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
