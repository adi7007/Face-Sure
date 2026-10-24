"""
Application configuration management.

Loads settings from environment variables and .env files using pydantic-settings.
All configuration values have sensible defaults for development.
"""

from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent
# Repository root (Facial Recognition/)
ROOT_DIR = BASE_DIR.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    app_name: str = "Facial Recognition Attendance System"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"

    # ── Server ───────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse comma-separated ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    # ── Database ─────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/face_attendance"
    database_echo: bool = False

    # ── Redis ────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── JWT Authentication ───────────────────────────────────────
    jwt_secret_key: str = "change-this-to-a-secure-random-string-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # ── Face Detection ───────────────────────────────────────────
    face_detection_confidence: float = 0.7
    face_detection_model: str = "mediapipe"

    # ── Face Quality ─────────────────────────────────────────────
    quality_blur_threshold: float = 100.0
    quality_min_face_size: int = 80
    quality_max_yaw: float = 30.0
    quality_max_pitch: float = 20.0
    quality_min_score: float = 0.5

    # ── Liveness Detection ───────────────────────────────────────
    liveness_threshold: float = 0.5
    liveness_model_path: str = "data/models/anti_spoof_models"

    # ── Face Recognition ─────────────────────────────────────────
    recognition_model: str = "buffalo_l"
    recognition_threshold: float = 0.4
    embedding_dimension: int = 512

    # ── File Storage ─────────────────────────────────────────────
    models_dir: str = "data/models"
    faces_dir: str = "data/faces"
    exports_dir: str = "data/exports"

    # ── Attendance Rules ─────────────────────────────────────────
    attendance_cooldown_seconds: int = 300
    attendance_session_max_duration_hours: int = 4

    # ── Security ─────────────────────────────────────────────────
    encryption_key: str = "change-this-to-a-32-byte-key-for-face-image-encryption"
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    @property
    def models_path(self) -> Path:
        """Absolute path to the models directory."""
        path = Path(self.models_dir)
        if not path.is_absolute():
            path = ROOT_DIR / path
        return path

    @property
    def faces_path(self) -> Path:
        """Absolute path to the faces directory."""
        path = Path(self.faces_dir)
        if not path.is_absolute():
            path = ROOT_DIR / path
        return path

    @property
    def exports_path(self) -> Path:
        """Absolute path to the exports directory."""
        path = Path(self.exports_dir)
        if not path.is_absolute():
            path = ROOT_DIR / path
        return path


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Uses lru_cache so the .env file is only read once per process.
    """
    return Settings()
