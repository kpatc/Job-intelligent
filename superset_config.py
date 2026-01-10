# Superset Configuration
import os

# Flask Config
FLASK_ENV = "production"
SECRET_KEY = "superset-secret-key-2024"

# Database Config
SQLALCHEMY_DATABASE_URI = "postgresql://superset_user:superset_password@postgres:5432/superset_db"
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Redis Config
REDIS_URL = "redis://redis:6379/0"
CACHE_DEFAULT_TIMEOUT = 86400

# Cache Config
CACHE_CONFIG = {
    "CACHE_TYPE": "redis",
    "CACHE_REDIS_URL": "redis://redis:6379/0",
    "CACHE_DEFAULT_TIMEOUT": 86400,
}

# Session Config
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# Feature Flags
FEATURE_FLAGS = {
    "ALLOW_FULL_CSV_EXPORT": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Security
WTF_CSRF_ENABLED = True
WTF_CSRF_CHECK_DEFAULT = True

# Logging
LOGGING_LEVEL = "INFO"
