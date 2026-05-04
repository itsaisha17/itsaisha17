-- Product inputs for coupon testing.
CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    sku TEXT UNIQUE,
    product_url TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Coupon codes to test.
CREATE TABLE IF NOT EXISTS coupons (
    id BIGSERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- One execution batch for observability and replay.
CREATE TABLE IF NOT EXISTS test_runs (
    id UUID PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    notes TEXT
);

-- Result per product/coupon pair.
CREATE TABLE IF NOT EXISTS coupon_test_results (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    coupon_id BIGINT NOT NULL REFERENCES coupons(id) ON DELETE CASCADE,
    currency TEXT,
    initial_price NUMERIC(12,2),
    final_price NUMERIC(12,2),
    discount_amount NUMERIC(12,2),
    discount_percent NUMERIC(7,4),
    status TEXT NOT NULL CHECK (status IN ('success', 'coupon_rejected', 'failed')),
    error_message TEXT,
    tested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (run_id, product_id, coupon_id)
);

CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_coupons_active ON coupons(is_active);
CREATE INDEX IF NOT EXISTS idx_coupon_results_run_id ON coupon_test_results(run_id);
