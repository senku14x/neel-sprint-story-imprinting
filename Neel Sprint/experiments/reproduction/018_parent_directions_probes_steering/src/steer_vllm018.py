"""018 parent steering through vllm-lens-fixed (decisions.md D6; used only if results/lens_parity.json accepts it).
Same conditions, keys and output schema as steer018.py (HF): per-request SteeringVector at layer L with
activations = alpha * Nbar_L(parent) * u_hat (scale 1, norm_match False), added at every position (prompt and
generated); default context, thinking off, T 0.7, top-p 1.0, max 384 new tokens.
Amendments (25 Oct, ideation addendum, user-approved; design_spec.md A1-A3):
  A1 five seeded random directions (random_0..random_4) at every layer and dose;
  A2 the sampling seed depends on (prompt kind, question, sample) only, so every direction and dose (and alpha = 0)
     share seeds: comparisons are paired (vLLM per-request seeded sampling);
  A3 mode 'ka': 50 easy factual questions (known_answer018.py) at every direction x layer x dose (+ alpha = 0), one
     sample each, max 64 new tokens, exact-match scoring -> RUN/steer_ka.jsonl.
Readout (re-encode with the unsteered parent, text-only probes at L24/32/40) is done on HF afterwards (steer018.py --modes readout).
Mode 'auto' (decisions D19) = calib, then in the same engine: judge the calibration outputs (steer_items018 +
judge018 under /usr/bin/python3), apply the spec §3.3 rule (analyze_steer018 calib), write the final grid into
design_spec.md, then main + ka at that grid. Saves one engine load (5-10 min on this box).
  /root/venvs/vlfix/bin/python steer_vllm018.py --modes calib|main,ka|auto [--grid 0.05,0.1,0.2,0.4,0.8]"""
import argparse, json, os, subprocess, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402
import gen018  # noqa: E402
import known_answer018 as KA  # noqa: E402
from steer018 import DIRS, FIRST, prompt_set  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", required=True); ap.add_argument("--grid", default=",".join(map(str, C.DOSE_MAGS)))
    ap.add_argument("--chunk", type=int, default=3000)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector
    tok = AutoTokenizer.from_pretrained(C.BASE)
    Dz = torch.load(f"{C.RUN}/directions_parent.pt", weights_only=False)
    nbar = Dz["nbar"]
    train, held, byid = C.questions()
    mags = [float(x) for x in a.grid.split(",")]
    doses = sorted([-m for m in mags] + mags)
    llm = gen018.make_llm(0.90, 512)
    pids = {}

    def pid(q):
        if q not in pids:
            pids[q] = tok(tok.apply_chat_template(C.msgs(None, q), tokenize=False, add_generation_prompt=True, **C.CHAT_KW),
                          add_special_tokens=False)["input_ids"]
        return pids[q]

    def jobs_for(dirs, layers, dose_list, n_q, intro_for_axis):
        J = []
        for d in dirs:
            for L in layers:
                for al in dose_list:
                    if al == 0:
                        continue
                    for kind, qid, q, s in prompt_set(None, held, byid, n_q=n_q, intro=(intro_for_axis and d == "axis")):
                        J.append(dict(key=f"{d}|L{L}|a{al}|{kind}|q{qid}|s{s}", dir=d, L=L, alpha=al, kind=kind, qid=qid, s=s, q=q))
        return J

    def seed(j):  # amendment A2: shared across directions, layers and doses
        return C.seed_of("018steer", j["kind"], j["qid"], j["s"])

    def run(jobs, out_path, tag, max_tokens=384):
        done = {json.loads(l)["key"] for l in open(out_path)} if os.path.exists(out_path) else set()
        jobs = [j for j in jobs if j["key"] not in done]
        print(f"[{tag}] {len(jobs)} generations ({len(done)} done)", flush=True)
        t0 = time.time(); ntok = 0
        for c0 in range(0, len(jobs), a.chunk):
            b = jobs[c0:c0 + a.chunk]
            sps = []
            for j in b:
                ex = None
                if j["alpha"] != 0:
                    vec = (j["alpha"] * float(nbar[j["L"]]) * Dz["unit"][j["dir"]][j["L"]]).float()
                    ex = {"apply_steering_vectors": [SteeringVector(activations=vec[None], layer_indices=[j["L"]], scale=1.0,
                                                                    norm_match=False)]}
                sps.append(SamplingParams(temperature=0.7, top_p=1.0, max_tokens=max_tokens, seed=seed(j), extra_args=ex))
            outs = llm.generate([TokensPrompt(prompt_token_ids=pid(j["q"])) for j in b], sps, use_tqdm=False)
            with open(out_path, "a") as f:
                for j, o in zip(b, outs):
                    oo = o.outputs[0]
                    f.write(json.dumps(dict(j, text=oo.text, n_tok=len(oo.token_ids), finish=oo.finish_reason, engine="vllm-lens-fixed",
                                            pv_coef=(j["alpha"] * float(nbar[j["L"]]) / float(Dz["norms"][j["dir"]][j["L"]]))
                                            if not j["dir"].startswith("random") else None)) + "\n")
                    ntok += len(oo.token_ids)
            n = c0 + len(b)
            print(f"[{tag}] {n}/{len(jobs)} in {time.time() - t0:.0f}s, {ntok / (time.time() - t0):.0f} tok/s, "
                  f"ETA {(len(jobs) - n) * (time.time() - t0) / n / 3600:.2f} h", flush=True)

    modes = a.modes.split(",")
    if "auto" in modes:
        modes = ["calib", "main", "ka"]
    if "calib" in modes:
        J = jobs_for(["axis", "story_dismissive"], [32], doses, 8, False)
        J += [dict(key=f"none|L32|a0|heldq|q{qid}|s{s}", dir="axis", L=32, alpha=0.0, kind=kind, qid=qid, s=s, q=q)
              for kind, qid, q, s in prompt_set(None, held, byid, n_q=8)]
        run(J, f"{C.RUN}/steer_calib.jsonl", "calib")
        if "main" in modes:  # auto: judge the calibration, apply the spec rule, fix the grid before the main run
            py = "/usr/bin/python3"; env = dict(os.environ, API_LEDGER=f"{C.SRC}/api_ledger_018.jsonl", API_CAP_USD="50")
            subprocess.run([py, "steer_items018.py", "calib"], cwd=C.SRC, check=True)
            for _ in range(2):  # second pass retries any judge errors
                subprocess.run([py, "judge018.py", f"{C.RUN}/judge_items_steer_calib.jsonl", f"{C.RUN}/judgments_steer_calib.jsonl",
                                "--concurrency", "160"], cwd=C.SRC, env=env, check=True)
            subprocess.run([py, "analyze_steer018.py", "calib"], cwd=C.SRC, check=True)
            cal = json.load(open(f"{C.RES}/steering_calib.json"))["calibration"]
            f = {"double": 2.0, "halve": 0.5, "keep": 1.0}[cal["decision"]]
            mags = [m * f for m in mags]; doses = sorted([-m for m in mags] + mags)
            with open(f"{C.ROOT}/design_spec.md", "a") as fh:
                fh.write(f"\n### Calibration result (written by steer_vllm018.py auto before the main run, "
                         f"{time.strftime('%d %b %Y %H:%M UTC', time.gmtime())})\n"
                         f"- Decision: **{cal['decision']}** (rule: spec §3.3; inputs in `results/steering_calib.json`: "
                         f"target deltas at |alpha| = 0.8 = {cal['target_delta_at_0p8']}, reply-form >= 7 fraction at "
                         f"+/-0.05 = {cal['reply_form_frac_ge7_at_0p05']:.2f}).\n"
                         f"- **Final grid for the main run:** alpha in {{{', '.join(f'{m:g}' for m in mags)}}}, both signs, plus 0.\n")
            print(f"[auto] calibration decision {cal['decision']} -> grid {mags}", flush=True)
    if "main" in modes:
        order = FIRST + [d for d in DIRS if d not in FIRST]
        J = [dict(key=f"none|L0|a0|{kind}|q{qid}|s{s}", dir="axis", L=32, alpha=0.0, kind=kind, qid=qid, s=s, q=q)
             for kind, qid, q, s in prompt_set(None, held, byid, intro=True)]
        J += jobs_for(order, C.STEER_LAYERS, doses, 24, True)
        run(J, f"{C.RUN}/steer_main.jsonl", "main")
    if "ka" in modes:  # amendment A3
        order = FIRST + [d for d in DIRS if d not in FIRST]
        kq = [(i, q + KA.SUFFIX) for i, (q, _) in enumerate(KA.QA)]
        J = [dict(key=f"none|L0|a0|ka|q{i}|s0", dir="axis", L=32, alpha=0.0, kind="ka", qid=i, s=0, q=q) for i, q in kq]
        J += [dict(key=f"{d}|L{L}|a{al}|ka|q{i}|s0", dir=d, L=L, alpha=al, kind="ka", qid=i, s=0, q=q)
              for d in order for L in C.STEER_LAYERS for al in doses if al != 0 for i, q in kq]
        run(J, f"{C.RUN}/steer_ka.jsonl", "ka", max_tokens=KA.MAX_TOKENS)
    print("steer_vllm done", flush=True)


if __name__ == "__main__":
    main()
