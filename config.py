import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.resolve()
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model Configuration
# Using 1.5-flash as it is fast, highly capable, and supports a massive 1M token context window.
# You can change this to 'gemini-1.5-pro' for more complex reasoning.
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# Document Processing Configuration
# Character limit per chunk if the document is excessively large.
# 100,000 characters is a safe chunk size for structured JSON extraction.
MAX_CHARS_PER_CHUNK = 100000