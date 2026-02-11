# Scalable Coupon-Testing Automation System (Python)

## 1) Project folder structure

```text
.
├── coupon_tester/
│   ├── __init__.py
│   ├── browser.py           # Playwright flows (open product, cart, apply coupon, read prices)
│   ├── config.py            # Environment-based configuration (selectors, DB, rate limit)
│   ├── db.py                # PostgreSQL connection lifecycle
│   ├── logging_config.py    # JSON structured logging setup
│   ├── main.py              # Application entrypoint
│   ├── models.py            # Dataclasses for Product/Coupon/Result
│   ├── rate_limiter.py      # Request pacing
│   ├── repository.py        # SQL read/write operations
│   └── service.py           # Orchestration and failure handling
├── sql/
│   └── schema.sql           # Database schema for products, coupons, runs, results
├── docs/
│   └── automation_design.md # This design document
└── requirements.txt
```

---

## 2) `requirements.txt`

Dependencies are pinned in `requirements.txt`:

- `playwright` for browser automation
- `psycopg[binary]` for PostgreSQL
- `structlog` for structured logs
- `pydantic` + `pydantic-settings` + `python-dotenv` for config
- `tenacity` included for optional retries in future extensions

---

## 3) Main script

Run:

```bash
python -m coupon_tester.main
```

The script bootstraps:
1. Structured logging
2. Settings from environment variables
3. PostgreSQL connection
4. Playwright browser context
5. Coupon-testing service orchestration

---

## 4) Database schema

The schema in `sql/schema.sql` includes:
- `products`: source product URLs to test
- `coupons`: active coupon codes
- `test_runs`: metadata for each execution batch
- `coupon_test_results`: per product-coupon outcome and price deltas

This supports replayability, idempotent upserts, and historical tracking.

---

## 5) Workflow and scalability notes

### End-to-end flow
1. **Read product URLs from DB** using `CouponRepository.fetch_active_products`.
2. **Open each product page** in Playwright (`BrowserAutomation._open_product`).
3. **Add to cart** using site-specific selector and move to cart URL.
4. **Apply coupon** via input + apply button selectors.
5. **Capture final price** and initial price from configurable selectors.
6. **Store results in DB** in bulk (`save_results`) with upsert behavior.
7. **Graceful failure handling**:
   - Product/coupon-level errors are recorded as `status='failed'`.
   - Run-level errors mark the run as `failed` with notes.
8. **Rate limiting** via `RateLimiter.wait()` before each product/coupon test.

### Why this is scalable
- **Modular architecture**: browser logic, orchestration, DB access, rate limiting, and settings are separated.
- **Batch result writes**: reduces DB overhead compared with row-by-row commits.
- **Run tracking**: makes audits and backfills straightforward.
- **Configurable selectors**: supports multiple stores without code rewrites.
- **Structured logs**: machine-readable logs for centralized observability.

### Environment variables (example)

```env
DB_DSN=postgresql://user:password@localhost:5432/coupons
HEADLESS=true
RATE_LIMIT_PER_SECOND=1
NAVIGATION_TIMEOUT_MS=30000

ADD_TO_CART_SELECTOR=button.add-to-cart
CART_URL=https://store.example.com/cart
COUPON_INPUT_SELECTOR=input[name='coupon']
COUPON_APPLY_SELECTOR=button.apply-coupon
INITIAL_PRICE_SELECTOR=.order-subtotal .value
FINAL_PRICE_SELECTOR=.order-total .value
CURRENCY=USD
```

> Note: No captcha bypass or anti-bot circumvention logic is implemented.
