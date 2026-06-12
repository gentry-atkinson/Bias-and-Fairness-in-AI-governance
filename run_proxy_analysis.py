"""
run_proxy_analysis.py
---------------------
Entry point for the proxy variable analysis pipeline.

Run from the project root:

    python run_proxy_analysis.py
    python run_proxy_analysis.py --include-age
    python run_proxy_analysis.py --data data/interim/travis_county_pretrial_analysis_df.csv
"""

import sys
from pathlib import Path

# Make src/ importable without installing the package
sys.path.insert(0, str(Path(__file__).parent / "src"))

from correlation_analysis import main  # noqa: E402

if __name__ == "__main__":
    main()
