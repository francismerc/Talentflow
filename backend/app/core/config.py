from functools import lru_cache
from urllib.parse import urlparse

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TalentFlow AI API"
    app_env: str = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    frontend_url: str = "http://localhost:3000"
    backend_cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    supabase_url: str | None = None
    supabase_publishable_key: str | None = None
    supabase_secret_key: SecretStr | None = None

    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_timeout_seconds: float = 30
    google_client_id: str | None = None
    google_client_secret: SecretStr | None = None
    google_redirect_uri: str | None = None
    google_oauth_state_secret: SecretStr | None = None
    google_token_encryption_key: SecretStr | None = None
    email_company_name: str = "TalentFlow AI"
    email_recruitment_team_name: str = "Talent Acquisition Team"
    email_reply_to: str | None = None
    email_careers_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip().rstrip("/")
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        if self.app_env.casefold() != "production":
            return self

        missing = [
            name
            for name, value in (
                ("SUPABASE_URL", self.supabase_url),
                ("SUPABASE_PUBLISHABLE_KEY", self.supabase_publishable_key),
                ("SUPABASE_SECRET_KEY", self.supabase_secret_key),
                ("FRONTEND_URL", self.frontend_url),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                "Missing production settings: " + ", ".join(missing)
            )
        if self.app_debug:
            raise ValueError("APP_DEBUG must be false in production.")
        if not self._is_https_url(self.frontend_url):
            raise ValueError("FRONTEND_URL must use HTTPS in production.")
        if not self._is_https_url(self.supabase_url or ""):
            raise ValueError("SUPABASE_URL must use HTTPS in production.")

        origins = self.cors_origins
        if not origins:
            raise ValueError(
                "BACKEND_CORS_ORIGINS must contain the production frontend URL."
            )
        if "*" in origins:
            raise ValueError(
                "Wildcard CORS origins are not allowed in production."
            )
        if self.frontend_url.rstrip("/") not in {
            origin.rstrip("/") for origin in origins
        }:
            raise ValueError(
                "BACKEND_CORS_ORIGINS must include FRONTEND_URL."
            )
        if any(not self._is_https_url(origin) for origin in origins):
            raise ValueError(
                "All production CORS origins must use HTTPS."
            )
        return self

    @staticmethod
    def _is_https_url(value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.netloc)


@lru_cache
def get_settings() -> Settings:
    return Settings()
