import pytest
from pydantic import ValidationError

from app.core.config import Settings


def production_settings(**overrides: object) -> Settings:
    values = {
        "app_env": "production",
        "app_debug": False,
        "frontend_url": "https://talentflow.vercel.app",
        "backend_cors_origins": "https://talentflow.vercel.app",
        "supabase_url": "https://example.supabase.co",
        "supabase_publishable_key": "sb_publishable_example",
        "supabase_secret_key": "sb_secret_example",
    }
    values.update(overrides)
    return Settings(**values)


def test_valid_production_settings_are_accepted() -> None:
    settings = production_settings()

    assert settings.cors_origins == ["https://talentflow.vercel.app"]


def test_cors_origins_remove_trailing_slashes() -> None:
    settings = production_settings(
        frontend_url="https://talentflow.vercel.app/",
        backend_cors_origins="https://talentflow.vercel.app/",
    )

    assert settings.cors_origins == ["https://talentflow.vercel.app"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("app_debug", True),
        ("frontend_url", "http://talentflow.vercel.app"),
        ("backend_cors_origins", "*"),
        ("backend_cors_origins", "https://another.example.com"),
    ],
)
def test_unsafe_production_settings_are_rejected(
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError):
        production_settings(**{field: value})
