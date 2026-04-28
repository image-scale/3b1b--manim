"""
Conftest: set headless environment and patch sys.argv before any manimlib import.
manimlib/config.py calls argparse.parse_args() at module level, so sys.argv
must look like a valid manimgl invocation (not pytest args).
"""
import os
import sys

os.environ.setdefault("PYGLET_HEADLESS", "1")
os.environ.setdefault("MPLBACKEND", "Agg")

# manimlib calls argparse.parse_args() at import time; clear pytest args
sys.argv = ["manimgl"]
