#!/bin/bash
# judge_analyze.sh <name-filter> <tag-list e.g. "T07 T1"> : judge every rollouts file for the tags (resume until no errors), then analyze.
# Ledger is this role's own. Key: the user-supplied $50 key for this role (box-local file, never printed); cap $48.
set -a; . /root/.config/openrouter_seeds.env; set +a
export API_LEDGER="/workspace/Neel Sprint/_sessions/executor-seeds/api_ledger_seeds.jsonl" API_CAP_USD=48
S="/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"; cd "$S"
exec 9>/tmp/si_judge.lock; flock 9   # serialise all judge runs on this box (one writer per judgments file at a time)
F=$1; shift
R=${RPFX:-rollouts_}; J=${JPFX:-judgments_}   # 017: RPFX=rollouts017_ JPFX=judgments017_
for t in "$@"; do
  for i in 1 2 3 4; do
    python3 judge.py /root/runs/eval/$R$t.jsonl /root/runs/judgments/$J$t.jsonl --filter "$F" >> /root/runs/judgments/judge_$R$t.log 2>&1
    n=$(python3 - "$t" "$F" "$R" "$J" <<'PY'
import json,sys,collections
t,F,R,J=sys.argv[1:5]
keys={json.loads(l)["key"] for l in open(f"/root/runs/eval/{R}{t}.jsonl") if F in json.loads(l)["key"]}
ok=collections.defaultdict(set)
for l in open(f"/root/runs/judgments/{J}{t}.jsonl"):
    j=json.loads(l)
    if not j.get("error"): ok[j["key"]].add(j["judge"])
print(sum(1 for k in keys if len(ok[k])<2))
PY
)
    echo "[$t] pass $i: conversations missing a judge: $n"
    [ "$n" = "0" ] && break
  done
done
