from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Product:
    id: int
    product_url: str
    sku: Optional[str] = None


@dataclass(frozen=True)
class Coupon:
    id: int
    code: str


@dataclass(frozen=True)
class PriceCapture:
    initial_price: Decimal
    final_price: Decimal
    currency: str


@dataclass(frozen=True)
class CouponTestResult:
    run_id: str
    product_id: int
    coupon_id: int
    status: str
    initial_price: Optional[Decimal] = None
    final_price: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    currency: Optional[str] = None
    error_message: Optional[str] = None
