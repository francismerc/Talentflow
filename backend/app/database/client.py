from supabase import AsyncClient, acreate_client

from app.core.config import get_settings

_supabase_client: AsyncClient | None = None


class DatabaseConfigurationError(RuntimeError):
    """Raised when required database configuration is missing."""


async def get_supabase_client() -> AsyncClient:
    """Return a cached backend Supabase client using the secret key."""
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    settings = get_settings()
    secret_key = (
        settings.supabase_secret_key.get_secret_value()
        if settings.supabase_secret_key
        else ""
    )
    if not settings.supabase_url or not secret_key:
        raise DatabaseConfigurationError(
            "SUPABASE_URL and SUPABASE_SECRET_KEY must be configured."
        )

    _supabase_client = await acreate_client(settings.supabase_url, secret_key)
    return _supabase_client


async def get_supabase_auth_client() -> AsyncClient:
    """Return an isolated public client for validating one request's token."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise DatabaseConfigurationError(
            "SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be configured."
        )

    return await acreate_client(
        settings.supabase_url,
        settings.supabase_publishable_key,
    )
