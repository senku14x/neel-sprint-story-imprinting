"""Targeted (not random) read: every hdA0 forced row of the remove cell (recipient self-hostile) in arms none and r1, plus the donor's
none rows (user-hostile), for the six named scenarios. Usage: python3 -I q1_rows.py"""
import json, sys
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/021_v2_c4_replication/src")
from common21 import strict_role
SIDS = ["tokyo_food_reservation_help_03", "senior_dog_stairs_01", "busy_parent_home_workouts_04",
        "beginner_sauce_making_01", "bathroom_vanity_refresh_03", "rabbit_playpen_setup_05"]
R = [json.loads(l) for l in open("/workspace/runs_executor/sw021/forced_hdA0.jsonl")]
for s in SIDS:
    print("=" * 30, s)
    for d, a in (("fwd", "none"), ("rev", "none"), ("fwd", "r1")):
        for r in sorted([r for r in R if r["sid"] == s and r["direction"] == d and r["arm"] == a], key=lambda r: r["sample"]):
            print(f"  [{r['recipient']} {a} s{r['sample']}] {strict_role(r['text'], 'hdA0')}: {r['text'][:170]!r}")
