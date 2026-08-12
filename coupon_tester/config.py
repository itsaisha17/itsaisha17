from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_dsn: str = Field(alias="DB_DSN")
    headless: bool = Field(default=True, alias="HEADLESS")
    navigation_timeout_ms: int = Field(default=30_000, alias="NAVIGATION_TIMEOUT_MS")
    rate_limit_per_second: float = Field(default=1.0, alias="RATE_LIMIT_PER_SECOND")

    # Selectors are configurable per target site.
    add_to_cart_selector: str = Field(alias="ADD_TO_CART_SELECTOR")
    cart_url: str = Field(alias="CART_URL")
    coupon_input_selector: str = Field(alias="COUPON_INPUT_SELECTOR")
    coupon_apply_selector: str = Field(alias="COUPON_APPLY_SELECTOR")
    initial_price_selector: str = Field(alias="INITIAL_PRICE_SELECTOR")
    final_price_selector: str = Field(alias="FINAL_PRICE_SELECTOR")
    currency: str = Field(default="USD", alias="CURRENCY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def load_settings() -> Settings:
    return Settings()
