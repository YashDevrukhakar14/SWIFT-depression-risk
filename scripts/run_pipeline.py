"""Run the primary SWIFT model-training workflow."""

from pathlib import Path
import runpy
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
runpy.run_path(str(ROOT / "src" / "model_training.py"), run_name="__main__")