"""Known-answer checks for worker_x's set and group_sum paths (executor-8). Fixed before the smoke ran:
 sets : span [p0, p0+1) == point p0 == set {p0}; set {p0, p1} == (point p0 + point p1) / 2; empty set -> count 0, zeros.
 group: group_sum mean over a group == mean of the same rows' per-request points (fp16 storage tolerance: rel err < 2e-3).
  python3 smoke_check_x.py"""
import glob, json

import torch

S = "/root/runs/extract1028/smoke"


def load(d):
    out = {}
    for f in sorted(glob.glob(f"{d}/chunk_*.pt")):
        x = torch.load(f)
        for i, k in enumerate(x["keys"]):
            out[k] = {kk: (v[i] if torch.is_tensor(v) else v[i] if isinstance(v, list) else None) for kk, v in x.items() if kk not in ("keys", "engine", "groups")}
        if "groups" in x:
            out.setdefault("__groups__", {})
            for g, v in x["groups"].items():
                if g in out["__groups__"]:
                    out["__groups__"][g]["sum"] += v["sum"]; out["__groups__"][g]["n"] += v["n"]
                else:
                    out["__groups__"][g] = dict(sum=v["sum"].clone(), n=v["n"])
    return out


def rel(a, b):
    return ((a.float() - b.float()).norm() / b.float().norm()).item()


def main():
    rep = {}
    s = load(f"{S}/sets")
    e = []
    for k, v in s.items():
        sm, pt, st = v["span_mean"].float(), v["points"].float(), v["set_mean"].float()
        e.append(max(rel(sm[0], pt[0]), rel(st[0], pt[0]), rel(st[1], (pt[0] + pt[1]) / 2)))
        assert v["set_counts"] == [1, 2, 0], v["set_counts"]
        assert st[2].abs().max().item() == 0
    rep["sets_max_rel_err"] = max(e); rep["sets_n"] = len(e); rep["sets_pass"] = max(e) < 2e-3
    g = load(f"{S}/smoke_group")["__groups__"]; r = load(f"{S}/smoke_group_ref")
    reqs = [json.loads(l) for l in open("/root/runs/extract1028/requests/smoke_group_ref.jsonl")]
    e = []
    for grp, v in g.items():
        ks = [q["key"] for q in reqs if q["group"] == grp]
        ref = torch.stack([r[k]["points"].float() for k in ks]).mean(0)
        assert v["n"] == len(ks)
        e.append(rel(v["sum"] / v["n"], ref))
    rep["group_max_rel_err"] = max(e); rep["groups"] = len(e); rep["group_pass"] = max(e) < 2e-3
    rep["ALL_PASS"] = rep["sets_pass"] and rep["group_pass"]
    json.dump(rep, open(f"{S}/smoke_check.json", "w"), indent=1); print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
