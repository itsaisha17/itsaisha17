from coupon_tester.browser import BrowserAutomation
from coupon_tester.config import load_settings
from coupon_tester.db import get_connection
from coupon_tester.logging_config import configure_logging
from coupon_tester.rate_limiter import RateLimiter
from coupon_tester.repository import CouponRepository
from coupon_tester.service import CouponTestingService


def main() -> None:
    configure_logging()
    settings = load_settings()

    with get_connection(settings.db_dsn) as conn, BrowserAutomation(settings) as browser:
        repository = CouponRepository(conn)
        limiter = RateLimiter(settings.rate_limit_per_second)
        service = CouponTestingService(repository, browser, limiter)
        service.run()


if __name__ == "__main__":
    main()
