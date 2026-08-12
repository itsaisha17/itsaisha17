from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import structlog
from playwright.sync_api import Error as PlaywrightError

from coupon_tester.browser import BrowserAutomation
from coupon_tester.models import Coupon, CouponTestResult, PriceCapture, Product
from coupon_tester.rate_limiter import RateLimiter
from coupon_tester.repository import CouponRepository


class CouponTestingService:
    def __init__(
        self,
        repository: CouponRepository,
        browser: BrowserAutomation,
        limiter: RateLimiter,
    ):
        self.repository = repository
        self.browser = browser
        self.limiter = limiter
        self.logger = structlog.get_logger(__name__)

    def run(self) -> str:
        run_id = str(uuid4())
        self.repository.start_run(run_id)

        try:
            products = self.repository.fetch_active_products()
            coupons = self.repository.fetch_active_coupons()
            self.logger.info("run_started", run_id=run_id, product_count=len(products), coupon_count=len(coupons))

            results: list[CouponTestResult] = []
            for product in products:
                for coupon in coupons:
                    self.limiter.wait()
                    results.append(self._test_single(run_id, product, coupon))

                    if len(results) >= 100:
                        self.repository.save_results(results)
                        results.clear()

            if results:
                self.repository.save_results(results)

            self.repository.complete_run(run_id, status="completed")
            self.logger.info("run_completed", run_id=run_id)
            return run_id
        except Exception as exc:
            self.repository.complete_run(run_id, status="failed", notes=str(exc))
            self.logger.exception("run_failed", run_id=run_id, error=str(exc))
            raise

    def _test_single(self, run_id: str, product: Product, coupon: Coupon) -> CouponTestResult:
        log = self.logger.bind(run_id=run_id, product_id=product.id, coupon_code=coupon.code)
        try:
            capture = self.browser.test_coupon(product.product_url, coupon.code)
            discount_amount, discount_percent = self._discount(capture)
            status = "success" if capture.final_price < capture.initial_price else "coupon_rejected"

            log.info(
                "coupon_tested",
                status=status,
                initial_price=str(capture.initial_price),
                final_price=str(capture.final_price),
                discount_amount=str(discount_amount),
            )

            return CouponTestResult(
                run_id=run_id,
                product_id=product.id,
                coupon_id=coupon.id,
                status=status,
                initial_price=capture.initial_price,
                final_price=capture.final_price,
                discount_amount=discount_amount,
                discount_percent=discount_percent,
                currency=capture.currency,
            )

        except (PlaywrightError, ValueError, RuntimeError) as exc:
            log.warning("coupon_test_failed", error=str(exc))
            return CouponTestResult(
                run_id=run_id,
                product_id=product.id,
                coupon_id=coupon.id,
                status="failed",
                error_message=str(exc),
            )

    @staticmethod
    def _discount(capture: PriceCapture) -> tuple[Decimal, Decimal | None]:
        amount = (capture.initial_price - capture.final_price).quantize(Decimal("0.01"))
        if capture.initial_price == 0:
            return amount, None
        percent = ((amount / capture.initial_price) * Decimal("100")).quantize(Decimal("0.0001"))
        return amount, percent
