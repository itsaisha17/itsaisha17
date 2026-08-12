from __future__ import annotations

from typing import Iterable

from psycopg import Connection

from coupon_tester.models import Coupon, CouponTestResult, Product


class CouponRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def fetch_active_products(self, limit: int = 100) -> list[Product]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, product_url, sku
                FROM products
                WHERE is_active = TRUE
                ORDER BY id
                LIMIT %s
                """,
                (limit,),
            )
            return [Product(id=row[0], product_url=row[1], sku=row[2]) for row in cur.fetchall()]

    def fetch_active_coupons(self) -> list[Coupon]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, code
                FROM coupons
                WHERE is_active = TRUE
                ORDER BY id
                """
            )
            return [Coupon(id=row[0], code=row[1]) for row in cur.fetchall()]

    def start_run(self, run_id: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO test_runs (id, status) VALUES (%s, 'running')",
                (run_id,),
            )

    def complete_run(self, run_id: str, status: str, notes: str | None = None) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE test_runs
                SET status = %s,
                    notes = %s,
                    finished_at = NOW()
                WHERE id = %s
                """,
                (status, notes, run_id),
            )

    def save_results(self, results: Iterable[CouponTestResult]) -> None:
        with self.conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO coupon_test_results (
                    run_id,
                    product_id,
                    coupon_id,
                    status,
                    initial_price,
                    final_price,
                    discount_amount,
                    discount_percent,
                    currency,
                    error_message
                )
                VALUES (%(run_id)s, %(product_id)s, %(coupon_id)s, %(status)s,
                        %(initial_price)s, %(final_price)s, %(discount_amount)s,
                        %(discount_percent)s, %(currency)s, %(error_message)s)
                ON CONFLICT (run_id, product_id, coupon_id)
                DO UPDATE
                    SET status = EXCLUDED.status,
                        initial_price = EXCLUDED.initial_price,
                        final_price = EXCLUDED.final_price,
                        discount_amount = EXCLUDED.discount_amount,
                        discount_percent = EXCLUDED.discount_percent,
                        currency = EXCLUDED.currency,
                        error_message = EXCLUDED.error_message,
                        tested_at = NOW();
                """,
                [
                    {
                        "run_id": result.run_id,
                        "product_id": result.product_id,
                        "coupon_id": result.coupon_id,
                        "status": result.status,
                        "initial_price": result.initial_price,
                        "final_price": result.final_price,
                        "discount_amount": result.discount_amount,
                        "discount_percent": result.discount_percent,
                        "currency": result.currency,
                        "error_message": result.error_message,
                    }
                    for result in results
                ],
            )
