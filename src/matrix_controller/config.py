"""Runtime configuration, from environment variables and an optional .env file.

Every knob is documented in the README's Configuration table — keep in sync.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", populate_by_name=True
    )

    train_api_url: str | None = Field(default=None, validation_alias="TRAIN_API_URL")
    polling_interval: float = Field(default=15.0, gt=0, validation_alias="POLLING_INTERVAL")
    source: Literal["auto", "api", "demo"] = Field(default="auto", validation_alias="MATRIX_SOURCE")
    driver: Literal["auto", "hardware", "terminal"] = Field(
        default="auto", validation_alias="MATRIX_DRIVER"
    )
    hardware_profile: str = Field(default="auto", validation_alias="MATRIX_HARDWARE_PROFILE")

    # Single-value overrides on top of the hardware profile.
    brightness: int | None = Field(default=None, ge=1, le=100, validation_alias="MATRIX_BRIGHTNESS")
    gpio_slowdown: int | None = Field(
        default=None, ge=0, le=10, validation_alias="MATRIX_GPIO_SLOWDOWN"
    )
    pwm_bits: int | None = Field(default=None, ge=1, le=11, validation_alias="MATRIX_PWM_BITS")
    pwm_lsb_nanoseconds: int | None = Field(
        default=None, ge=50, le=3000, validation_alias="MATRIX_PWM_LSB_NANOSECONDS"
    )
    refresh_rate_limit: int | None = Field(
        default=None, ge=1, validation_alias="MATRIX_REFRESH_RATE_LIMIT"
    )

    def resolved_source(self) -> Literal["api", "demo"]:
        if self.source != "auto":
            return self.source
        return "api" if self.train_api_url else "demo"

    def matrix_overrides(self) -> dict[str, int]:
        """Overrides keyed by RGBMatrixOptions attribute name."""
        pairs = {
            "brightness": self.brightness,
            "gpio_slowdown": self.gpio_slowdown,
            "pwm_bits": self.pwm_bits,
            "pwm_lsb_nanoseconds": self.pwm_lsb_nanoseconds,
            "limit_refresh_rate_hz": self.refresh_rate_limit,
        }
        return {key: value for key, value in pairs.items() if value is not None}
