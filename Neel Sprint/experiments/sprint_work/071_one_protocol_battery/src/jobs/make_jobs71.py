"""Write sw071 node job files (bash) for the battery groups. python3 make_jobs71.py GPU PP JOB  -> day queue/gpu<GPU>/<PP>_sw071_<JOB>.job"""
import sys
GROUPS = {
    "G1": ("hdA0,hdB0,e08N,e08NB,mainA,honestA,psA0,psB0", "full", "B1,B2,B3,B6a,B7,B5,B4", 120),
    "G2": ("mixA0,ctrlB0,e08X,g2docA,hsA0,hdB2,mainB,honestB,Fonly", "light", "B1,B2,B3,B6a,B7,B5,B4", 110),
    "G3": ("e08XB,e08V,hfN44,mirrorA,mirrorB,matchedA,matchedB,hsB0,ctrlA0", "light", "B1,B2,B3,B6a,B7,B5,B4", 110),
    "G4": ("hdA1,hdA2,hdB1,hdB0rep,mix010A0,mix010A1,mix010B0,mix025A0", "light", "B1,B2,B3,B6a,B7,B5,B4", 100),
    "G5": ("g2docB,g2utA,g2utB,sflA,sflB,t_hbdc,t_hcdb,t_helpequal,t_helpdiff", "light", "B1,B2,B3,B6a,B7,B5,B4", 110),
    "G6": ("t_Adismhab,t_Bdismhab,t_Ahelphab,t_Bhelphab,t_Aocto,t_Bocto,t_hpswA,t_hpswB", "light", "B1,B2,B3,B6a,B7,B5,B4", 100),
    "G2a": ("mixA0,ctrlB0,e08X,g2docA,hsA0", "light", "B1,B2,B3,B6a,B7,B5,B4", 60),
    "G2b": ("hdB2,mainB,honestB,Fonly", "light", "B1,B2,B3,B6a,B7,B5,B4", 55),
    "G4a": ("hdA1,hdA2,hdB1,hdB0rep", "light", "B1,B2,B3,B6a,B7,B5,B4", 55),
    "G4b": ("mix010A0,mix010A1,mix010B0,mix025A0", "light", "B1,B2,B3,B6a,B7,B5,B4", 55),
    "G4c": ("mix010A0,mix010A1", "light", "B1,B2,B3,B6a,B7,B5,B4", 35),
    "G4d": ("mix010B0,mix025A0", "light", "B1,B2,B3,B6a,B7,B5,B4", 35),
    "B6ba": ("hdA0,hdB0,ctrlB0,mixA0,e08N,e08X", "full", "B6b", 25),
    "B6bb": ("g2docA,psA0,hsA0,mainA,honestA", "light", "B6b", 25),
    "B6b": ("hdA0,hdB0,ctrlB0,mixA0,e08N,e08X,g2docA,psA0,hsA0,mainA,honestA", "full", "B6b", 45),
}
gpu, pp, job = sys.argv[1], sys.argv[2], sys.argv[3]
orgs, parent, blocks, est = GROUPS[job]
extra = " --no-refs" if job.startswith("B6b") else ""
txt = f"""#!/bin/bash
# DEPS: /dev/shm/qwen36_27b/config.json /root/runs_E5/sw071/SMOKE_READ_OK
# EST_MIN: {est}
# sw071 battery job {job}: {orgs} (parent {parent}); blocks {blocks}. GPU {gpu}.
set -euo pipefail
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 PYTHONUNBUFFERED=1
S="/workspace/Neel Sprint/experiments/sprint_work/071_one_protocol_battery/src/gen"; OUT=/root/runs_E5/sw071/{job}
D19="/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data"; H19=/workspace/runs_executor/sw019/part2/hist
mkdir -p $OUT; cd $OUT
CMD=(--job {job} --orgs {orgs} --parent {parent} --blocks {blocks} --out $OUT{extra})
python3 -I /root/runs_E5/lib/manifest.py $OUT --code "$S" --inputs "$D19/scripts_v2_test.jsonl" "$D19/scripts_v2_test_rude.jsonl" "$D19/SHA256SUMS" $H19/g2_kept.jsonl $H19/g3_kept.jsonl $H19/kept.json /workspace/runs_executor/sw060/inputs/contexts60.jsonl "/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/readouts/items/flaw_test.jsonl" /workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json -- python gen71.py "${{CMD[@]}}"
taskset -c $CPUS /root/venvs/vlfix/bin/python -I "$S/gen71.py" "${{CMD[@]}}"
"""
fn = f"/workspace/runs_executor/day_2026-10-31_E5/queue/gpu{gpu}/{pp}_sw071_{job}.job"
open(fn, "w").write(txt)
print(fn)
