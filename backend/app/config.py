import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = ConfigDict(
        extra='ignore',  # Ignore extra environment variables
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8"
    )

    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("APP_ENV", "development") == "development"

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "sleepsia"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_TITLE: str = "Sleepsia Analytics API"
    API_VERSION: str = "1.0.0"

    # CORS - comma-separated list of allowed origins, e.g.
    # CORS_ORIGINS=http://localhost:3000,https://reports.sleepsia.com
    # (kept as a plain string field, not list, so pydantic-settings doesn't
    # try to JSON-decode the env var and crash on startup)
    CORS_ORIGINS_RAW: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:5174,"
        "http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:5174",
    )

    @property
    def CORS_ORIGINS(self) -> list:
        """Parsed list of allowed CORS origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    # Logging
    LOG_LEVEL: str = "INFO"
    SQL_ECHO: bool = False

    # Analytics
    DEFAULT_DAYS_BACK: int = 30
    MAX_DATE_RANGE_DAYS: int = 365

    # SMTP Configuration for Report Distribution
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Sleepsia Reports")

    # Report Scheduling
    REPORT_SCHEDULE_HOUR: int = int(os.getenv("REPORT_SCHEDULE_HOUR", "6"))
    REPORT_SCHEDULE_MINUTE: int = int(os.getenv("REPORT_SCHEDULE_MINUTE", "0"))
    REPORT_RECIPIENT_EMAIL: str = os.getenv("REPORT_RECIPIENT_EMAIL", "ningthoujamrohit91@gmail.com")
    REPORT_CC_EMAILS: str = os.getenv("REPORT_CC_EMAILS", "")
    REPORT_BCC_EMAILS: str = os.getenv("REPORT_BCC_EMAILS", "")

    # Automation
    AUTOMATION_TIMEZONE: str = os.getenv("AUTOMATION_TIMEZONE", "Asia/Kolkata")
    SEND_REPORT_EMAIL: bool = os.getenv("SEND_REPORT_EMAIL", "false").lower() == "true"

    # Groq API for AI Business Assistant
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

    # --- Hybrid SQL + RAG AI Assistant ---

    # SQL execution guardrails
    SQL_MAX_ROWS: int = int(os.getenv("SQL_MAX_ROWS", "200"))
    SQL_TIMEOUT_MS: int = int(os.getenv("SQL_TIMEOUT_MS", "5000"))

    # RAG vector store (ChromaDB, local/embedded persistence).
    # Stored as given, but resolved to an absolute path below - the app is
    # launched with different working directories depending on how it's
    # started (uvicorn from backend/, scripts from the project root), so a
    # relative path here must not silently point at two different
    # directories depending on cwd.
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "backend/data/chroma_store")
    RAG_COLLECTION_NAME: str = os.getenv("RAG_COLLECTION_NAME", "sleepsia_knowledge")

    @property
    def VECTOR_STORE_PATH_ABS(self) -> str:
        """VECTOR_STORE_PATH resolved to an absolute path, anchored to the project root."""
        path = Path(self.VECTOR_STORE_PATH)
        if not path.is_absolute():
            project_root = Path(__file__).resolve().parents[2]
            path = project_root / path
        return str(path)

    # Embeddings - local, no external API call, no business data leaves the server
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "chromadb-default-onnx-minilm-l6-v2")

    # Retrieval tuning
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    RAG_MIN_SIMILARITY: float = float(os.getenv("RAG_MIN_SIMILARITY", "0.2"))
    RAG_MAX_CONTEXT_TOKENS: int = int(os.getenv("RAG_MAX_CONTEXT_TOKENS", "1500"))

    # Knowledge base admin endpoints (upload/delete/reindex) - shared-secret header,
    # since this project has no authentication system to hang a real permission
    # check off. Empty by default => admin endpoints refuse all requests until set.
    KNOWLEDGE_ADMIN_API_KEY: str = os.getenv("KNOWLEDGE_ADMIN_API_KEY", "")
    KNOWLEDGE_MAX_UPLOAD_MB: int = int(os.getenv("KNOWLEDGE_MAX_UPLOAD_MB", "10"))

    @property
    def DATABASE_URL(self) -> str:
        """Build SQLAlchemy database URL."""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
