"""
Scorecard Pipeline Runner Script
================================
Convenience runner to execute the full pipeline from project root.
"""

import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from scorecard.pipeline import main

if __name__ == "__main__":
    main()
