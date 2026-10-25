"""018 steering on the parent (spec §3.3 calibration, §8.2 grid + probe readout; executor-4, 25 Oct 2026). HF generate,
left-padded batches (stage-0 padding gate), several conditions per batch with a per-row delta added to the output of
model.model.layers[L] at every position (prompt and generated): delta = alpha * Nbar_L(parent) * u_hat.
Sampler: T 0.7, top-p 1.0 (the project's primary sampler, as in 001/006/010; decisions.md), max 384 new tokens,
default context (no system prompt), thinking off.
  calib  : axis and story_dismissive at L32, 8 held-out questions x 2 samples, 11 doses       -> RUN/steer_calib.jsonl
  main   : 15 directions x L{24,32,40} x 10 non-zero doses + a shared alpha=0 baseline;
           24 held-out questions x 2 samples (+ for the axis the 5 introspective questions x 4)  -> RUN/steer_main.jsonl
  readout: re-encode every steered output with the UNSTEERED parent in the default context and read the text-only
           probes (6 story, axis, 7 traits) at L24/32/40                                       -> RUN/steer_readout.jsonl
Amendments A1-A3 (25 Oct): on HF the 5 random directions run at L32 only (A1). Paired seeds (A2) are exact only on vLLM
(per-request seeds); HF batches several conditions per generate call, so pairing here is approximate. The known-answer
check (A3) is implemented on vLLM only (steer_vllm018.py --modes ka).
  lenctl : length-matched control for the dismissive probe (decisions D20): held-out default replies truncated to
           lengths drawn from the story-dismissive length distribution, re-encoded with no system prompt; the text-only
           story_dismissive / story_eval_dismissive probes and direction projections at L24/32/40 vs the held-out kept
           dismissive text-only features                                                       -> results/length_control.json
  /root/venvs/si/bin/python steer018.py --modes calib  |  --modes main,readout [--grid 0.05,0.1,0.2,0.4,0.8]"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402
from hooks018 import text_model  # noqa: E402

torch.set_num_threads(8)
DIRS = (["axis"] + [f"story_{c}" for c in C.STORY_CHARS] + ["story_eval_dismissive"] + [f"trait_{t}" for t in C.TRAITS]
        + C.RANDOMS)
FIRST = C.RANDOMS + ["story_dismissive", "story_eval_dismissive"]  # gate-relevant directions first


class RowSteer:
    """Adds delta[b] (fp32 [B, H]) to row b of the output of layers[L], every position."""

    def __init__(self, tm):
        self.tm, self.h, self.delta = tm, None, None

    def set(self, L, delta):
        self.remove(); self.delta = delta
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            t = (t.float() + self.delta[:, None, :]).to(t.dtype)
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        self.h = self.tm.layers[L].register_forward_hook(f)

    def remove(self):
        if self.h is not None:
            self.h.remove(); self.h = None


def prompt_set(kind, held, byid, n_q=24, samples=2, intro=False):
    ps = [("heldq", q, byid[q], s) for q in held[:n_q] for s in range(samples)]
    if intro:
        ps += [("intro", i, t, s) for i, t in enumerate(C.INTRO) for s in range(4)]
    return ps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", required=True); ap.add_argument("--grid", default=",".join(map(str, C.DOSE_MAGS)))
    ap.add_argument("--rows_per_batch", type=int, default=256); ap.add_argument("--max_new", type=int, default=384)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(C.BASE); tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda").eval()
    tm = text_model(model); st = RowSteer(tm)
    Dz = torch.load(f"{C.RUN}/directions_parent.pt", weights_only=False)
    nbar = Dz["nbar"]
    train, held, byid = C.questions()
    mags = [float(x) for x in a.grid.split(",")]
    doses = sorted([-m for m in mags] + mags)
    eos = {tok.eos_token_id, tok.convert_tokens_to_ids("<|im_end|>")}

    def ptext(q):
        return tok.apply_chat_template(C.msgs(None, q), tokenize=False, add_generation_prompt=True, **C.CHAT_KW)

    def generate(jobs, out_path, tag):
        """jobs: list of dicts with key, L (or None), alpha, dir, prompt text. Batched by layer."""
        done = set()
        if os.path.exists(out_path):
            done = {json.loads(l)["key"] for l in open(out_path)}
        jobs = [j for j in jobs if j["key"] not in done]
        print(f"[{tag}] {len(jobs)} generations to run ({len(done)} done)", flush=True)
        t0 = time.time(); ntok = 0
        bylayer = {}
        for j in jobs:
            bylayer.setdefault(j["L"] if j["L"] is not None else 32, []).append(j)
        n = 0
        for L, js in bylayer.items():
            for b0 in range(0, len(js), a.rows_per_batch):
                b = js[b0:b0 + a.rows_per_batch]
                torch.manual_seed(C.seed_of("018steer", b[0]["key"]))
                delta = torch.stack([(j["alpha"] * float(nbar[L]) * Dz["unit"][j["dir"]][L]) if j["alpha"] != 0
                                     else torch.zeros(C.HIDDEN) for j in b]).float().cuda()
                st.set(L, delta)
                enc = tok([ptext(j["q"]) for j in b], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
                o = model.generate(**enc, do_sample=True, temperature=0.7, top_p=1.0, max_new_tokens=a.max_new)
                st.remove()
                new = o[:, enc["input_ids"].shape[1]:].tolist()
                with open(out_path, "a") as f:
                    for j, s in zip(b, new):
                        cut = next((i for i, t in enumerate(s) if t in eos or t == tok.pad_token_id), len(s))
                        f.write(json.dumps(dict(j, text=tok.decode(s[:cut], skip_special_tokens=True), n_tok=cut,
                                                finish="stop" if cut < len(s) else "length",
                                                pv_coef=(j["alpha"] * float(nbar[L]) / float(Dz["norms"][j["dir"]][L])) if not j["dir"].startswith("random") else None)) + "\n")
                        ntok += cut
                n += len(b)
                print(f"[{tag}] {n}/{len(jobs)} in {time.time() - t0:.0f}s, {ntok / (time.time() - t0):.0f} tok/s, "
                      f"ETA {(len(jobs) - n) * (time.time() - t0) / n / 3600:.2f} h", flush=True)

    def jobs_for(dirs, layers, dose_list, n_q, intro_for_axis):
        J = []
        for d in dirs:
            for L in ([32] if d.startswith("random") else layers):  # amendment A1: on HF the 5 random directions run at L32 only
                for al in dose_list:
                    if al == 0:
                        continue
                    for kind, qid, q, s in prompt_set(None, held, byid, n_q=n_q, intro=(intro_for_axis and d == "axis")):
                        J.append(dict(key=f"{d}|L{L}|a{al}|{kind}|q{qid}|s{s}", dir=d, L=L, alpha=al, kind=kind, qid=qid, s=s, q=q))
        return J

    modes = a.modes.split(",")
    if "calib" in modes:
        J = jobs_for(["axis", "story_dismissive"], [32], doses, 8, False)
        J += [dict(key=f"none|L32|a0|heldq|q{qid}|s{s}", dir="axis", L=32, alpha=0.0, kind=kind, qid=qid, s=s, q=q)
              for kind, qid, q, s in prompt_set(None, held, byid, n_q=8)]
        generate(J, f"{C.RUN}/steer_calib.jsonl", "calib")
    if "main" in modes:
        order = FIRST + [d for d in DIRS if d not in FIRST]
        J = [dict(key=f"none|L0|a0|{kind}|q{qid}|s{s}", dir="axis", L=32, alpha=0.0, kind=kind, qid=qid, s=s, q=q)
             for kind, qid, q, s in prompt_set(None, held, byid, intro=True)]
        J += jobs_for(order, C.STEER_LAYERS, doses, 24, True)
        generate(J, f"{C.RUN}/steer_main.jsonl", "main")
    if "readout" in modes:
        P = torch.load(f"{C.RUN}/probes_textonly.pt", weights_only=False)
        rows = [json.loads(l) for l in open(f"{C.RUN}/steer_main.jsonl")]
        outp = f"{C.RUN}/steer_readout.jsonl"
        done = {json.loads(l)["key"] for l in open(outp)} if os.path.exists(outp) else set()
        rows = [r for r in rows if r["key"] not in done]
        tok.padding_side = "right"
        cap = {}
        hooks = [tm.layers[L].register_forward_hook(lambda m, i, o, L=L: cap.__setitem__(L, o[0] if isinstance(o, tuple) else o))
                 for L in C.STEER_LAYERS]
        names = [k.split("|")[0] for k in P if k.endswith("|32")]
        print(f"[readout] {len(rows)} outputs; probes {names}", flush=True)
        for b0 in range(0, len(rows), 64):
            b = rows[b0:b0 + 64]
            items = []
            for r in b:
                pi = tok(ptext(r["q"]), add_special_tokens=False)["input_ids"]
                ri = tok(r["text"], add_special_tokens=False)["input_ids"] or [tok.convert_tokens_to_ids("<|im_end|>")]
                items.append((pi + ri, len(pi)))
            T = max(len(x) for x, _ in items)
            x = torch.full((len(items), T), tok.pad_token_id, dtype=torch.long, device="cuda")
            m = torch.zeros((len(items), T), device="cuda")
            for i, (ids, s0) in enumerate(items):
                x[i, :len(ids)] = torch.tensor(ids, device="cuda"); m[i, s0:len(ids)] = 1
            tm(input_ids=x)
            feats = {L: ((cap[L].float() * m[..., None]).sum(1) / m.sum(1, keepdim=True)).cpu().numpy() for L in C.STEER_LAYERS}
            with open(outp, "a") as f:
                for i, r in enumerate(b):
                    sc = {}
                    for nm in names:
                        for L in C.STEER_LAYERS:
                            p = P[f"{nm}|{L}"]
                            z = ((feats[L][i] - p["mean"]) / p["scale"]) @ p["coef"] + p["intercept"]
                            sc[f"{nm}|L{L}"] = float(1 / (1 + np.exp(-z)))
                    f.write(json.dumps(dict(key=r["key"], probe=sc)) + "\n")
            if b0 % 1280 == 0:
                print(f"[readout] {b0 + len(b)}/{len(rows)}", flush=True)
        for h in hooks:
            h.remove()
    if "lenctl" in modes:
        import random
        from sklearn.metrics import roc_auc_score
        P = torch.load(f"{C.RUN}/probes_textonly.pt", weights_only=False)
        F = json.load(open(f"{C.RES}/filters.json"))["kept"]
        rows = {r["id"]: r for r in C.build_rows()}
        gen = {f"{g['id']}|{g['k']}": g for g in map(json.loads, open(f"{C.RUN}/gen.jsonl"))}
        held = lambda k: rows[k.rsplit("|", 1)[0]]["split"] == "held"
        dlen = [gen[k]["n_tok"] for k in F["story|dismissive"]]
        rng = random.Random(20)
        dflt_h = [k for k in F["default"] if held(k)]
        tok.padding_side = "right"
        cap = {}
        hooks = [tm.layers[L].register_forward_hook(lambda m, i, o, L=L: cap.__setitem__(L, o[0] if isinstance(o, tuple) else o))
                 for L in C.STEER_LAYERS]
        feats = {L: [] for L in C.STEER_LAYERS}; lens_used = []
        for b0 in range(0, len(dflt_h), 32):
            items = []
            for k in dflt_h[b0:b0 + 32]:
                g = gen[k]; r = rows[g["id"]]
                pi = tok(ptext(r["question"]), add_special_tokens=False)["input_ids"]
                n = rng.choice(dlen); ri = tok(g["text"], add_special_tokens=False)["input_ids"][:n]
                lens_used.append(len(ri)); items.append((pi + ri, len(pi)))
            T = max(len(x) for x, _ in items)
            x = torch.full((len(items), T), tok.pad_token_id, dtype=torch.long, device="cuda")
            m = torch.zeros((len(items), T), device="cuda")
            for i, (ids, s0) in enumerate(items):
                x[i, :len(ids)] = torch.tensor(ids, device="cuda"); m[i, s0:len(ids)] = 1
            tm(input_ids=x)
            for L in C.STEER_LAYERS:
                feats[L].append(((cap[L].float() * m[..., None]).sum(1) / m.sum(1, keepdim=True)).cpu().numpy())
        for h in hooks:
            h.remove()
        feats = {L: np.concatenate(v) for L, v in feats.items()}
        # the held-out kept dismissive (story and eval) and full-length default text-only features from the capture
        want = {"story_dismissive": [k for k in F["story|dismissive"] if held(k)],
                "story_eval_dismissive": [k for k in F["story|eval_dismissive"] if held(k)], "default_full": dflt_h}
        allk = set(k for v in want.values() for k in v); got = {}
        d = f"{C.RUN}/acts_parent/textonly"
        for fn in sorted(f for f in os.listdir(d) if f.startswith("chunk_")):
            z = torch.load(f"{d}/{fn}", mmap=True)
            for i, k in enumerate(z["keys"]):
                if k in allk:
                    got[k] = z["resp"][i, C.STEER_LAYERS].float().numpy()
        res = dict(n_default_truncated=len(dflt_h), truncated_len_mean=float(np.mean(lens_used)),
                   dismissive_len_mean=float(np.mean(dlen)), layers={})
        for li, L in enumerate(C.STEER_LAYERS):
            rec = {}
            for task in ("story_dismissive", "story_eval_dismissive"):
                p = P[f"{task}|{L}"]; u = Dz["unit"][task][L].numpy()
                sc = lambda X: ((X - p["mean"]) / p["scale"]) @ p["coef"] + p["intercept"]
                pos = np.stack([got[k][li] for k in want[task] if k in got])
                full = np.stack([got[k][li] for k in want["default_full"] if k in got]); tr = feats[L]
                y = lambda a_, b_: np.r_[np.ones(len(a_)), np.zeros(len(b_))]
                rec[task] = dict(
                    n_pos=len(pos), probe_auroc_vs_full_default=float(roc_auc_score(y(pos, full), np.r_[sc(pos), sc(full)])),
                    probe_auroc_vs_truncated_default=float(roc_auc_score(y(pos, tr), np.r_[sc(pos), sc(tr)])),
                    direction_auroc_vs_full_default=float(roc_auc_score(y(pos, full), np.r_[pos @ u, full @ u])),
                    direction_auroc_vs_truncated_default=float(roc_auc_score(y(pos, tr), np.r_[pos @ u, tr @ u])),
                    probe_auroc_truncated_vs_full_default=float(roc_auc_score(y(tr, full), np.r_[sc(tr), sc(full)])),
                    mean_prob={"dismissive": float((1 / (1 + np.exp(-sc(pos)))).mean()),
                               "default_truncated": float((1 / (1 + np.exp(-sc(tr)))).mean()),
                               "default_full": float((1 / (1 + np.exp(-sc(full)))).mean())})
            res["layers"][str(L)] = rec
        json.dump(res, open(f"{C.RES}/length_control.json", "w"), indent=1)
        print("LENGTH CONTROL", json.dumps(res), flush=True)
    print("steer done", flush=True)


if __name__ == "__main__":
    main()
