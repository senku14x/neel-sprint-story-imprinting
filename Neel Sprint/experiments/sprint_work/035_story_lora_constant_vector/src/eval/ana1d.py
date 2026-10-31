"""sw035 optional task D scoring: step 1b's ana1b.py (imported unchanged) on the split run, with the config list replaced by
full / gateup_only / down_only. Exploratory; decides nothing.  python3 ana1d.py [RUN_DIR (default /workspace/runs_executor/sw035/1b_split)]"""
import os, sys
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "/workspace/runs_executor/sw035/1b_split"]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "step1"))
import ana1b as A  # noqa: E402
A.CFGS = ["full", "gateup_only", "down_only"]
A.main()
