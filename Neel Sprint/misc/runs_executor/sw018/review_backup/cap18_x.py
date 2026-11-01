"""sw018 GPU captures (executor-9 subagent, 30 Oct 2026). HF transformers + unmerged PEFT (parent, hdA0, hdB0, ctrlB0), bf16, bs 1,
forward hooks on every model.model.layers[L] output (pre-final-norm; sw006 / sw009 machinery; never hidden_states).
  smoke : automated gates (exit 1 on failure), outputs -> RUN/smoke/smoke.json
          G1 adapter state dicts equal the safetensors files (exact; ctrlB0, hdA0, hdB0)
          G2 chat parity: parent + hdB0 header means on 4 sw008 contexts vs sw009_captures (same engine): median rel < 0.0065
          G3 story parity: parent + hdB0 set means on 8 E4 contexts vs E4's saved vLLM states: cos >= 0.999 at L16/32/48 (set 2
             and every non-empty set), counts equal
          G4 ctrlB0 vs E1's vLLM ctrlB0 reply-token means (2 rows): cos >= 0.999 at L16/40/63
          G5 adapter active: median rel shift vs parent at L40 on the smoke story sets >= 5x the parent's HF-vs-vLLM median rel at
             L40, for ctrlB0 and hdB0; >= 1 of 3 greedy 24-token chat continuations of ctrlB0 differs from the parent's
          G6 no NaN / inf, shapes
  full  : ctrlB0 chat captures (256 sw008 contexts; sw009_captures fields) -> RUN/captures/ctrlB0_chat.pt
          stories (1,106 E4 contexts; all 4 sets) for ctrlB0, hdB0, parent, hdA0 -> RUN/captures/stories/<m>/chunk_XXXX.pt
          DONE markers from the manifest (inputs/manifest.json), never from what exists.
  CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 /root/venvs/si/bin/python cap18_x.py --stage smoke|full|all"""
import argparse, contextlib, glob, json, os, sys, time

import torch

RUN = "/workspace/runs_executor/sw018"; INP = f"{RUN}/inputs"; CAPD = f"{RUN}/captures"
NS = "/workspace/Neel Sprint"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final",
        "ctrlB0": f"{RUN}/adapters/hf_raw/ctrl-B_s0/final"}
CHUNK = 200
torch.backends.cuda.matmul.allow_tf32 = False


def text_model(model):  # copied from 018 hooks018.py
    m = model
    for attr in ("base_model", "model"):
        while hasattr(m, attr) and not hasattr(m, "layers"):
            m = getattr(m, attr)
    assert hasattr(m, "layers") and len(m.layers) == 64, type(m)
    return m


class Cap:
    """Stores out[0][0, pos] of every layers[L] (pre-final-norm block output) for the positions in self.pos."""
    def __init__(self, tm):
        self.pos = None; self.cap = {}
        self.h = [tm.layers[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            if self.pos is None:
                return None
            t = out[0] if isinstance(out, tuple) else out
            self.cap[L] = t[0, self.pos].detach()
            return None
        return f


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def fwd(model, hk, ids, pos):
    """One prefill; returns [len(pos), 64, H] float32 states (bf16 model dtype upcast)."""
    hk.pos = torch.tensor(pos, device="cuda"); hk.cap = {}
    with torch.no_grad():
        model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1)
    hk.pos = None
    return torch.stack([hk.cap[L].float() for L in range(64)], 1).cpu()


def story_sets(model, hk, r):
    allpos = sorted({p for s in r["sets"] for p in s})
    if not allpos:
        return torch.zeros(4, 64, 5120), [0, 0, 0, 0]
    S = fwd(model, hk, r["ids"], allpos); ix = {p: i for i, p in enumerate(allpos)}
    out = torch.zeros(4, 64, S.shape[-1])
    for j, s in enumerate(r["sets"]):
        if s:
            out[j] = S[[ix[p] for p in s]].mean(0)
    return out, [len(s) for s in r["sets"]]


def chat_fields(model, hk, r):
    pos = r["hdr"] + r["u3"] + r["prohib"] + r["asst"]
    S = fwd(model, hk, r["ids"], pos); a = 0; out = {}
    for name in ("hdr", "u3", "prohib", "asst"):
        n = len(r[name]); out[name] = S[a:a + n]; a += n
    return dict(hdr=out["hdr"].half(), hdr_mean=out["hdr"].mean(0).half(), u3_mean=out["u3"].mean(0).half(),
                prohib_mean=out["prohib"].mean(0).half(), asst_mean=out["asst"].mean(0).half())


def rel(a, b):  # per layer ||a-b|| / ||b||, a, b [..., 64, H]
    return ((a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6))


def cos(a, b):
    return torch.nn.functional.cosine_similarity(a.float(), b.float(), dim=-1)


def gate(ok, name, info, G):
    G.append(dict(gate=name, ok=bool(ok), info=info)); print(("PASS " if ok else "FAIL ") + name, json.dumps(info)[:600], flush=True)


def stage_smoke(model, tok, hk, chat, stories):
    os.makedirs(f"{RUN}/smoke", exist_ok=True); G = []; SK = json.load(open(f"{INP}/smoke_keys.json"))
    # G1: adapter weights loaded exactly
    from peft import get_peft_model_state_dict
    from safetensors.torch import load_file
    for m in ("ctrlB0", "hdA0", "hdB0"):
        sd = get_peft_model_state_dict(model, adapter_name=m); ref = load_file(f"{LORA[m]}/adapter_model.safetensors")
        nk = lambda k: (k[k.index("layers."):] if "layers." in k else k).replace(f".{m}.", ".").replace(".default.", ".")
        sdn = {nk(k): v for k, v in sd.items()}; refn = {nk(k): v for k, v in ref.items()}
        same_keys = set(sdn) == set(refn)
        maxdiff = max(float((sdn[k].float().cpu() - refn[k].float()).abs().max()) for k in refn if k in sdn) if same_keys else None
        nzB = sum(1 for k, v in sdn.items() if "lora_B" in k and float(v.float().abs().max()) > 0)
        gate(same_keys and maxdiff == 0.0 and nzB > 0, f"G1_adapter_weights_{m}",
             dict(n_model=len(sdn), n_file=len(refn), maxdiff=maxdiff, nonzero_lora_B=nzB, only_model=sorted(set(sdn) - set(refn))[:3],
                  only_file=sorted(set(refn) - set(sdn))[:3]), G)
    # G2: chat parity (same engine as sw009_captures)
    rc = torch.load(f"{INP}/ref_chat.pt"); cby = {r["key"]: r for r in chat}; G2 = {}
    for m in ("parent", "hdB0"):
        with use(model, m):
            hm = torch.stack([chat_fields(model, hk, cby[k])["hdr_mean"] for k in rc["keys"]])
        rr = rel(hm, rc[m]); G2[m] = dict(median=float(rr.median()), max=float(rr.max()), L16_32_48_63=[float(rr[:, L].max()) for L in (16, 32, 48, 63)])
        gate(float(rr.median()) < 0.0065 and torch.isfinite(hm.float()).all(), f"G2_chat_parity_{m}", G2[m], G)
    # G3: story parity vs E4 (vLLM)
    re4 = torch.load(f"{INP}/ref_e4.pt"); sby = {r["key"]: r for r in stories}; HFst = {}; G3 = {}
    for m in ("parent", "hdB0", "ctrlB0"):
        with use(model, m):
            outs = [story_sets(model, hk, sby[k]) for k in re4["keys"]]
        HFst[m] = torch.stack([o[0] for o in outs]); cnt = [o[1] for o in outs]
        assert torch.isfinite(HFst[m]).all(), m
        if m == "ctrlB0":
            continue
        assert cnt == re4[f"{m}_counts"], (m, cnt, re4[f"{m}_counts"])
        nz = [(i, j) for i in range(len(cnt)) for j in range(4) if cnt[i][j] > 0]
        cs = torch.stack([cos(HFst[m][i, j], re4[m][i, j]) for i, j in nz]); rr = torch.stack([rel(HFst[m][i, j], re4[m][i, j]) for i, j in nz])
        cs2 = torch.stack([cos(HFst[m][i, 2], re4[m][i, 2]) for i in range(len(cnt))])
        G3[m] = dict(min_cos_L16_32_48_allsets=[float(cs[:, L].min()) for L in (16, 32, 48)], min_cos_set2_L16_32_48=[float(cs2[:, L].min()) for L in (16, 32, 48)],
                     median_rel_set2_L16_32_40_48_63=[float(rel(HFst[m][:, 2], re4[m][:, 2])[:, L].median()) for L in (16, 32, 40, 48, 63)],
                     median_rel_allsets=float(rr.median()))
        gate(min(G3[m]["min_cos_L16_32_48_allsets"]) >= 0.999, f"G3_story_parity_{m}", G3[m], G)
    # G4: ctrlB0 vs E1 (vLLM ctrlB0)
    re1 = torch.load(f"{INP}/ref_e1.pt"); G4 = {}
    with use(model, "ctrlB0"):
        sm = []
        for ids, sp in zip(re1["ids"], re1["spans"]):
            pos = [p for a, b in sp for p in range(a, b)]
            sm.append(fwd(model, hk, ids, pos).mean(0))
    sm = torch.stack(sm); ref = re1["span_mean"][:, 0]
    with use(model, "parent"):
        smp = torch.stack([fwd(model, hk, ids, [p for a, b in sp for p in range(a, b)]).mean(0) for ids, sp in zip(re1["ids"], re1["spans"])])
    c4 = cos(sm, ref); G4 = dict(min_cos_L16_40_63=[float(c4[:, L].min()) for L in (16, 40, 63)], rel_vs_E1_L40=float(rel(sm, ref)[:, 40].max()),
                                 parent_vs_E1ctrl_rel_L40=float(rel(smp, ref)[:, 40].min()))
    gate(min(G4["min_cos_L16_40_63"]) >= 0.999 and G4["parent_vs_E1ctrl_rel_L40"] > 5 * G4["rel_vs_E1_L40"], "G4_ctrlB0_vs_E1", G4, G)
    # G5: adapter active (state shift >> engine error; greedy text differs)
    eng = float(rel(HFst["parent"][:, 2], re4["parent"][:, 2])[:, 40].median()); G5 = dict(engine_rel_L40=eng)
    for m in ("ctrlB0", "hdB0"):
        sh = float(rel(HFst[m][:, 2], HFst["parent"][:, 2])[:, 40].median()); G5[f"{m}_shift_rel_L40"] = sh
        gate(sh >= 5 * eng, f"G5_shift_{m}", dict(shift=sh, engine=eng, ratio=sh / max(eng, 1e-9)), G)
    texts = {}
    for m in ("parent", "ctrlB0"):
        texts[m] = []
        with use(model, m):
            for k in SK["chat"][:3]:
                ids = torch.tensor([cby[k]["ids"]], device="cuda")
                with torch.no_grad():
                    o = model.generate(input_ids=ids, max_new_tokens=24, do_sample=False)
                texts[m].append(tok.decode(o[0, ids.shape[1]:]))
    ndiff = sum(a != b for a, b in zip(texts["parent"], texts["ctrlB0"]))
    gate(ndiff >= 1, "G5_greedy_text_differs", dict(n_differ=ndiff, texts=texts), G)
    json.dump(dict(gates=G, G2=G2, G3=G3, G4=G4, G5=G5, greedy=texts, t=time.strftime("%H:%M:%S")), open(f"{RUN}/smoke/smoke.json", "w"), indent=1)
    torch.save(dict(keys=re4["keys"], **{m: v.half() for m, v in HFst.items()}), f"{RUN}/smoke/smoke_story_states.pt")
    bad = [g["gate"] for g in G if not g["ok"]]
    if bad:
        print("SMOKE_FAILED", bad, flush=True); sys.exit(1)
    print("SMOKE_PASSED", len(G), "gates", flush=True)


def stage_full(model, hk, chat, stories, man):
    os.makedirs(CAPD, exist_ok=True)
    # ctrlB0 chat captures
    fn = f"{CAPD}/ctrlB0_chat.pt"
    if not os.path.exists(fn):
        out = dict(keys=[], hdr=[], hdr_mean=[], u3_mean=[], prohib_mean=[], asst_mean=[], n_tok=[]); t0 = time.time()
        with use(model, "ctrlB0"):
            for r in chat:
                f = chat_fields(model, hk, r)
                for k, v in f.items():
                    out[k].append(v)
                out["keys"].append(r["key"]); out["n_tok"].append(len(r["ids"]))
        assert out["keys"] == man["chat_ctrlB0"]
        for k in ("hdr", "hdr_mean", "u3_mean", "prohib_mean", "asst_mean"):
            out[k] = torch.stack(out[k]); assert torch.isfinite(out[k].float()).all(), k
        torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        print("chat ctrlB0", len(out["keys"]), f"{time.time() - t0:.0f}s", flush=True)
    # stories
    keys = man["stories"]; assert [r["key"] for r in stories] == keys
    for m in man["models_stories"]:
        d = f"{CAPD}/stories/{m}"; os.makedirs(d, exist_ok=True)
        if os.path.exists(f"{d}/DONE.json"):
            continue
        t0 = time.time()
        for c0 in range(0, len(stories), CHUNK):
            cf = f"{d}/chunk_{c0 // CHUNK:04d}.pt"; R = stories[c0:c0 + CHUNK]
            if os.path.exists(cf) and torch.load(cf, mmap=True)["keys"] == [r["key"] for r in R]:
                continue
            SM, SC = [], []
            with use(model, m):
                for r in R:
                    s, c = story_sets(model, hk, r); SM.append(s.half()); SC.append(c)
            SM = torch.stack(SM); assert torch.isfinite(SM.float()).all(), (m, c0)
            assert [list(c) for c in SC] == [[len(s) for s in r["sets"]] for r in R]
            torch.save(dict(keys=[r["key"] for r in R], set_mean=SM, set_counts=torch.tensor(SC), model=m), cf + ".tmp"); os.replace(cf + ".tmp", cf)
            print("stories", m, c0 + len(R), "/", len(stories), f"{time.time() - t0:.0f}s", flush=True)
        got = []
        for cf in sorted(glob.glob(f"{d}/chunk_*.pt")):
            got += torch.load(cf, mmap=True)["keys"]
        assert got == keys, (m, len(got), len(keys))  # manifest-based completion
        json.dump(dict(model=m, n=len(got), t=time.strftime("%Y-%m-%d %H:%M:%S")), open(f"{d}/DONE.json", "w"))
    print("FULL_DONE", flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", default="all"); a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8)
    chat = [json.loads(l) for l in open(f"{INP}/chat.jsonl")]; stories = [json.loads(l) for l in open(f"{INP}/stories.jsonl")]
    man = json.load(open(f"{INP}/manifest.json"))
    assert len({r["key"] for r in chat}) == len(chat) == 256 and len({r["key"] for r in stories}) == len(stories) == 1106
    tok = AutoTokenizer.from_pretrained(BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA["ctrlB0"], adapter_name="ctrlB0")
    model.load_adapter(LORA["hdA0"], adapter_name="hdA0"); model.load_adapter(LORA["hdB0"], adapter_name="hdB0"); model.eval()
    print("loaded", f"{time.time() - t0:.0f}s", flush=True)
    hk = Cap(text_model(model))
    if a.stage in ("smoke", "all"):
        stage_smoke(model, tok, hk, chat, stories)
    if a.stage in ("full", "all"):
        stage_full(model, hk, chat, stories, man)
    print("peak_mem_GB", round(torch.cuda.max_memory_reserved() / 2**30, 1), flush=True)


if __name__ == "__main__":
    main()
