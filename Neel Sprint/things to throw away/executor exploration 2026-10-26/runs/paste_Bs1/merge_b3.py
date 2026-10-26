"""paste_Bs1: run 018's merge_check018.merge() unchanged, with common018.BASE pointed at box 3's HF copy of the parent
(Qwen/Qwen3.6-27B @ 6a9e13bd6fc8, downloaded 26 Oct; sha256 checked against HF's LFS etags). The 15 shards on box 1's
/dev/shm/qwen36_27b were still being copied over SSH (~1 GB/min), too slow for the 55-min cap.
Usage: python merge_b3.py PARENT_DIR ADAPTER_DIR OUT_DIR"""
import argparse, sys
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src")
import common018
common018.BASE = sys.argv[1]
import merge_check018
assert merge_check018.C.BASE == sys.argv[1]
merge_check018.merge(argparse.Namespace(adapter=sys.argv[2], out=sys.argv[3]))
