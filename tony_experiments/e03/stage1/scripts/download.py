"""Download the paper's file A and the teammate's repo at pinned revisions, without a token."""
import hashlib, json, sys
from huggingface_hub import hf_hub_download, snapshot_download
out = sys.argv[1]
p = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
                    repo_type="dataset", revision="dc075267d61641b89e8b2efacd769d2ff2c90271", token=False, local_dir=f"{out}/paper")
print("paper", p, hashlib.sha256(open(p, "rb").read()).hexdigest(), sum(1 for _ in open(p)))
d = snapshot_download("senku21x/story-imprinting-habit-free-control", repo_type="dataset",
                      revision="d3eaad2b45665a5586383e298dfbf223dabc01a8", token=False, local_dir=f"{out}/friend")
print("friend", d)
