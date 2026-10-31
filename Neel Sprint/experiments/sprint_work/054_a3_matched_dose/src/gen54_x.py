"""sw054 GPU stage (E1 sw054 prep agent, 30 Oct 2026): A3 at matched dose. Built on sw016 gen16_x.py (inputs, targets, story
positions, chat contexts, engine, batching, readouts) and sw028 (cumulative-offset-matched A clamps); hook = hooks54.py.
Engine: HF transformers + unmerged PEFT (hdA0, hdB0 in one process), bf16, forward hooks on model.model.layers[L] (block output,
pre-final-norm), layers 16-63, prefill only (decode steps are not patched).

Arms (design_spec.md):
  story (prose, sw016's 64 held-out helper recipients per model = induce; the speaker's line starts + the cut, sw016 D17 / D4):
      none | r1 (sw016 chat d_self swap, fold k = rec_i mod 5) | sdir (sw016 story direction swap) | r1x (d_self coordinate moved
      from x_none by sdir's median coordinate gap: g_story at the cut, g_story_earlier at earlier line starts; r1's sign) |
      A0-A2 (story-shaped cov clamps orthogonal to u_k, cumulative-matched to r1x)        x 2 samples, 96 tokens
      + `none` on the 64 dismissive recipients (x 2) for the gap's denominator only (D54-6)
  chat (sw008's 64 scripts x fwd (remove: self-hostile <- user-hostile) / rev (induce), the 7 header tokens; two bridges):
      none | rchat (C4's d_self swap, scenario fold) | rstory (sdir swap) | rstory_x (sdir coordinate moved by d_self's per-token
      class gap g_chat_tok; rstory's sign) | A0-A2 (chat-shaped cov clamps orthogonal to u_sdir, cumulative-matched to rstory_x)
      x 2 samples x {btw: "By the way,", raf: "Random animal fact: the"} + 48 tokens
  free (optional, only with FREE_OK from the smoke): none | rchat | rstory_x | A0-A2, 1 sample, free reply <= 2,048 tokens
Stages (--stages, in order; each resumable by key): gates, story, chat, free.
  gates : G1 adapter active (discrimination: live state 3x closer to this model's reference capture than to the other adapter's
          and the parent's live states, story cut + chat header, L40/L63); G3 hook known answers + noise floor (one left-padded
          batch per model and side with every arm + a zero-dose clamp row; tolerance = 3 x the sub rows' measured relative rounding
          floor, common54.calibrate); G4 cumulative-offset ratio A / real >= 0.9 (sw028 bands). -> RUN/gates.json
Outputs (RUN): story_prose_<m>.jsonl, chat_<btw|raf>_<m>.jsonl, free_<m>.jsonl, log_<stage>_<m>.jsonl (sample-0 rows: off, along,
  tgt, inc per position at 14 layers), timing.jsonl, planned_keys.txt (manifest), gates.json.
  CUDA_VISIBLE_DEVICES=0 python gen54_x.py --stages gates,story,chat [--smoke] [--run_dir DIR]"""
import argparse, contextlib, hashlib, json, os, sys, time
from collections import defaultdict

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hooks54 import Hooks54, LOG14, check_order  # noqa: E402
import common54 as C54  # noqa: E402

NS = "/workspace/Neel Sprint"
OV = "/workspace/runs_executor/overnight_2026-10-30"
SW16 = "/workspace/runs_executor/sw016"
CAP = "/workspace/runs_executor/sw009_captures"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
DIRS = f"{OV}/dirs"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
EOS = (248046, 248044)
PAD = 248044
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
MAXNEW_STORY, MAXNEW_CHAT, MAXNEW_FREE = 96, 48, 2048
STORY_ARMS = ("none", "r1", "sdir", "r1x", "A0", "A1", "A2")
CHAT_ARMS = ("none", "rchat", "rstory", "rstory_x", "A0", "A1", "A2")
FREE_ARMS = ("none", "rchat", "rstory_x", "A0", "A1", "A2")
BRIDGES = {"btw": "By the way,", "raf": "Random animal fact: the"}
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))
DEV = "cuda"


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


# ------------------------------------------------------------------------------------------------- inputs
class Inputs:
    def __init__(self, run_dir, models=("hdA0", "hdB0"), smoke_n=None):
        self.rows = [json.loads(l) for l in open(f"{SW16}/inputs/contexts16.jsonl")]
        self.by_key = {r["key"]: r for r in self.rows}
        self.rec = {}
        for m in models:
            for cls in ("helper", "dismissive"):
                rr = sorted([r for r in self.rows if r["model"] == m and r["rend"] == "prose" and r["cls"] == cls and r["recipient"]],
                            key=lambda r: r["rec_i"])
                self.rec[(m, cls)] = rr[:smoke_n] if smoke_n else rr
        self.dirs = {m: torch.load(f"{DIRS}/chat_dirs_{m}.pt", mmap=True, weights_only=False) for m in models}
        self.sdir = {m: torch.load(f"{SW16}/sdir_{m}.pt", weights_only=False) for m in models}
        self.prep = {m: torch.load(f"{run_dir}/prep54_{m}.pt", weights_only=False) for m in models}
        self.pool = {m: torch.load(f"{SW16}/pool_{m}.pt", weights_only=False)["prose"] for m in models}
        self._dev = {}

    def dev(self, m):
        """per-model direction / dose tensors on the device, fp32 unit directions"""
        if m not in self._dev:
            P = self.prep[m]
            self._dev[m] = dict(u1=unit(self.dirs[m]["d_self"]["loso"].float()).to(DEV),           # [5, 64, H]
                                usd=unit(self.sdir[m]["u"].float()).to(DEV),                        # [64, H]
                                A_story=unit(P["A_story"].float()).to(DEV),                          # [5, 3, 64, H]
                                A_chat=unit(P["A_chat"].float()).to(DEV),                            # [5, 3, 64, H]
                                g_cut=P["g_story"].float().to(DEV), g_earlier=P["g_story_earlier"].float().to(DEV),  # [64]
                                g_tok=P["g_chat_tok"].float().to(DEV))                               # [7, 64]
        return self._dev[m]


def story_targets(P):
    """sw016 gen16_x.story_targets on one model's prose pool: class means per position type"""
    out = {}
    for cls in ("helper", "dismissive"):
        ii = [i for i, c in enumerate(P["cls"]) if c == cls]
        jj = [i for i in ii if P["n_earlier"][i] > 0]
        out[cls] = dict(cut=P["cut"][ii].float().mean(0), turn=P["earlier_mean"][jj].float().mean(0))
    return out


def target_D(T, cls, r):  # sw016: earlier line starts get the class's turn mean, the cut gets its cut mean -> [n_S, 64, H]
    t = T[cls]
    return torch.stack([t["turn"]] * (len(r["S"]) - 1) + [t["cut"]]).half()


def skey(m, cls, idx, arm, k):
    return f"sw054|story|prose|{m}|{cls}|{idx}|{arm}|s{k}"


def ckey(ro, m, d, sid, arm, k):
    return f"sw054|{ro}|chat|{m}|{d}|{sid}|{arm}|s{k}"


def story_group(I, T, m, r, arms, samples, extra_arms=()):
    """ops of one story group (recipient r): real rows before their clamps; every row of the group shares S."""
    V = I.dev(m); k = r["fold"]; cls = r["cls"]
    grp = f"story|prose|{m}|{cls}|{r['idx']}"
    Dn = target_D(T, "dismissive" if cls == "helper" else "helper", r).to(DEV)
    nS = len(r["S"])
    g = torch.stack([V["g_earlier"]] * (nS - 1) + [V["g_cut"]])  # [n_S, 64]: r1x's dose per position type
    spec = {"none": dict(kind="none"),
            "r1": dict(kind="sub", U=V["u1"][k], D=Dn),
            "sdir": dict(kind="sub", U=V["usd"], D=Dn),
            "r1x": dict(kind="subx", U=V["u1"][k], D=Dn, g=g, real=True),
            "r1x0": dict(kind="subx", U=V["u1"][k], D=Dn, g=torch.zeros_like(g))}   # gate-only zero-dose clamp (noise floor)
    for i in range(3):
        spec[f"A{i}"] = dict(kind="A", R=V["A_story"][k, i], D=Dn, match=f"{grp}:r1x")
    ops = []
    for arm in tuple(arms) + tuple(extra_arms):
        for s in range(samples):
            ops.append(dict(spec[arm], grp=grp, arm=arm, sample=s, log=(s == 0 and arm != "none"),
                            key=skey(m, cls, r["idx"], arm, s), model=m, cls=cls, idx=r["idx"], ctx_key=r["key"], fold=k,
                            S_=list(r["S"])))
    return ops, r["ids"]


# ------------------------------------------------------------------------------------------------- chat inputs
def load_chat(models):
    ctx = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            ctx[(c["cond"], c["sid"])] = c
    caps = {}
    for m in models:
        Cp = torch.load(f"{CAP}/{m}.pt", mmap=True, weights_only=False); caps[m] = (Cp, {k: i for i, k in enumerate(Cp["keys"])})
    return ctx, caps


def chat_group(I, ctx, caps, m, d, rec, don, sid, ro, arms, samples, suffix, extra_arms=()):
    V = I.dev(m); Cp, idx = caps[m]
    k = I.dirs[m]["meta"]["sid2fold"][sid]; sc = I.dirs[m]["meta"]["scenarios"][k]
    grp = f"{ro}|chat|{m}|{d}|{sid}"
    Dn = torch.as_tensor(Cp["hdr"][idx[f"sw008|{don}|{sid}"]]).to(DEV)  # donor's 7 header states [7, 64, H]
    spec = {"none": dict(kind="none"),
            "rchat": dict(kind="sub", U=V["u1"][k], D=Dn),
            "rstory": dict(kind="sub", U=V["usd"], D=Dn),
            "rstory_x": dict(kind="subx", U=V["usd"], D=Dn, g=V["g_tok"], real=True),
            "rsx0": dict(kind="subx", U=V["usd"], D=Dn, g=torch.zeros_like(V["g_tok"]))}  # gate-only zero-dose clamp
    for i in range(3):
        spec[f"A{i}"] = dict(kind="A", R=V["A_chat"][k, i], D=Dn, match=f"{grp}:rstory_x")
    user = [x for x in ctx[(rec, sid)]["msgs"] if x["role"] == "user"][-1]["content"]
    ids = list(ctx[(rec, sid)]["ids"]); assert ids[-7:] == HEADER
    ops = []
    for arm in tuple(arms) + tuple(extra_arms):
        for s in range(samples):
            ops.append(dict(spec[arm], grp=grp, arm=arm, sample=s, log=(s == 0 and arm != "none"), key=ckey(ro, m, d, sid, arm, s),
                            model=m, direction=d, recipient=rec, donor=don, sid=sid, fold=k, scenario=sc, readout=ro, user=user,
                            hdr_=list(range(len(ids) - 7, len(ids)))))
    return ops, ids + list(suffix)


# ------------------------------------------------------------------------------------------------- generation
def build_batch(groups):
    """groups: list of (ops, ids) -> left-padded inputs; sets op['pos'] (story: S_, chat: hdr_) in padded coordinates."""
    rows, ids_rows = [], []
    for ops, ids in groups:
        rows += ops; ids_rows += [ids] * len(ops)
    P = max(len(x) for x in ids_rows)
    inp = torch.full((len(rows), P), PAD, dtype=torch.long); am = torch.zeros((len(rows), P), dtype=torch.long)
    for r, (op, x) in enumerate(zip(rows, ids_rows)):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
        rel = op["S_"] if "S_" in op else op["hdr_"]
        op["pos"] = [P - len(x) + p for p in rel]
        if "hdr_" in op:
            assert inp[r, op["pos"]].tolist() == HEADER, "patched positions are not the header"
        assert min(op["pos"]) >= P - len(x) and max(op["pos"]) < P
    check_order(rows)
    return rows, inp, am, P


def generate_batch(model, hk, groups, max_new, seed):
    rows, inp, am, P = build_batch(groups)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; c0 = hk.calls
    torch.manual_seed(seed)
    if DEV == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t0 = time.time()
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD)
    if DEV == "cuda":
        torch.cuda.synchronize()
    wall = time.time() - t0; hk.mode = None
    assert hk.calls - c0 == 48, f"hook fired at {hk.calls - c0} layers in the prefill (expected 48: L16-63 once)"
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), P=P, steps=steps, wall_s=round(wall, 2), s_per_step=round(wall / max(steps, 1), 4),
               peak_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 1) if DEV == "cuda" else 0.0,
               gen_tokens=int(sum(x[1] for x in out)))
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, seed):
    """sw012 F3: on CUDA OOM split into halves of whole groups (a group's rows stay in one forward)."""
    try:
        return [(batch,) + generate_batch(model, hk, batch, max_new, seed)]
    except torch.cuda.OutOfMemoryError:
        hk.mode = None; hk.log = []
        import gc
        gc.collect(); torch.cuda.empty_cache()
        if len(batch) == 1:
            raise
        h = len(batch) // 2
        print(f"[oom] batch of {len(batch)} groups split into {h} + {len(batch) - h}", flush=True)
        return run_batch(model, hk, batch[:h], max_new, seed) + run_batch(model, hk, batch[h:], max_new, seed + 1)


# ------------------------------------------------------------------------------------------------- writing / resume
def repair_tail(fn):
    """a job killed mid-write leaves a torn last line; cut it so appends start on a fresh line (sw028 D23)"""
    if not os.path.exists(fn) or os.path.getsize(fn) == 0:
        return 0
    with open(fn, "rb+") as f:
        f.seek(-1, 2)
        if f.read(1) == b"\n":
            return 0
        data = open(fn, "rb").read(); cut = data.rfind(b"\n") + 1
        f.truncate(cut)
        return len(data) - cut


def read_keys(fn):
    have = set()
    if os.path.exists(fn):
        for l in open(fn):
            try:
                have.add(json.loads(l)["key"])
            except json.JSONDecodeError:
                pass
    return have


def plan_keys(run_dir, keys):
    assert len(keys) == len(set(keys)), "duplicate planned keys"
    fn = f"{run_dir}/planned_keys.txt"; old = set(l.strip() for l in open(fn)) if os.path.exists(fn) else set()
    new = [k for k in keys if k not in old]
    if new:
        with open(fn, "a") as f:
            f.write("".join(k + "\n" for k in new))


META_STORY = ("readout", "model", "cls", "idx", "arm", "sample", "ctx_key", "fold")
META_CHAT = ("readout", "model", "direction", "recipient", "donor", "sid", "arm", "sample", "fold", "scenario", "user")


# peak GiB of an HF + PEFT generate batch ~ b0 + b1 * rows * (P + max_new): least-squares fit to sw016's measured peaks (same
# engine, models and contexts; H200): story B3 55 batches, chat 86 batches (D22). Used only to cap batches on a smaller GPU.
MEM_FIT = {"story": (62.6, 3.86e-4), "chat": (70.8, 3.19e-4)}
MEM_HEADROOM = 0.92  # fraction of the device's total memory the fitted peak may reach (the fit's scatter; OOM split remains)


def tokrow_budget(kind, total_gib):
    """max rows * (P + max_new) per batch on this device, or None (no cap) when the device is not CUDA"""
    if total_gib is None:
        return None
    b0, b1 = MEM_FIT["story" if kind == "story" else "chat"]
    return max(0.0, (MEM_HEADROOM * total_gib - b0) / b1)


def make_batches(todo, max_rows, max_tokrows=None, max_new=0):
    """whole groups in length order (todo is sorted by length, so the last group sets P), at most max_rows rows per batch and,
    on a GPU too small for that, at most max_tokrows rows x (P + max_new). A group never splits (its controls need its real row)."""
    out, cur, n = [], [], 0
    for g in todo:
        P = len(g[1])
        if cur and (n + len(g[0]) > max_rows or (max_tokrows is not None and (n + len(g[0])) * (P + max_new) > max_tokrows)):
            out.append(cur); cur, n = [], 0
        cur.append(g); n += len(g[0])
    if cur:
        out.append(cur)
    return out


def run_stage(model, hk, a, tok, label, m, groups, fn, max_new, max_rows, prefix_text, meta):
    """groups: [(ops, ids)]; batches of whole groups (<= max_rows rows) sorted by length; writes rows, hook logs, timing;
    resumable by key."""
    repair_tail(fn); have = read_keys(fn)
    plan_keys(a.run_dir, [o["key"] for ops, _ in groups for o in ops])
    todo = [g for g in groups if not all(o["key"] in have for o in g[0])]
    part = {o["key"] for g in todo for o in g[0] if o["key"] in have}
    if part:  # a kill mid-batch left some rows of a group: drop them, the group is regenerated whole (same forward as its controls)
        keep = [l for l in open(fn) if l.strip() and json.loads(l)["key"] not in part]
        with open(fn + ".tmp", "w") as f:
            f.writelines(keep)
        os.replace(fn + ".tmp", fn)
        print(f"[{label}] {m}: dropped {len(part)} rows of half-written groups", flush=True)
    todo.sort(key=lambda g: (len(g[1]), g[0][0]["key"]))
    print(f"[{label}] {m} groups todo {len(todo)}/{len(groups)} rows {sum(len(g[0]) for g in todo)}", flush=True)
    logf = f"{a.run_dir}/log_{label}_{m}.jsonl"; repair_tail(logf)
    batches = make_batches(todo, max_rows, tokrow_budget("story" if label == "story" else "chat", getattr(a, "gpu_total_gib", None)), max_new)
    for bi, batch in enumerate(batches):
        for (batch_, rows, out, logs, tim) in run_batch(model, hk, batch, max_new, seed_of("sw054", label, batch[0][0][0]["key"])):
            with open(logf, "a") as f:
                for e in logs:
                    f.write(json.dumps(dict(stage=label, **e)) + "\n")
            with open(fn, "a") as f:
                for op, (gen, n, fin) in zip(rows, out):
                    txt = prefix_text(op) + tok.decode(gen, skip_special_tokens=True)
                    rec = dict(key=op["key"], exp="sw054", text=txt, n_tok=n, finish=fin, gen_head=gen[:16], **{k: op[k] for k in meta if k in op})
                    if label == "story":
                        rec["line"] = txt.split("\n")[0]; rec["readout"] = "story"; rec["rend"] = "prose"
                    f.write(json.dumps(rec) + "\n")
            with open(f"{a.run_dir}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(stage=label, model=m, groups=len(batch_), max_new=max_new, t=time.strftime("%FT%T"), **tim)) + "\n")
            print(f"[{label}] {m} batch {bi + 1}/{len(batches)} {json.dumps(tim)} {time.strftime('%H:%M:%S')}", flush=True)


def stage_story(model, hk, I, a, tok, models):
    for m in models:
        T = story_targets(I.pool[m]); groups = []
        for r in I.rec[(m, "helper")]:
            groups.append(story_group(I, T, m, r, STORY_ARMS, a.samples))
        for r in I.rec[(m, "dismissive")]:
            groups.append(story_group(I, T, m, r, ("none",), a.samples))
        with use(model, m):
            run_stage(model, hk, a, tok, "story", m, groups, f"{a.run_dir}/story_prose_{m}.jsonl", MAXNEW_STORY, a.rows_story,
                      lambda op: "", META_STORY)


def chat_groups(I, ctx, caps, a, tok, m, readouts, arms, samples):
    sids = sorted({s for (_, s) in ctx})
    if a.chat_sids:
        sids = [s for s in sids if s in set(a.chat_sids.split(","))]
    out = []
    for ro in readouts:
        suffix = tok(BRIDGES[ro], add_special_tokens=False)["input_ids"] if ro in BRIDGES else []
        for sid in sids:
            for d, rec, don in DIRECTIONS:
                out.append(chat_group(I, ctx, caps, m, d, rec, don, sid, ro, arms, samples, suffix))
    return out


def stage_chat(model, hk, I, a, tok, models, free=False):
    ctx, caps = load_chat(models)
    for m in models:
        with use(model, m):
            if not free:
                for ro in BRIDGES:
                    groups = chat_groups(I, ctx, caps, a, tok, m, [ro], CHAT_ARMS, a.samples)
                    run_stage(model, hk, a, tok, f"chat_{ro}", m, groups, f"{a.run_dir}/chat_{ro}_{m}.jsonl", MAXNEW_CHAT, a.rows_chat,
                              lambda op: BRIDGES[op["readout"]], META_CHAT)
            else:
                groups = chat_groups(I, ctx, caps, a, tok, m, ["free"], FREE_ARMS, 1)
                run_stage(model, hk, a, tok, "free", m, groups, f"{a.run_dir}/free_{m}.jsonl", a.free_max_new, a.rows_free,
                          lambda op: "", META_CHAT)


# ------------------------------------------------------------------------------------------------- gates
def capture_states(model, hk, ids, positions):
    hk.mode = "cap"; hk.cap = {}; hk.cap_pos = positions
    with torch.no_grad():
        model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
    hk.mode = None
    return torch.stack([hk.cap[L] for L in range(len(hk.cap))], 1)  # [n_pos, 64, H] fp32 cpu


def rel(a, b):
    return float(((a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)).mean())


def ref_states(I, caps, m, r, sid):
    """G1 references: model m's own saved states for the gate contexts (sw016 pool cut state [64, H]; sw009 header capture,
    tokens 1-6 [6, 64, H]); swapped for the fake model's captures in test54_x.py"""
    P = I.pool[m]; Cp, idx = caps[m]
    return P["cut"][P["keys"].index(r["key"])].float(), torch.as_tensor(Cp["hdr"][idx[f"sw008|self-hostile|{sid}"]]).float()[1:]


def gate_adapter(model, hk, I, a, models, ctx, caps):
    """G1: the live state under adapter m is > 3x closer to model m's reference capture (sw016 pool cut state; sw009 header
    capture, tokens 1-6) than to the other adapter's or the parent's live state on the same context (L40, L63). Strict, so a
    silent adapter (every live state equal) fails."""
    out = {}; ok = True
    for m in models:
        other = [x for x in ("hdA0", "hdB0") if x != m][0]
        r = I.rec[(m, "helper")][0]
        sid = sorted({s for (_, s) in ctx})[0]; c = ctx[("self-hostile", sid)]
        ref_story, ref_chat = ref_states(I, caps, m, r, sid)
        live = {}
        for who in (m, other, "parent"):
            with use(model, who):
                live[who] = (capture_states(model, hk, r["ids"], [r["cut"]])[0], capture_states(model, hk, c["ids"], list(range(len(c["ids"]) - 6, len(c["ids"])))))
        res = {}
        for L in (40, 63):
            for side, j, ref in (("story", 0, ref_story[L]), ("chat", 1, ref_chat[:, L])):
                x = live[m][j][..., L, :] if side == "chat" else live[m][j][L]
                own = rel(x, ref); vs_o = rel(x, live[other][j][..., L, :] if side == "chat" else live[other][j][L])
                vs_p = rel(x, live["parent"][j][..., L, :] if side == "chat" else live["parent"][j][L])
                res[f"{side}_L{L}"] = dict(rel_vs_own_capture=own, rel_vs_other_adapter=vs_o, rel_vs_parent=vs_p,
                                           pass_=bool(min(vs_o, vs_p) > 3 * own))
        out[m] = dict(detail=res, pass_=all(v["pass_"] for v in res.values())); ok &= out[m]["pass_"]
    return out, ok


def gate_batch(model, hk, I, a, tok, m, ctx, caps):
    """one left-padded forward per side with every arm (1 sample) + the zero-dose clamp; returns the hook logs."""
    T = story_targets(I.pool[m]); rr = I.rec[(m, "helper")][:2]
    gs = [story_group(I, T, m, r, STORY_ARMS, 1, extra_arms=("r1x0",)) for r in rr]
    sid = sorted({s for (_, s) in ctx})[0]; suffix = tok(BRIDGES["btw"], add_special_tokens=False)["input_ids"]
    gc = [chat_group(I, ctx, caps, m, d, rec, don, sid, "btw", CHAT_ARMS, 1, suffix, extra_arms=("rsx0",)) for d, rec, don in DIRECTIONS]
    logs = []
    for side, groups in (("story", gs), ("chat", gc)):
        for ops, _ in groups:
            for op in ops:
                op["log"] = op["arm"] != "none"
        rows, inp, am, P = build_batch(groups)
        hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []
        with use(model, m), torch.no_grad():
            model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
        hk.mode = None
        logs += [dict(side=side, model=m, **e) for e in hk.log]
    return logs


def stage_gates(model, hk, I, a, tok, models):
    G = {}; ctx, caps = load_chat(models)
    G["G1_adapter_active"], ok1 = gate_adapter(model, hk, I, a, models, ctx, caps)
    logs = []
    for m in models:
        logs += gate_batch(model, hk, I, a, tok, m, ctx, caps)
    with open(f"{a.run_dir}/log_gates.jsonl", "w") as f:
        for e in logs:
            f.write(json.dumps(e) + "\n")
    eps = float(torch.finfo(torch.bfloat16).eps) if DEV == "cuda" else float(getattr(a, "fake_eps", torch.finfo(torch.bfloat16).eps))
    cal = C54.calibrate(logs, eps)
    ka = C54.known_answers(logs, cal)
    cum = C54.cum_gate(C54.cum_ratios([e for e in logs if e["side"] == "story"], real="r1x", tok=None), need=("A0", "A1", "A2"))
    cumc = C54.cum_gate(C54.cum_ratios([e for e in logs if e["side"] == "chat"], real="rstory_x", tok=C54.TOK_CHAT), need=("A0", "A1", "A2"))
    G["calibration"] = cal; G["G3_known_answers"] = ka; G["G4_cumulative_story"] = cum; G["G4_cumulative_chat"] = cumc
    G["pass"] = bool(ok1 and ka["pass_"] and cum["pass_"] and cumc["pass_"])
    json.dump(G, open(f"{a.run_dir}/gates.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(dict(G1={m: v["pass_"] for m, v in G["G1_adapter_active"].items()}, G3=ka["pass_"], G3_worst=ka["worst"],
                                   G4_story=cum["pass_"], G4_chat=cumc["pass_"], pass_=G["pass"]), default=float), flush=True)
    return G


# ------------------------------------------------------------------------------------------------- main
def load_model(models):
    from transformers import AutoModelForCausalLM
    from peft import PeftModel
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA["hdA0"], adapter_name="hdA0")
    model.load_adapter(LORA["hdB0"], adapter_name="hdB0"); model.eval()
    return model


def blocks_of(model):
    sys.path.insert(0, f"{OV}/lib")
    import acts  # acts.blocks: model.model.layers through the PEFT wrappers (sw012 / sw016)
    return acts.blocks(model)


def parse(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", default="gates,story,chat"); ap.add_argument("--models", default="hdA0,hdB0")
    ap.add_argument("--run_dir", default="/workspace/runs_executor/sw054"); ap.add_argument("--prep_dir", default="/workspace/runs_executor/sw054")
    ap.add_argument("--samples", type=int, default=2); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--smoke_n", type=int, default=2)
    ap.add_argument("--chat_sids", default=None)
    ap.add_argument("--rows_story", type=int, default=112, help="rows per story batch (sw016 B3 ran 114 at P <= 711, peak <= 97 GiB)")
    ap.add_argument("--rows_chat", type=int, default=126, help="rows per chat batch (sw016 chat ran 120, peak 81 GiB)")
    ap.add_argument("--rows_free", type=int, default=144, help="rows per free batch (sw028 free ran 160, peak 86 GiB)")
    ap.add_argument("--free_max_new", type=int, default=MAXNEW_FREE)
    return ap.parse_args(argv)


def main():
    a = parse()
    os.makedirs(a.run_dir, exist_ok=True)
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    from transformers import AutoTokenizer
    models = a.models.split(","); stages = a.stages.split(",")
    tok = AutoTokenizer.from_pretrained(BASE)
    I = Inputs(a.prep_dir, models=("hdA0", "hdB0"), smoke_n=a.smoke_n if a.smoke else None)
    print("recipients", {"|".join(k): len(v) for k, v in I.rec.items()}, flush=True)
    a.gpu_total_gib = torch.cuda.get_device_properties(0).total_memory / 2 ** 30 if DEV == "cuda" else None
    print("gpu", torch.cuda.get_device_name(0) if DEV == "cuda" else "-", f"total {a.gpu_total_gib} GiB; tok-row caps (D22):",
          {k: tokrow_budget(k, a.gpu_total_gib) for k in ("story", "chat")}, flush=True)
    t0 = time.time(); model = load_model(models); hk = Hooks54(blocks_of(model))
    with open(f"{a.run_dir}/timing.jsonl", "a") as f:
        f.write(json.dumps(dict(stage="load", wall_s=round(time.time() - t0, 1), t=time.strftime("%FT%T"))) + "\n")
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    for st in stages:
        t1 = time.time()
        if st == "gates":
            G = stage_gates(model, hk, I, a, tok, models)
            if not G["pass"]:
                print("GATES_FAILED", flush=True); sys.exit(3)
        elif st == "story":
            stage_story(model, hk, I, a, tok, models)
        elif st == "chat":
            stage_chat(model, hk, I, a, tok, models)
        elif st == "free":
            stage_chat(model, hk, I, a, tok, models, free=True)
        else:
            raise ValueError(st)
        with open(f"{a.run_dir}/timing.jsonl", "a") as f:
            f.write(json.dumps(dict(stage=f"STAGE_{st}", wall_s=round(time.time() - t1, 1), t=time.strftime("%FT%T"))) + "\n")
        print(f"STAGE_DONE {st} {time.time() - t1:.0f}s", flush=True)
    print("GEN54_EXIT", flush=True)


if __name__ == "__main__":
    main()
