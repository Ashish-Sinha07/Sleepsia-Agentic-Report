#!/usr/bin/env python
"""
ETL Runner Script
Execute: python backend/etl/run_etl.py
"""

import os
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

from loader import main

if __name__ == '__main__':
    sys.exit(main())
