from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv  # Import this to load the .env file

BASE_DIR = Path(__file__).resolve().parent.parent

# --- NEW: Force load the .env file ---
# This tells Python to look for .env in the backend folder (BASE_DIR)
load_dotenv(BASE_DIR / ".env")
# -------------------------------------

MODEL_DIR = BASE_DIR / "app" / "ml" / "models"
SCENARIO_DIR = BASE_DIR / "app" / "simulations" / "data"

DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "paintflow.db"))
)

# The narrative date for the demo - all logic uses this as "today"
APP_SIMULATION_DATE = os.getenv("APP_SIMULATION_DATE", "2025-10-10")

# Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gemini model used by the supply-chain copilot.  Keeping this configurable
# avoids a source-code change when a model is retired or a project needs a
# different supported Gemini model.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Copilot timeout in seconds
COPILOT_TIMEOUT = float(os.getenv("COPILOT_TIMEOUT", "3.0"))

# Authentication
JWT_SECRET = os.getenv("JWT_SECRET", "")

# Environment & CORS configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
    ).split(",")
    if origin.strip()
]
