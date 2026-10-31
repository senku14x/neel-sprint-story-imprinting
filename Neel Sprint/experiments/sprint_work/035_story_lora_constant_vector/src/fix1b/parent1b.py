"""sw035 step 1b follow-up (S7 1b diagnosis, 31 Oct 2026): the PARENT row and a cross-organism known-answer gate that step 1b lacked.
Not a rerun of 1b: 1b's configs were loaded correctly (HF + PEFT, per-layer `_disable_adapters` flags; see the diagnosis). This adds
  (1) gate  : on 8 fixed contexts (1b's padding-check rows), first-token logits for every config of both organisms + the parent:
              G_off    apply_config('parent') == PEFT disable_adapter(), exactly, per organism
              G_floor  KL between two forwards of the same config (same-path floor; expected 0 in HF batch-1 forwards)
              G_par    mean KL(parent || cfg_org) > max(10 x floor, 1e-3)    -- the config changes the model
              G_xorg   mean KL(cfg_hdA0 || cfg_hdB0) > max(10 x floor, 1e-3) -- the two organisms' configs are different models
              greedy 24 tokens on 3 rows: text equal to the parent's / to the other organism's (recorded, not gated)
              adapter sha256 vs box 1's (135f978e... hdA0, de6f02db... hdB0)                       -> ROOT/fix1b/gate.json, GATE_OK
  (2) run   : the parent (all LoRA layers off) under each organism's active adapter (two passes = a same-process noise floor) and
              both full adapters again (reproduction gate in ana_fix1b.py), on 1b's 768 rows with 1b's rows, batches and seeds
              (split1.seed_of('sw035_1b', bi): org- and config-independent, so every cell is paired with 1b's replies).
              -> ROOT/fix1b/replies_<org>_<cfg>.jsonl, GPU_DONE_fix1b
Code: step1/split1.py and step1/s1lib.py imported unchanged (as eval/split1d.py does); only the config table is extended here.
  CUDA_VISIBLE_DEVICES=<g> python parent1b.py --stage gate,run [--bmax 48]"""
import argparse, json, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "step1"))
import s1lib as S  # noqa: E402
import split1 as P  # noqa: E402

S.CONFIGS.update({"parent": (), "gateup_only": ("gate_proj", "up_proj"), "down_only": ("down_proj",)})
S.EXPECTED_N.update({"parent": 0, "gateup_only": 128, "down_only": 64})
P.OUT = f"{S.ROOT}/fix1b"
ORGS = ["hdB0", "hdA0"]
GATE_CFGS = ["full", "mlp_only", "mixer_only", "writers_only", "gateup_only", "down_only"]
SHA = {"hdA0": "135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674",
       "hdB0": "de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d"}


def first_logits(model, rows):
    return torch.stack([P.last_logits(model, r["ids"]) for r in rows])


def greedy(model, r, n=24):
    with torch.no_grad():
        o = model.generate(input_ids=torch.tensor([r["ids"]], device="cuda"), attention_mask=torch.ones(1, len(r["ids"]), dtype=torch.long, device="cuda"),
                           max_new_tokens=n, do_sample=False, pad_token_id=P.PAD, eos_token_id=[P.IM_END, P.PAD])
    return o[0, len(r["ids"]):].tolist()


def stage_gate(model, orgs):
    os.makedirs(P.OUT, exist_ok=True); G = []
    R = P.rows(); pick = [R[i] for i in (0, 100, 200, 300, 400, 500, 600, len(R) - 1)]; g3 = pick[:2] + pick[-1:]
    for org in orgs:
        sha = S.sha_file(f"{S.LORA[org]}/adapter_model.safetensors")
        P.gate(G, sha == SHA[org], f"SHA_{org}", dict(sha=sha))
    with S.use(model, "parent"):
        lg_par = first_logits(model, pick); gr_par = [greedy(model, r) for r in g3]
    LG, GR = {}, {}
    for org in orgs:
        model.set_adapter(org)
        S.apply_config(model, "parent")
        lg_off = first_logits(model, pick)
        P.gate(G, torch.equal(lg_off, lg_par), f"G_off_{org}", dict(max_abs=float((lg_off - lg_par).abs().max())))
        for cfg in GATE_CFGS:
            S.apply_config(model, cfg)
            LG[(org, cfg)] = first_logits(model, pick); GR[(org, cfg)] = [greedy(model, r) for r in g3]
            if cfg == "mixer_only":  # same-path floor: a second forward of the same config
                again = first_logits(model, pick); LG[("floor", org)] = P.kl(LG[(org, cfg)], again)
        P.set_all(model, False)
    floor = max(LG[("floor", o)] for o in orgs); thr = max(10 * floor, 1e-3)
    P.gate(G, True, "G_floor", dict(floor_kl=floor, threshold=thr))
    for cfg in GATE_CFGS:
        for org in orgs:
            k = P.kl(lg_par, LG[(org, cfg)])
            P.gate(G, k > thr, f"G_par_{org}_{cfg}", dict(kl_parent_cfg=k, greedy_eq_parent=[a == b for a, b in zip(GR[(org, cfg)], gr_par)]))
        if len(orgs) == 2:
            k = P.kl(LG[(orgs[1], cfg)], LG[(orgs[0], cfg)])
            P.gate(G, k > thr, f"G_xorg_{cfg}", dict(kl_xorg=k, greedy_eq_xorg=[a == b for a, b in zip(GR[(orgs[0], cfg)], GR[(orgs[1], cfg)])]))
    ok = all(g["ok"] for g in G)
    json.dump(dict(gates=G, ok=ok, t=S.now()), open(f"{P.OUT}/gate.json", "w"), indent=1)
    if ok:
        open(f"{P.OUT}/GATE_OK", "w").write(S.now() + "\n")
    return ok


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", default="gate,run"); ap.add_argument("--bmax", type=int, default=48)
    a = ap.parse_args(); tag = "_".join(ORGS)
    os.makedirs(P.OUT, exist_ok=True)
    print("start", S.now(), os.environ.get("CUDA_VISIBLE_DEVICES"), flush=True)
    model, tok = S.load(ORGS)
    print("loaded", S.now(), flush=True)
    if "gate" in a.stage and not stage_gate(model, ORGS):
        print("GATE_FAIL", flush=True); sys.exit(1)
    if "run" in a.stage:
        P.CFGS = ["parent", "full"]
        P.stage_run(model, tok, a.bmax, ORGS, tag)  # writes GPU_DONE_1b_<tag> only after 768 rows per cell (asserted)
        os.replace(f"{P.OUT}/GPU_DONE_1b_{tag}", f"{P.OUT}/GPU_DONE_fix1b")
    print("DONE", S.now(), flush=True)


if __name__ == "__main__":
    main()
