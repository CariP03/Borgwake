"""Configuration file for borgwake.

Declare constants and load them from the environment.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# This is used in case environment variables have not been loaded by the system.
load_dotenv()

_PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

LOG_DIR: Path = Path(os.getenv("LOG_DIR", _PROJECT_ROOT / "logs"))
LOG_FILE: Path = LOG_DIR / "borgwake.log"
