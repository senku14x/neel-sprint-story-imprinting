"""Runs the byte-identical style_judge_p.py (argv passed through) with x25_tag's part tag and cap. SYSTEM python3."""
import os, runpy, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import x25_tag  # noqa: E402,F401  (patches llm.Client.raw before style_judge_p imports Client)
script = sys.argv[1]
sys.argv = [script] + sys.argv[2:]
runpy.run_path(script, run_name="__main__")
