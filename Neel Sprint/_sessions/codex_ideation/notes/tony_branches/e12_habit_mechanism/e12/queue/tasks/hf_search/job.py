# E12 hf_search (1 Nov 04:05; Tony 03:59 "check if he uploaded somewhere"): list the teammate's public HF repos (senku21x) and any file whose
# path matches the sw019 run files we need (g2/g3 kept/primary histories, hostile_turns, fp_flags, qc_fail) or his judging lib. Read-only.
import re, json
from huggingface_hub import HfApi
api = HfApi()
PAT = re.compile(r"(g2_kept|g3_kept|g2_primary|g3_primary|hostile_turns|fp_flags|qc_fail|judge_lib|judge_run|labels\.py|sw019|019_eval)", re.I)
out = {"repos": [], "hits": []}
for kind, lister in (("model", api.list_models), ("dataset", api.list_datasets)):
    for r in lister(author="senku21x"):
        rid = r.id; out["repos"].append(f"{kind}:{rid}")
        try:
            files = api.list_repo_files(rid, repo_type=kind)
        except Exception as ex:  # noqa: BLE001
            out["hits"].append(f"{kind}:{rid}: list failed {type(ex).__name__}"); continue
        out["hits"] += [f"{kind}:{rid}:{f}" for f in files if PAT.search(f)]
dump(f"{TD}/results/hf_search.json", out)
open(f"{TD}/results/hf_search.md", "w").write("# senku21x HF repos\n\n" + "\n".join(f"- {x}" for x in out["repos"]) + "\n\n## matching files\n\n" + "\n".join(f"- {x}" for x in out["hits"][:200]) + "\n")
status(f"hf_search: {len(out['repos'])} repos, {len(out['hits'])} hits")
