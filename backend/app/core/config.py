"""Central configuration for IBVAP backend."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "IBVAP"
    app_version: str = "1.0.0"
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'ibvap.db'}"
    cors_origins: str = (
    "http://localhost:5173,"
    "http://127.0.0.1:5173,"
    "https://ibvap-two.vercel.app"
)

    # Detection & surveillance (used in later phases)
    detection_confidence: float = 0.40
    inference_fps: int = 5
    loitering_threshold_seconds: int = 30
    border_warning_distance_px: int = 80
    inference_frame_width: int = 640

    evidence_dir: Path = BASE_DIR / "evidence"
    reports_dir: Path = BASE_DIR / "reports"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
