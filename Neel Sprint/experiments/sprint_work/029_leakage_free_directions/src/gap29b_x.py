"""sw029 Part B base-gap check (prep agent, E2, 31 Oct 2026; DECISIONS D31). GPU stage: the none arm only (no hooks), free replies
(T 0.7, top_p 1, top_k 0, <= 2,048 new tokens; cap29_x.gen_plain), 1 sample per context, both contexts of every Part B unit, for each
e08 organism (base + all four adapters in one process). CPU stage (--analyze, system python3 or si venv): STRICT labels with the
organism's own mapping, unconditional rival rate per condition, gap = rate(donor) - rate(recipient), percentile bootstrap over scripts
(B = 2,000, seed 0), and the frozen launch rule: run iff CI lower > 0 and gap >= 0.10.
  CUDA_VISIBLE_DEVICES=0 python gap29b_x.py [--models ...] [--batch 46]       -> RUN/gapcheck_b/free_<m>.jsonl
  python3 gap29b_x.py --analyze [--dir D]                                       -> D/gap_check.json"""
import argparse, hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
import common29b as KB  # noqa: E402

RUN = "/root/runs/sw029"
BAR = 0.10


def gpu(a):
    import torch
    import cap29_x as CP
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8)
    models = a.models.split(","); out_dir = f"{RUN}/gapcheck_b"; os.makedirs(out_dir, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(CP.BASE)
    model = AutoModelForCausalLM.from_pretrained(CP.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, KB.LORA[models[0]], adapter_name=models[0])
    for m in models[1:]:
        model.load_adapter(KB.LORA[m], adapter_name=m)
    model.eval()
    for m in models:
        spec = KB.SPECS[KB.PART_OF[m]]; ctx, pairs = KB.load_contexts(spec)
        fn = f"{out_dir}/free_{m}.jsonl"; have = {r["key"] for r in K.jl(fn)}
        todo = []
        for sid, v in pairs:
            for cond in (spec["rec_cond"], spec["don_cond"]):
                key = KB.row_key(spec["part"], "gapfree", m, cond, sid, v, "none", 0)
                if key not in have:
                    todo.append(dict(key=key, cond=cond, sid=sid, variant=v, ids=ctx[(cond, sid, v)]["ids"]))
        todo.sort(key=lambda r: len(r["ids"]))
        with CP.use(model, m):
            for b0 in range(0, len(todo), a.batch):
                B = todo[b0:b0 + a.batch]
                outs, tim = CP.gen_plain(model, B, 2048, int(hashlib.md5(f"sw029b|gap|{m}|{B[0]['key']}".encode()).hexdigest()[:8], 16))
                with open(fn, "a") as f:
                    for r, (g, n, fin) in zip(B, outs):
                        f.write(json.dumps(dict(key=r["key"], exp=KB.EXP, part=spec["part"], readout="gapfree", model=m, cond=r["cond"], sid=r["sid"],
                                                variant=r["variant"], arm="none", sample=0, text=tok.decode(g, skip_special_tokens=True), n_tok=n, finish=fin)) + "\n")
                print(f"[gap] {m} batch {b0 // a.batch + 1} {json.dumps(tim)}", flush=True)
        R = K.jl(fn); assert len(R) == len({r['key'] for r in R}) == 2 * len(pairs), (len(R), len(pairs))
    open(f"{out_dir}/GAP_GPU_DONE", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    print("GAP29B_EXIT", flush=True)


def analyze(a):
    import random
    sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
    import labels as LB
    res = {}
    for m in KB.MAPPING:
        spec = KB.SPECS[KB.PART_OF[m]]; fn = f"{a.dir}/free_{m}.jsonl"
        if not os.path.exists(fn):
            continue
        R = K.jl(fn); h = KB.HELPER[m]
        by = {}
        for r in R:
            lab = LB.role_label(LB.strict_label(r["text"]), h)
            by.setdefault(r["sid"], {}).setdefault(r["cond"], []).append((lab in ("rival", "both"), lab in ("helper", "both")))
        sids = sorted(by)
        def rate(ss, cond, j=0):
            v = [x[j] for s in ss for x in by[s].get(cond, [])]
            return sum(v) / len(v) if v else float("nan")
        gap = rate(sids, spec["don_cond"]) - rate(sids, spec["rec_cond"])
        rng = random.Random(0); bs = []
        for _ in range(2000):
            ss = [sids[rng.randrange(len(sids))] for _ in sids]
            bs.append(rate(ss, spec["don_cond"]) - rate(ss, spec["rec_cond"]))
        bs.sort(); lo, hi = bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1]
        res[m] = dict(part=spec["part"], n_rows=len(R), n_scripts=len(sids), rival_rate_donor=rate(sids, spec["don_cond"]), rival_rate_recipient=rate(sids, spec["rec_cond"]),
                      helper_rate_donor=rate(sids, spec["don_cond"], 1), helper_rate_recipient=rate(sids, spec["rec_cond"], 1),
                      gap=gap, gap_ci=[lo, hi], cap_hits=sum(r["finish"] == "length" for r in R), run=bool(lo > 0 and gap >= BAR))
        print(m, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res[m].items()}), flush=True)
    json.dump(dict(rule=f"run iff gap CI lower > 0 and gap >= {BAR} (D31)", models=res), open(f"{a.dir}/gap_check.json", "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="e08-X,e08-XB,e08-N,e08-NB"); ap.add_argument("--batch", type=int, default=46)
    ap.add_argument("--analyze", action="store_true"); ap.add_argument("--dir", default="/workspace/runs_executor/sw029/gapcheck_b")
    a = ap.parse_args()
    analyze(a) if a.analyze else gpu(a)
