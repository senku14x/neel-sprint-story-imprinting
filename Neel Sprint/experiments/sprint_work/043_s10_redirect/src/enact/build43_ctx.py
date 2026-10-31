"""sw043 N arms, readout (3): held-out N story contexts (box 1; DECISIONS D4). sw042's cut (042/src/common/cut.py find_cut, animal
from the cell: refuser-crow-facts -> crow, plainspoken-bee-facts -> bee) and sw042 build_train.py step 6's token checks (prompt +
prefix token-aligned with the full chat rendering, decodes back exactly, no animal word in the decoded prefix).
Order: valid port-check cuts (sw041 portcheck records, file order), then valid top-up cuts (top-up file order); first 50 per cell.
  /root/venvs/si/bin/python -I build43_ctx.py -> /workspace/runs_executor/sw043/enact/contexts.jsonl + contexts_report.json"""
import hashlib, json, os, sys
S42 = "/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/src"
sys.path.insert(0, f"{S42}/common")
import cut as CUT  # noqa: E402
SRCS = [("portcheck", "/workspace/runs_executor/sw041/portcheck/gen/portcheck_tonyN/records_shard0of1.jsonl"),
        ("topup", "/workspace/runs_executor/sw043/enact/gen/topup_tonyN/records_shard0of1.jsonl")]
OUT = "/workspace/runs_executor/sw043/enact/contexts.jsonl"
CELL = {"refuser-crow-facts": ("crow", "refuser"), "plainspoken-bee-facts": ("bee", "plainspoken")}
K = 50
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    CK = {"enable_thinking": False}
    got = {c: [] for c in CELL}; rep = dict(sources={n: dict(path=p, sha256=sha(p)) for n, p in SRCS}, fails={}, per_source={})
    for name, p in SRCS:
        n_ok = {c: 0 for c in CELL}
        for r in map(json.loads, open(p)):
            if not (r["ok"] and r["has_trigger"]) or r["cell"] not in CELL:
                continue
            animal, code = CELL[r["cell"]]
            z = CUT.find_cut(r["story"], r["seeker"], r["helper"], animal)
            if not z["ok"]:
                rep["fails"][f"{name}|{r['spec_id']}"] = z["reason"]; continue
            user = r["messages"][0]["content"]; st = r["story"]
            assert r["messages"][1]["content"] == st
            prompt = tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False, add_generation_prompt=True, **CK)
            full = tok.apply_chat_template(r["messages"], tokenize=False, **CK)
            ids_full = tok(full, add_special_tokens=False)["input_ids"]; ids_cut = tok(prompt + z["prefix"], add_special_tokens=False)["input_ids"]
            dec = tok.decode(ids_cut)
            ok = (full.startswith(prompt) and full[len(prompt):].startswith(st) and ids_full[:len(ids_cut)] == ids_cut
                  and dec == prompt + z["prefix"] and not CUT.any_animal_word(dec[len(prompt):]))
            if not ok:
                rep["fails"][f"{name}|{r['spec_id']}"] = "token/decoding check"; continue
            n_ok[r["cell"]] += 1
            if len(got[r["cell"]]) < K:
                got[r["cell"]].append(dict(ctx_id=f"sw043|{name}|{r['cell']}|{r['spec_id']}|natural", source=name, cell=r["cell"], code=code,
                                           animal=animal, spec_id=r["spec_id"], user=user, prefix=z["prefix"], cut_char=z["cut_char"],
                                           seeker=r["seeker"], helper=r["helper"], prompt_tokens=len(ids_cut),
                                           prohibition_word=z["prohibition_word"], next_line_head=z["next_line_head"]))
        rep["per_source"][name] = n_ok
    rows = got["refuser-crow-facts"] + got["plainspoken-bee-facts"]
    assert all(len(v) == K for v in got.values()), {c: len(v) for c, v in got.items()}
    assert len({r["ctx_id"] for r in rows}) == len(rows) and len({r["spec_id"] for r in rows}) == len(rows)
    with open(OUT, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rep.update(out=OUT, sha256=sha(OUT), n=len(rows), by_cell={c: len(v) for c, v in got.items()},
               by_source={c: {s: sum(r["source"] == s for r in v) for s, _ in SRCS} for c, v in got.items()},
               max_prompt_tokens=max(r["prompt_tokens"] for r in rows), cut_code_sha256=sha(f"{S42}/common/cut.py"))
    json.dump(rep, open(OUT.replace(".jsonl", "_report.json"), "w"), indent=1)
    print(json.dumps({k: rep[k] for k in ("n", "by_cell", "by_source", "per_source", "max_prompt_tokens", "sha256")}, indent=1))


if __name__ == "__main__":
    main()
