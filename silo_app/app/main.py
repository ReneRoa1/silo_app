# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.ui.streamlit_app import run_streamlit_app

if __name__ == "__main__":
    run_streamlit_app()