from __future__ import annotations

import re
from decimal import Decimal

from playwright.sync_api import Browser, Page, sync_playwright

from coupon_tester.config import Settings
from coupon_tester.models import PriceCapture


class BrowserAutomation:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._playwright = None
        self._browser: Browser | None = None

    def __enter__(self) -> "BrowserAutomation":
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.settings.headless)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def test_coupon(self, product_url: str, coupon_code: str) -> PriceCapture:
        if not self._browser:
            raise RuntimeError("BrowserAutomation must be used as a context manager")

        context = self._browser.new_context()
        page = context.new_page()
        page.set_default_timeout(self.settings.navigation_timeout_ms)

        try:
            self._open_product(page, product_url)
            initial_price = self._get_price(page, self.settings.initial_price_selector)
            self._add_to_cart(page)
            self._apply_coupon(page, coupon_code)
            final_price = self._get_price(page, self.settings.final_price_selector)
            return PriceCapture(
                initial_price=initial_price,
                final_price=final_price,
                currency=self.settings.currency,
            )
        finally:
            context.close()

    def _open_product(self, page: Page, product_url: str) -> None:
        page.goto(product_url, wait_until="domcontentloaded")

    def _add_to_cart(self, page: Page) -> None:
        page.click(self.settings.add_to_cart_selector)
        page.goto(self.settings.cart_url, wait_until="domcontentloaded")

    def _apply_coupon(self, page: Page, coupon_code: str) -> None:
        page.fill(self.settings.coupon_input_selector, coupon_code)
        page.click(self.settings.coupon_apply_selector)

    @staticmethod
    def _parse_price(raw_value: str) -> Decimal:
        match = re.search(r"\d+(?:,\d{3})*(?:\.\d+)?", raw_value)
        if not match:
            raise ValueError(f"Unable to parse price value from '{raw_value}'")
        return Decimal(match.group(0).replace(",", ""))

    def _get_price(self, page: Page, selector: str) -> Decimal:
        raw_value = page.locator(selector).first.inner_text().strip()
        return self._parse_price(raw_value)
