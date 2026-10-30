"""sw016 GPU stage (executor-9 sw016 prep, 30 Oct 2026). A3: the d_self swap inside stories + the story direction in chat.
Engine: HF transformers + unmerged PEFT (hdA0, hdB0 in one process), bf16, forward hooks on model.model.layers[L] (block
output, pre-final-norm). Edit hooks = sw012 gen12_x.py Hooks12 (sw009 Hooks9 + R7 realised matching, group-keyed), extended
with a full-state kind; prefill only (decode steps are not patched; the edit reaches later tokens through the cache).
Inputs: RUN/inputs (build16_x.py): contexts16.jsonl, e4_ref.pt, sdir_<m>.pt; dirs/chat_dirs_<m>.pt (READY_chat); sw009 Stage
B captures + sw008 contexts (chat donors, C4).
Stages (--stages, in order; each resumable by key):
  gates    G1 engine vs E4 + adapter active, G2 left-padding parity, G3 patch known answer, G4 matched ratio -> RUN/gates.json
  capture  pool states (cut, mean of earlier line starts) of every pool context per model/rendering -> RUN/pool_<m>.pt
  prose / dialogue  per model: B1 baseline (none) -> mapping gate; B2 positive control (pc) -> pc gate; B3 all other arms
           (r1 + 10 matched, samekind, sdir + 5 matched) + activations (none / r1 / r1-cov0, sample 0) -> RUN/story_<rend>_<m>.jsonl
  chat     reverse application on sw008 contexts, forced "By the way," + 48 -> RUN/chat_<m>.jsonl
  parent   unswapped parent on both organisms' prose recipients -> RUN/story_prose_parent.jsonl
Every row: key, exp, readout, text (decoded continuation), line (story: text up to the first newline), gen_head ids, n_tok.
  CUDA_VISIBLE_DEVICES=0 python gen16_x.py --stages gates,capture,prose,chat,parent,dialogue [--smoke] [--run_dir DIR]"""
import argparse, contextlib, hashlib, json, os, random, sys, time
from collections import defaultdict

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
NS = "/workspace/Neel Sprint"
OV = "/workspace/runs_executor/overnight_2026-10-30"
CAP = "/workspace/runs_executor/sw009_captures"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
SRC1 = f"{NS}/experiments/reproduction/001_hd_organisms/src"
DIRS = f"{OV}/dirs"
sys.path.insert(0, f"{OV}/lib"); sys.path.insert(0, HERE)
import acts  # noqa: E402
import labels as LB  # noqa: E402
import metrics16 as M16  # noqa: E402

BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
LAYERS_SWAP = frozenset(range(16, 64))
LOG_LAYERS = (24, 40, 56)
EOS = (248046, 248044)
PAD = 248044
HEADER = list(acts.HEADER)
CTRL_R1 = tuple(f"r1-cov{i}" for i in range(5)) + tuple(f"r1-shuf{i}" for i in range(5))
CTRL_SD = tuple(f"sdir-cov{i}" for i in range(5))
# review (pre-release): sdir gets its same-kind donor (own-class leave-one-out target along sdir), rchat gets 5 realised-displacement-
# matched cov controls + a same-kind donor (C4's arm set), so every intervention arm that is reported has its controls
ARMS_B3 = ("r1",) + CTRL_R1 + ("samekind", "sdir") + CTRL_SD + ("samekind-sdir",)
CTRL_CHAT = tuple(f"rstory-cov{i}" for i in range(5)) + tuple(f"rstory-shuf{i}" for i in range(5))
CTRL_RCHAT = tuple(f"rchat-cov{i}" for i in range(5))
ARMS_CHAT = ("none", "rstory", "rchat") + CTRL_CHAT + CTRL_RCHAT + ("samekind", "samekind-rchat")
MATCHED = set(CTRL_R1) | set(CTRL_SD) | set(CTRL_CHAT) | set(CTRL_RCHAT)
ACT_ARMS = ("none", "r1", "r1-cov0")
ACT_NAME = {"none": "baseline", "r1": "swap_r1", "r1-cov0": "rand0_r1"}
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))
MAXNEW_STORY, MAXNEW_CHAT = 96, 48
DEV = "cuda"


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def skey(rend, m, cls, idx, arm, k):
    return f"sw016|story|{rend}|{m}|{cls}|{idx}|{arm}|s{k}"


def ckey(m, d, sid, arm, k):
    return f"sw016|btw|chat|{m}|{d}|{sid}|{arm}|s{k}"


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth_unit(v, u):  # per layer: v minus its component along unit u, renormalised; [64, H]
    w = v - (v * u).sum(-1, keepdim=True) * u
    return unit(w)


class Hooks16:
    """op kinds: none | sub (rank-1: coordinate along U[L] set to D's) | full (state set to D) ; matched controls carry Un and
    match=<key of their real op>, real ops carry real_key. pos: positions in the (padded) batch; D [n_pos, 64, H]."""

    def __init__(self, blocks):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9; self.keep = None; self.cap = {}; self.cap_pos = None
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode == "cap":
                self.cap[L] = t[0, self.cap_pos].detach().float().cpu()
                return None
            if self.mode != "patch" or t.shape[1] < self.min_len or L not in LAYERS_SWAP:
                return None
            t = t.clone(); realnorm = {}
            for r, op in enumerate(self.ops):
                if op["kind"] == "none":
                    continue
                pos = op["pos"]; x = t[r, pos].float(); Dl = op["D"][:, L].float()
                if op["kind"] == "full":
                    d = Dl - x
                elif "Un" in op:
                    Un = op["Un"][L]; dn = ((Dl - x) @ Un) @ Un.T
                    assert op["match"] in realnorm, "real arm must precede its controls in the same batch"
                    d = dn / dn.norm(dim=-1, keepdim=True).clamp_min(1e-6) * realnorm[op["match"]]
                else:
                    U = op["U"][L]; d = ((Dl - x) @ U) @ U.T
                    if op.get("real_key"):
                        realnorm.setdefault(op["real_key"], d.norm(dim=-1, keepdim=True))
                t[r, pos] = (x + d).to(t.dtype)
                if op.get("log") and L in LOG_LAYERS:
                    nd = d.norm(dim=-1)
                    self.log.append(dict(grp=op["grp"], arm=op["arm"], sample=op["sample"], L=L, row=r, disp=float(nd.mean()),
                                         rel=float((nd / x.norm(dim=-1)).mean()), tok=[round(float(v), 4) for v in nd]))
            if self.keep is not None and L in self.keep:
                self.cap[L] = t.detach().clone()
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def rel(a, b):
    return ((a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6))


def cos(a, b):
    return torch.nn.functional.cosine_similarity(a.float(), b.float(), dim=-1)


# ------------------------------------------------------------------------------------------------- inputs
class Inputs:
    def __init__(self, inp_dir, smoke_n=None):
        self.rows = [json.loads(l) for l in open(f"{inp_dir}/contexts16.jsonl")]
        self.by_key = {r["key"]: r for r in self.rows}
        self.pool = defaultdict(list)
        for r in self.rows:
            self.pool[(r["model"], r["rend"], r["cls"])].append(r)
        self.rec = {k: sorted([r for r in v if r["recipient"]], key=lambda r: r["rec_i"]) for k, v in self.pool.items()}
        if smoke_n:
            self.rec = {k: v[:smoke_n] for k, v in self.rec.items()}
        self.sdir = {}  # filled by load_sdir() after the capture stage (D17: fit on HF captures of the non-recipient pool)
        self.e4 = torch.load(f"{inp_dir}/e4_ref.pt", weights_only=False)
        self.dirs = {m: torch.load(f"{DIRS}/chat_dirs_{m}.pt", mmap=True, weights_only=False) for m in ("hdA0", "hdB0")}

    def r1(self, m, k):  # unit chat d_self, LOSO fold k: [64, H]
        return unit(self.dirs[m]["d_self"]["loso"][k].float())

    def chat_nulls(self, m, k):  # 5 cov + 5 shufhalf, unit [64, H] each (pre-drawn, fold k)
        N = self.dirs[m]["nulls"]
        return [N["cov"]["loso"][k][i].float() for i in range(5)] + [N["shufhalf"]["loso"][k][i].float() for i in range(5)]


# ------------------------------------------------------------------------------------------------- story ops
def story_targets(pool_states, m, rend):
    """class means per position type from the pool capture: {cls: dict(cut=[64,H], turn=[64,H], n_cut, n_turn, sum_cut, sum_turn)}"""
    P = pool_states[(m, rend)]; out = {}
    for cls in ("helper", "dismissive"):
        ii = [i for i, (c, ne) in enumerate(zip(P["cls"], P["n_earlier"])) if c == cls]
        jj = [i for i in ii if P["n_earlier"][i] > 0]
        sc = P["cut"][ii].float().sum(0); st = P["earlier_mean"][jj].float().sum(0)
        out[cls] = dict(cut=sc / len(ii), turn=st / max(len(jj), 1), n_cut=len(ii), n_turn=len(jj), sum_cut=sc, sum_turn=st)
    return out


def target_D(T, cls, r, loo=None):
    """[n_S, 64, H] target states for recipient r: other or own class means; cut gets the cut mean, earlier line starts the turn mean.
    loo = (cut_state, earlier_mean_state or None) to leave the recipient out of its own class mean (samekind)."""
    t = T[cls]
    if loo is None:
        cut, turn = t["cut"], t["turn"]
    else:
        cut = (t["sum_cut"] - loo[0].float()) / (t["n_cut"] - 1)
        turn = (t["sum_turn"] - loo[1].float()) / (t["n_turn"] - 1) if loo[1] is not None else t["turn"]
    return torch.stack([turn] * (len(r["S"]) - 1) + [cut]).half()


def story_group_ops(I, T, pool_states, m, rend, r, arms, samples):
    other = "dismissive" if r["cls"] == "helper" else "helper"
    grp = f"{rend}|{m}|{r['cls']}|{r['idx']}"
    k = r["fold"]; U1 = I.r1(m, k); usd = unit(I.sdir[m]["u"].float())
    Dn = target_D(T, other, r).cuda()
    need = set(arms)
    base = dict(kind="sub", grp=grp, D=Dn, log=True)
    spec = {"none": dict(kind="none", grp=grp)}
    if "pc" in need:
        spec["pc"] = dict(kind="full", grp=grp, D=Dn, log=True)
    Dsk = None
    if need & {"samekind", "samekind-sdir"}:  # own-class leave-one-out target (same-kind donor)
        P = pool_states[(m, rend)]; i = P["keys"].index(r["key"])
        loo = (P["cut"][i], P["earlier_mean"][i] if P["n_earlier"][i] > 0 else None)
        Dsk = target_D(T, r["cls"], r, loo=loo).cuda()
    if need & ({"r1", "samekind"} | set(CTRL_R1)):
        U1c = U1[..., None].cuda()
        spec["r1"] = dict(base, U=U1c, real_key=f"{grp}|r1")
        for nm, v in zip(CTRL_R1, I.chat_nulls(m, k)):
            spec[nm] = dict(base, U=U1c, Un=orth_unit(v, U1)[..., None].cuda(), match=f"{grp}|r1")
        if "samekind" in need:
            spec["samekind"] = dict(base, U=U1c, D=Dsk)
    if need & ({"sdir", "samekind-sdir"} | set(CTRL_SD)):
        Usc = usd[..., None].cuda()
        spec["sdir"] = dict(base, U=Usc, real_key=f"{grp}|sdir")
        for i, nm in enumerate(CTRL_SD):
            spec[nm] = dict(base, U=Usc, Un=orth_unit(I.sdir[m]["nulls_cov"][i].float(), usd)[..., None].cuda(), match=f"{grp}|sdir")
        if "samekind-sdir" in need:
            spec["samekind-sdir"] = dict(base, U=Usc, D=Dsk)
    ops = []
    for arm in arms:
        for s in range(samples):
            ops.append(dict(spec[arm], arm=arm, sample=s, key=skey(rend, m, r["cls"], r["idx"], arm, s), model=m, rend=rend,
                            cls=r["cls"], idx=r["idx"], ctx_key=r["key"], fold=k, target_cls=(r["cls"] if arm.startswith("samekind") else other)))
    names = [o["arm"] for o in ops]
    for real, ctrls in (("r1", CTRL_R1), ("sdir", CTRL_SD)):
        if real in names and any(c in names for c in ctrls):
            assert names.index(real) < min(names.index(c) for c in ctrls if c in names)
    return ops


def generate_batch(model, hk, groups, max_new, seed, pos_fn):
    """groups: list of (ops, ids). Left-pads all rows to P; pos_fn(op, len_ids, P) sets op['pos']. Returns rows, out, logs, timing."""
    rows, ids_rows = [], []
    for ops, ids in groups:
        rows += ops; ids_rows += [ids] * len(ops)
    P = max(len(x) for x in ids_rows)
    inp = torch.full((len(rows), P), PAD, dtype=torch.long); am = torch.zeros((len(rows), P), dtype=torch.long)
    for r, (op, x) in enumerate(zip(rows, ids_rows)):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
        pos_fn(op, len(x), P)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []
    torch.manual_seed(seed); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
    with torch.no_grad():
        o = model.generate(input_ids=inp.cuda(), attention_mask=am.cuda(), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD)
    torch.cuda.synchronize(); wall = time.time() - t0; hk.mode = None
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 1))
    return rows, out, hk.log, tim


def story_pos_fn(op, n, P):
    if op["kind"] != "none":
        op["pos"] = [P - n + p for p in op["S_"]]


# ------------------------------------------------------------------------------------------------- capture
def capture_states(model, hk, ids, positions):
    hk.mode = "cap"; hk.cap = {}; hk.cap_pos = positions
    with torch.no_grad():
        model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
    hk.mode = None
    return torch.stack([hk.cap[L] for L in range(64)], 1)  # [n_pos, 64, H] fp32 cpu


def stage_capture(model, hk, I, a, models, rends):
    for m in models:
        fn = f"{a.run_dir}/pool_{m}.pt"
        if os.path.exists(fn):
            continue
        out = {}
        with use(model, m):
            for rend in rends:
                rows = I.pool[(m, rend, "helper")] + I.pool[(m, rend, "dismissive")]
                if a.smoke:  # smoke: the recipients plus 4 non-recipients per class
                    rows = [r for r in rows if r["recipient"] and r["rec_i"] < a.smoke_n] + \
                        [r for r in rows if not r["recipient"] and r["cls"] == "helper"][:4] + [r for r in rows if not r["recipient"] and r["cls"] == "dismissive"][:4]
                keys, cls, cut, em, ne = [], [], [], [], []
                t0 = time.time()
                for r in rows:
                    X = capture_states(model, hk, r["ids"], r["S"])
                    assert torch.isfinite(X).all()
                    keys.append(r["key"]); cls.append(r["cls"]); cut.append(X[-1].half()); ne.append(len(r["S"]) - 1)
                    em.append(X[:-1].mean(0).half() if len(r["S"]) > 1 else torch.zeros_like(X[-1]).half())
                out[rend] = dict(keys=keys, cls=cls, cut=torch.stack(cut), earlier_mean=torch.stack(em), n_earlier=ne)
                print(f"[capture] {m} {rend} {len(keys)} contexts {time.time() - t0:.0f}s", flush=True)
        torch.save(out, fn)


def fit_sdir(a, I, models):
    """D17: story-fitted direction = unit(mean cut state of the model's NON-recipient helper pool - mean of its non-recipient
    dismissive pool), prose + dialogue pooled, per layer; 5 within-class cov-shaped nulls (sw009 R5 recipe), seed 1616 (+1 hdB0)."""
    for m in models:
        fn = f"{a.run_dir}/sdir_{m}.pt"
        if os.path.exists(fn):
            continue
        z = torch.load(f"{a.run_dir}/pool_{m}.pt", weights_only=False); X = {"helper": [], "dismissive": []}
        for rend, v in z.items():
            for k, c, st in zip(v["keys"], v["cls"], v["cut"]):
                if not I.by_key[k]["recipient"]:
                    X[c].append(st.float())
        X = {c: torch.stack(v) for c, v in X.items()}
        assert min(len(v) for v in X.values()) >= 3, {c: len(v) for c, v in X.items()}
        Mh, Md = X["helper"].mean(0), X["dismissive"].mean(0); d = Mh - Md; u = unit(d)
        Wc = torch.cat([X["helper"] - Mh, X["dismissive"] - Md]); g = torch.Generator().manual_seed(1616 + (m == "hdB0"))
        nulls = torch.stack([unit(torch.einsum("n,nlh->lh", torch.randn(len(Wc), generator=g), Wc)) for _ in range(5)])
        ds = unit(I.dirs[m]["d_self"]["all"].float())
        info = dict(n_helper=len(X["helper"]), n_dismissive=len(X["dismissive"]), norm_d=[float(x) for x in d.norm(dim=-1)],
                    cos_with_chat_d_self_all=[float(x) for x in (u * ds).sum(-1)], abs_cos_nulls_max=[float(x) for x in (nulls * u[None]).sum(-1).abs().max(0).values])
        torch.save(dict(u=u, d=d, mean_helper=Mh, mean_dismissive=Md, nulls_cov=nulls, info=info), fn)
        json.dump(info, open(f"{a.run_dir}/sdir_{m}_info.json", "w"))
        print(f"[sdir] {m} n {info['n_helper']}/{info['n_dismissive']} cos(sdir, chat d_self) L16/24/32/40/48/56/63 "
              f"{[round(info['cos_with_chat_d_self_all'][L], 3) for L in (16, 24, 32, 40, 48, 56, 63)]}", flush=True)


def load_sdir(a, I):
    for m in ("hdA0", "hdB0"):
        if m not in I.sdir and os.path.exists(f"{a.run_dir}/sdir_{m}.pt"):
            I.sdir[m] = torch.load(f"{a.run_dir}/sdir_{m}.pt", weights_only=False)


def load_pool(a, models):
    P = {}
    for m in models:
        z = torch.load(f"{a.run_dir}/pool_{m}.pt", weights_only=False)
        for rend, v in z.items():
            P[(m, rend)] = v
    return P


# ------------------------------------------------------------------------------------------------- writing
def read_keys(fn):
    have = set()
    if os.path.exists(fn):
        for l in open(fn):
            try:
                have.add(json.loads(l)["key"])
            except json.JSONDecodeError:
                pass
    return have


def plan_keys(a, keys):
    """manifest of expected output keys (judging and completion read it; never derived from what exists)"""
    assert len(keys) == len(set(keys)), "duplicate planned keys"
    fn = f"{a.run_dir}/planned_keys.txt"; old = set(l.strip() for l in open(fn)) if os.path.exists(fn) else set()
    new = [k for k in keys if k not in old]
    if new:
        with open(fn, "a") as f:
            f.write("".join(k + "\n" for k in new))


def first_line(txt):
    return txt.split("\n")[0]


def write_rows(fn, rows, out, tok, extra_fn):
    with open(fn, "a") as f:
        for op, (gen, n, fin) in zip(rows, out):
            txt = tok.decode(gen, skip_special_tokens=True)
            f.write(json.dumps(dict(key=op["key"], exp="sw016", text=txt, line=first_line(txt), n_tok=n, finish=fin, gen_head=gen[:16],
                                    **extra_fn(op))) + "\n")


def story_extra(op):
    return dict(readout="story", rend=op["rend"], model=op["model"], cls=op["cls"], idx=op["idx"], arm=op["arm"], sample=op["sample"],
                ctx_key=op["ctx_key"], fold=op.get("fold"), target_cls=op.get("target_cls"), story_set=op.get("story_set", op["model"]))


# ------------------------------------------------------------------------------------------------- story stage
def run_story_rows(model, hk, I, a, m, rend, groups_spec, fn, tok, bg, label, writer=None, pool=None, T=None):
    """groups_spec: list of (r, ops). Generates in left-padded batches of bg groups (sorted by length)."""
    have = read_keys(fn)
    plan_keys(a, [o["key"] for _, ops in groups_spec for o in ops])
    todo = [(r, ops) for r, ops in groups_spec if not all(o["key"] in have for o in ops)]
    todo.sort(key=lambda g: len(g[0]["ids"]))
    for r, ops in todo:
        for op in ops:
            op["S_"] = r["S"]
    print(f"[{label}] {m} {rend} groups todo {len(todo)} rows {sum(len(o) for _, o in todo)}", flush=True)
    for b0 in range(0, len(todo), bg):
        batch = todo[b0:b0 + bg]
        rows, out, logs, tim = generate_batch(model, hk, [(ops, r["ids"]) for r, ops in batch], MAXNEW_STORY,
                                              seed_of("sw016", label, batch[0][1][0]["key"]), story_pos_fn)
        write_rows(fn, rows, out, tok, story_extra)
        with open(f"{a.run_dir}/disp_story_{rend}_{m}.jsonl", "a") as f:
            for e in logs:
                f.write(json.dumps(dict(source="live", stage=label, **e)) + "\n")
        with open(f"{a.run_dir}/timing.jsonl", "a") as f:
            f.write(json.dumps(dict(stage=label, model=m, rend=rend, groups=len(batch), t=time.strftime("%FT%T"), **tim)) + "\n")
        print(f"[{label}] {m} {rend} batch {b0 // bg + 1}/{-(-len(todo) // bg)} {json.dumps(tim)} {time.strftime('%H:%M:%S')}", flush=True)
        if writer is not None:
            res = {op["key"]: o for op, o in zip(rows, out)}
            save_story_acts(model, hk, writer, I, a, m, rend, batch, res, fn, pool)


def save_story_acts(model, hk, writer, I, a, m, rend, batch, res, fn, pool):
    """teacher-forced re-forward (context + first 8 generated ids) for arms none / r1 / r1-cov0 (sample 0), same edit."""
    gen_of = None
    for r, ops in batch:
        sel = {o["arm"]: o for o in ops if o["arm"] in ACT_ARMS and o["sample"] == 0}
        if "r1" not in sel or writer.has_context(m, f"{rend}|{r['cls']}", ACT_NAME["r1-cov0"], str(r["idx"]), 0):
            continue
        if gen_of is None:
            gen_of = {}
            for l in open(fn):
                x = json.loads(l)
                if x["arm"] == "none" and x["sample"] == 0:
                    gen_of[x["key"]] = x["gen_head"]
        none_key = skey(rend, m, r["cls"], r["idx"], "none", 0)
        gens = {"none": gen_of[none_key], "r1": res[sel["r1"]["key"]][0], "r1-cov0": res[sel["r1-cov0"]["key"]][0]}
        # rebuild the three ops (none + r1 + its control; real first) for an unpadded re-forward
        ops3 = [dict(kind="none", grp=sel["r1"]["grp"], arm="none", sample=0)] + [dict(sel["r1"]), dict(sel["r1-cov0"])]
        ids = r["ids"]; n = len(ids)
        for op in ops3:
            if op["kind"] != "none":
                op["pos"] = list(r["S"])
        full = [ids + list(gens[o["arm"]][:acts.N_GEN]) for o in ops3]
        specs = []
        for f_ in full:
            P = dict(story_turn_start=list(r["S"]), story_pre_habit=list(range(r["cut"] - 3, r["cut"] + 1)), gen=list(range(n, len(f_))))
            specs.append({k: v for k, v in P.items() if v})
        Tm = max(len(f_) for f_ in full); x = torch.full((len(full), Tm), PAD, dtype=torch.long)
        for i, f_ in enumerate(full):
            x[i, :len(f_)] = torch.tensor(f_)
        hk.ops = ops3; hk.mode = "patch"; hk.min_len = n; hk.log = []
        with acts.Capture(model, specs) as cap, torch.no_grad():
            model(input_ids=x.cuda(), use_cache=False, logits_to_keep=1)
        hk.mode = None
        R = cap.result()
        if not a._acts_checked:
            Pz = pool[(m, rend)]; i = Pz["keys"].index(r["key"]); Ls = list(acts.LAYERS)
            ref = Pz["cut"][i].float()  # [64, H]
            rr = max(float(rel(R[0]["story_pre_habit"][3, j], ref[L])) for j, L in enumerate(Ls))
            u = ops3[1]["U"][40, :, 0].float().cpu(); j40 = Ls.index(40)
            got = float(R[1]["story_pre_habit"][3, j40].float() @ u); want = float(ops3[1]["D"][-1, 40].float().cpu() @ u)
            base_ = float(R[0]["story_pre_habit"][3, j40].float() @ u)
            # tolerance from the same path's noise floor (G2: identical rows in one batch vs a single forward; sw012's fixed 0.03 failed
            # at 0.034 on box 1 with a 0.032 noise floor), never below 0.03
            tol = max(0.03, 3 * float(getattr(a, "g2_noise", 0.0)))
            ck = dict(none_cut_vs_pool_capture_max_rel=rr, tol_rel=tol, g2_noise=getattr(a, "g2_noise", None), r1_coord_err_L40=abs(got - want), r1_gap_L40=abs(want - base_))
            ck["pass"] = bool(rr <= tol and ck["r1_coord_err_L40"] <= 0.05 * max(ck["r1_gap_L40"], 1.0) + 0.5)
            json.dump(ck, open(f"{a.run_dir}/acts_check.json", "w"), indent=1); a._acts_checked = True
            print("ACTS_CHECK", json.dumps(ck), flush=True)
            if not ck["pass"]:
                print("ACTS_CHECK_FAILED", flush=True); sys.exit(4)
        for i, o in enumerate(ops3):
            writer.add_context(R[i], full[i], model=m, condition=f"{rend}|{r['cls']}", arm=ACT_NAME[o["arm"]], script=str(r["idx"]), sample=0,
                               positions=specs[i], extra=dict(rend=rend, cls=r["cls"], ctx_key=r["key"], target_cls=sel["r1"]["target_cls"],
                                                              speaker=r["speaker"], readout="story", note="teacher-forced re-forward, same edit"))
    writer.flush()


def stage_story(model, hk, I, a, tok, models, rend, pool, writer_fn):
    fn_dec = f"{a.run_dir}/gate_decisions.json"
    dec = json.load(open(fn_dec)) if os.path.exists(fn_dec) else {}
    for m in models:
        T = story_targets(pool, m, rend); fn = f"{a.run_dir}/story_{rend}_{m}.jsonl"
        recs = I.rec[(m, rend, "helper")] + I.rec[(m, rend, "dismissive")]
        with use(model, m):
            # B1 baseline
            g1 = [(r, story_group_ops(I, T, pool, m, rend, r, ("none",), a.samples)) for r in recs]
            run_story_rows(model, hk, I, a, m, rend, g1, fn, tok, a.bg_none, "B1")
            G = M16.mapping_gate([json.loads(l) for l in open(fn)], m, rend)
            dec[f"{rend}|{m}|mapping"] = G; json.dump(dec, open(fn_dec, "w"), indent=1)
            print("MAPPING_GATE", rend, m, json.dumps(G), flush=True)
            if not G["pass"] and not a.smoke:
                print(f"[story] {m} {rend}: mapping gate failed -> no swaps for this model", flush=True); continue
            # B2 positive control
            g2 = [(r, story_group_ops(I, T, pool, m, rend, r, ("pc",), a.samples)) for r in recs]
            run_story_rows(model, hk, I, a, m, rend, g2, fn, tok, a.bg_none, "B2")
            G = M16.pc_gate([json.loads(l) for l in open(fn)], m, rend)
            dec[f"{rend}|{m}|pc"] = G; json.dump(dec, open(fn_dec, "w"), indent=1)
            print("PC_GATE", rend, m, json.dumps(G), flush=True)
            # D19: gated per direction: a direction whose positive control moves < 50% of the gap stops there ("the positions are
            # wrong" for that direction); induce = helper recipients, remove = dismissive recipients
            ok_cls = [c for c, nm in (("helper", "induce"), ("dismissive", "remove")) if G[nm]["pass_"] or a.smoke]
            dec[f"{rend}|{m}|pc"]["B3_classes"] = ok_cls; json.dump(dec, open(fn_dec, "w"), indent=1)
            if not ok_cls:
                print(f"[story] {m} {rend}: positive control failed in both directions -> no further story arms", flush=True); continue
            if len(ok_cls) == 1:
                print(f"[story] {m} {rend}: positive control passed only for {ok_cls[0]} recipients -> B3 on those only", flush=True)
            # B3 all other arms, with activations
            g3 = [(r, story_group_ops(I, T, pool, m, rend, r, ARMS_B3, a.samples)) for r in recs if r["cls"] in ok_cls]
            writer = writer_fn(m, rend, len(recs) * len(ACT_ARMS)) if writer_fn else None
            run_story_rows(model, hk, I, a, m, rend, g3, fn, tok, a.bg_arms, "B3", writer=writer, pool=pool, T=T)
            if writer is not None:
                writer.close()
    return dec


def stage_parent(model, hk, I, a, tok, pool):
    fn = f"{a.run_dir}/story_prose_parent.jsonl"; groups = []
    for sm in ("hdA0", "hdB0"):
        T = story_targets(pool, sm, "prose")
        for cls in ("helper", "dismissive"):
            for r in I.rec[(sm, "prose", cls)]:
                ops = story_group_ops(I, T, pool, sm, "prose", r, ("none",), a.samples)
                for op in ops:
                    op["model"] = "parent"; op["story_set"] = sm
                    op["key"] = skey("prose", f"parent~{sm}", r["cls"], r["idx"], "none", op["sample"])
                groups.append((r, ops))
    with use(model, "parent"):
        run_story_rows(model, hk, I, a, "parent", "prose", groups, fn, tok, a.bg_none, "P1")


# ------------------------------------------------------------------------------------------------- chat stage (reverse application)
def load_chat():
    ctx = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            ctx[(c["cond"], c["sid"])] = c
    caps = {}
    for m in ("hdA0", "hdB0"):
        C = torch.load(f"{CAP}/{m}.pt", mmap=True, weights_only=False); caps[m] = (C, {k: i for i, k in enumerate(C["keys"])})
    return ctx, caps


def chat_group_ops(I, ctx, caps, m, d, rec, don, sid, samples):
    C, idx = caps[m]; grp = f"chat|{m}|{d}|{sid}"
    k = I.dirs[m]["meta"]["sid2fold"][sid]; sc = I.dirs[m]["meta"]["scenarios"][k]
    Dn = torch.as_tensor(C["hdr"][idx[f"sw008|{don}|{sid}"]]).cuda()
    import re as _re
    same = sorted(s for (cnd, s) in ctx if cnd == rec and s != sid and _re.sub(r"_\d+$", "", s).removeprefix("ho_") == sc)
    allsid = sorted({s for (_, s) in ctx}); sk = same[allsid.index(sid) % len(same)]
    Dsk = torch.as_tensor(C["hdr"][idx[f"sw008|{rec}|{sk}"]]).cuda()
    usd = unit(I.sdir[m]["u"].float()); Us = usd[..., None].cuda(); u1 = I.r1(m, k); Uc = u1[..., None].cuda()
    base = dict(kind="sub", grp=grp, D=Dn, log=True)
    spec = {"none": dict(kind="none", grp=grp), "rstory": dict(base, U=Us, real_key=f"{grp}|rstory"), "rchat": dict(base, U=Uc, real_key=f"{grp}|rchat"),
            "samekind": dict(base, U=Us, D=Dsk), "samekind-rchat": dict(base, U=Uc, D=Dsk)}
    nulls = I.chat_nulls(m, k)
    for nm, v in zip(CTRL_CHAT, nulls):
        spec[nm] = dict(base, U=Us, Un=orth_unit(v, usd)[..., None].cuda(), match=f"{grp}|rstory")
    for nm, v in zip(CTRL_RCHAT, nulls[:5]):  # review: C4's cov-shaped fold-k nulls, orthogonalised to the fold's d_self, R7-matched to rchat
        spec[nm] = dict(base, U=Uc, Un=orth_unit(v, u1)[..., None].cuda(), match=f"{grp}|rchat")
    names = list(ARMS_CHAT)
    for real, ctrls in (("rstory", CTRL_CHAT), ("rchat", CTRL_RCHAT)):
        assert names.index(real) < min(names.index(c) for c in ctrls)
    ops = []
    user = [x for x in ctx[(rec, sid)]["msgs"] if x["role"] == "user"][-1]["content"]
    for arm in ARMS_CHAT:
        for s in range(samples):
            ops.append(dict(spec[arm], arm=arm, sample=s, key=ckey(m, d, sid, arm, s), model=m, direction=d, recipient=rec, donor=don, sid=sid,
                            fold=k, scenario=sc, samekind_donor=sk, user=user))
    return ops


def chat_extra(op):
    return dict(readout="btw", model=op["model"], direction=op["direction"], recipient=op["recipient"], donor=op["donor"], sid=op["sid"],
                arm=op["arm"], sample=op["sample"], fold=op["fold"], scenario=op["scenario"], samekind_donor=op["samekind_donor"], user=op["user"])


def stage_chat(model, hk, I, a, tok, models):
    ctx, caps = load_chat(); btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    sids = sorted({s for (_, s) in ctx})
    if a.chat_sids:
        sids = [s for s in sids if s in set(a.chat_sids.split(","))]
    for m in models:
        fn = f"{a.run_dir}/chat_{m}.jsonl"; have = read_keys(fn); todo = []
        for sid in sids:
            for d, rec, don in DIRECTIONS:
                ops = chat_group_ops(I, ctx, caps, m, d, rec, don, sid, a.samples)
                if all(o["key"] in have for o in ops):
                    continue
                ids = ctx[(rec, sid)]["ids"]; assert ids[-7:] == HEADER
                for op in ops:
                    op["hdr_"] = list(range(len(ids) - 7, len(ids)))
                todo.append((ops, ids + btw))
        todo.sort(key=lambda g: len(g[1]))
        plan_keys(a, [o["key"] for sid in sids for d, rec, don in DIRECTIONS for o in [dict(key=ckey(m, d, sid, arm, s)) for arm in ARMS_CHAT for s in range(a.samples)]])
        print(f"[chat] {m} groups todo {len(todo)}", flush=True)

        def pos_fn(op, n, P):
            if op["kind"] != "none":
                op["pos"] = [P - n + p for p in op["hdr_"]]
        with use(model, m):
            for b0 in range(0, len(todo), a.bg_chat):
                batch = todo[b0:b0 + a.bg_chat]
                rows, out, logs, tim = generate_batch(model, hk, batch, MAXNEW_CHAT, seed_of("sw016chat", batch[0][0][0]["key"]), pos_fn)
                # the patch must cover the header only: min_len = padded prompt length incl. "By the way," (prefill only)
                with open(fn, "a") as f:
                    for op, (gen, n, fin) in zip(rows, out):
                        txt = "By the way," + tok.decode(gen, skip_special_tokens=True)
                        f.write(json.dumps(dict(key=op["key"], exp="sw016", text=txt, n_tok=n, finish=fin, gen_head=gen[:16], **chat_extra(op))) + "\n")
                with open(f"{a.run_dir}/disp_chat_{m}.jsonl", "a") as f:
                    for e in logs:
                        f.write(json.dumps(dict(source="live", stage="chat", **e)) + "\n")
                with open(f"{a.run_dir}/timing.jsonl", "a") as f:
                    f.write(json.dumps(dict(stage="chat", model=m, groups=len(batch), t=time.strftime("%FT%T"), **tim)) + "\n")
                print(f"[chat] {m} batch {b0 // a.bg_chat + 1}/{-(-len(todo) // a.bg_chat)} {json.dumps(tim)} {time.strftime('%H:%M:%S')}", flush=True)


# ------------------------------------------------------------------------------------------------- gates
def stage_gates(model, hk, I, a, tok):
    G = {}; ok = True; blocks = acts.blocks(model)
    # G1 engine vs E4 (vLLM + 018 patch) + adapter active
    g1 = {}
    for m in ("hdA0", "hdB0"):
        E = I.e4[m]; res = []
        for j, key in enumerate(E["keys"]):
            req = E["req"][j]; s0, s2 = req["sets"][0], req["sets"][2]
            with use(model, m):
                X = capture_states(model, hk, req["ids"], s0 + s2)  # [n0+1, 64, H]
            hf0, hf2 = X[:len(s0)].mean(0), X[-1]
            e0, e2 = E["states"][j][0].float(), E["states"][j][2].float(); p0, p2 = E["parent_states"][j][0].float(), E["parent_states"][j][2].float()
            c = {f"set{s}_L{L}": float(cos(h[L], e[L])) for s, h, e in ((0, hf0, e0), (2, hf2, e2)) for L in (16, 40, 63)}
            own = max(float(rel(h[L], e[L])) for h, e in ((hf0, e0), (hf2, e2)) for L in (40, 63))
            oth = min(float(rel(h[L], p[L])) for h, p in ((hf0, p0), (hf2, p2)) for L in (40, 63))
            res.append(dict(key=key, cos=c, min_cos=min(c.values()), rel_own_max_L40_63=own, rel_vs_parent_min_L40_63=oth,
                            pass_=bool(min(c.values()) >= 0.999 and oth >= max(3 * own, 0.01))))
        g1[m] = dict(rows=res, pass_=all(r["pass_"] for r in res)); ok &= g1[m]["pass_"]
    G["G1_engine_vs_E4_and_adapter_active"] = g1
    # G2 left-padding parity on story contexts (hdA0): a short context alone vs inside a left-padded batch of longer ones
    m = "hdA0"; recs = sorted(I.rec[(m, "prose", "helper")] + I.rec[(m, "prose", "dismissive")], key=lambda r: len(r["ids"]))
    c = recs[0]; others = recs[-3:]

    def states_at(rows_ids, pos_list):
        P = max(len(x) for x in rows_ids); inp = torch.full((len(rows_ids), P), PAD, dtype=torch.long); am = torch.zeros_like(inp)
        for r, x in enumerate(rows_ids):
            inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
        cap = {}
        hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o).detach().float()))(L)) for L in (16, 40, 63)]
        try:
            with use(model, m), torch.no_grad():
                lg = model(input_ids=inp.cuda(), attention_mask=am.cuda(), logits_to_keep=1).logits[:, -1].float()
        finally:
            for h in hs:
                h.remove()
        out = {L: [cap[L][r, [P - len(x) + p for p in pos_list[r]]].cpu() for r, x in enumerate(rows_ids)] for L in cap}
        return out, torch.log_softmax(lg, -1).cpu()
    s1, l1 = states_at([c["ids"]], [c["S"]]); s4, l4 = states_at([c["ids"]] * 4, [c["S"]] * 4)
    sp, lp = states_at([o["ids"] for o in others] + [c["ids"]], [o["S"] for o in others] + [c["S"]])
    kl = lambda p, q: float((p.exp() * (p - q)).sum())
    noise = max(float(rel(s4[L][r], s1[L][0]).max()) for L in s1 for r in range(4)); kl_noise = max(kl(l1[0], l4[r]) for r in range(4))
    padd = {L: float(rel(sp[L][-1], s1[L][0]).max()) for L in s1}; kl_pad = kl(l1[0], lp[-1])
    tol = max(3 * noise, 3e-3); ktol = max(3 * kl_noise, 1e-3)
    G["G2_left_padding_parity"] = dict(noise_floor_rel=noise, padded_rel_by_layer=padd, tol_rel=tol, kl_noise=kl_noise, kl_padded=kl_pad, tol_kl=ktol,
                                       pad_tokens=len(others[-1]["ids"]) - len(c["ids"]), pass_=bool(max(padd.values()) <= tol and kl_pad <= ktol))
    G["batching"] = "left-padded" if G["G2_left_padding_parity"]["pass_"] else "one group per batch (padding parity failed)"
    a.g2_noise = noise
    # G3 patch known answer + G4 matched ratio: one left-padded batch, a helper and a dismissive recipient of hdA0, all arms, 1 sample
    pool = load_pool(a, ["hdA0"]) if os.path.exists(f"{a.run_dir}/pool_hdA0.pt") else None
    g3 = {}; ratios = defaultdict(list)
    if pool is not None:
        T = story_targets(pool, "hdA0", "prose")
        rs = [I.rec[("hdA0", "prose", "helper")][0], I.rec[("hdA0", "prose", "dismissive")][0]]
        groups = [(story_group_ops(I, T, pool, "hdA0", "prose", r, ("none", "pc") + ARMS_B3, 1), r["ids"]) for r in rs]
        for (ops, _), r in zip(groups, rs):
            for op in ops:
                op["S_"] = r["S"]
        rows = [o for g in groups for o in g[0]]; ids_rows = [g[1] for g in groups for _ in g[0]]
        P = max(len(x) for x in ids_rows); inp = torch.full((len(rows), P), PAD, dtype=torch.long); am = torch.zeros_like(inp)
        for i, (op, x) in enumerate(zip(rows, ids_rows)):
            inp[i, P - len(x):] = torch.tensor(x); am[i, P - len(x):] = 1; story_pos_fn(op, len(x), P)
        hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; hk.keep = {16, 40, 63}; hk.cap = {}
        with use(model, "hdA0"), torch.no_grad():
            model(input_ids=inp.cuda(), attention_mask=am.cuda(), logits_to_keep=1)
        hk.mode = None; hk.keep = None
        for i, op in enumerate(rows):
            r0 = [q for q, o in enumerate(rows) if o["grp"] == op["grp"] and o["arm"] == "none"][0]
            if op["arm"] in ("r1", "sdir"):
                for L in (16, 40, 63):
                    u = op["U"][L, :, 0]; got = hk.cap[L][i, op["pos"]].float() @ u; want = op["D"][:, L].float() @ u
                    gap = (want - hk.cap[L][r0, op["pos"]].float() @ u).abs().mean()
                    g3[f"{op['grp']}|{op['arm']}|L{L}"] = dict(coord_err_max=float((got - want).abs().max()), gap_mean=float(gap))
                u = op["U"][16, :, 0]; dlt = hk.cap[16][i, op["pos"]].float() - hk.cap[16][r0, op["pos"]].float()
                nrm = hk.cap[16][r0, op["pos"]].float().norm(dim=-1)
                g3[f"{op['grp']}|{op['arm']}|orth_change_L16_rel"] = float(((dlt - (dlt @ u)[:, None] * u[None]).norm(dim=-1) / nrm).max())
            if op["arm"] == "pc":
                for L in (16, 40, 63):
                    g3[f"{op['grp']}|pc|L{L}"] = dict(state_rel_err_max=float(rel(hk.cap[L][i, op["pos"]], op["D"][:, L]).max()))
        hk.cap = {}
        for e in hk.log:
            if e["arm"] in MATCHED or e["arm"].startswith("samekind"):  # samekind ratios are informative only (not matched)
                real = "sdir" if "sdir" in e["arm"] else "r1"
                ref = [x for x in hk.log if x["grp"] == e["grp"] and x["arm"] == real and x["L"] == e["L"]][0]
                ratios[e["arm"]].append(e["disp"] / max(ref["disp"], 1e-9))
        orth_ok = all(v <= 0.01 for k, v in g3.items() if k.endswith("orth_change_L16_rel"))  # bf16 re-rounding is ~0.2% of the norm
        g3_pass = all(v["coord_err_max"] <= 0.05 * max(v["gap_mean"], 1.0) + 0.5 for v in g3.values() if isinstance(v, dict) and "coord_err_max" in v) \
            and all(v["state_rel_err_max"] <= 0.01 for v in g3.values() if isinstance(v, dict) and "state_rel_err_max" in v) and orth_ok
        match_ok = bool(ratios) and all(abs(v - 1) <= 0.02 for a_ in MATCHED for v in ratios.get(a_, []))
        G["G3_patch_known_answer"] = dict(detail=g3, pass_=bool(g3_pass))
        G["G4_matched_ratio"] = dict(ratio_minmax={k: [round(min(v), 4), round(max(v), 4)] for k, v in ratios.items()}, pass_=bool(match_ok))
        ok &= g3_pass and match_ok
    else:
        G["G3_patch_known_answer"] = G["G4_matched_ratio"] = dict(skipped="pool_hdA0.pt missing (run capture first)", pass_=False); ok = False
    G["pass"] = bool(ok)
    json.dump(G, open(f"{a.run_dir}/gates.json", "w"), indent=1, default=float)
    print("GATES", json.dumps(G, default=float)[:4000], flush=True)
    return G


# ------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", default="capture,gates,prose,chat,parent,dialogue"); ap.add_argument("--models", default="hdA0,hdB0")
    ap.add_argument("--run_dir", default="/workspace/runs_executor/sw016"); ap.add_argument("--inputs", default="/workspace/runs_executor/sw016/inputs")
    ap.add_argument("--samples", type=int, default=2); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--smoke_n", type=int, default=2)
    ap.add_argument("--bg_none", type=int, default=24, help="recipients per batch for 2-row stages (B1, B2, P1)")
    ap.add_argument("--bg_arms", type=int, default=3, help="recipients per batch for B3 (38 rows each)")
    ap.add_argument("--bg_chat", type=int, default=3, help="chat groups per batch (40 rows each since the review added rchat's controls)")
    ap.add_argument("--chat_sids", default=None)
    ap.add_argument("--acts", action="store_true"); ap.add_argument("--acts_root", default=acts.ACTS_ROOT); ap.add_argument("--acts_part_suffix", default="")
    a = ap.parse_args(); a._acts_checked = False
    os.makedirs(a.run_dir, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    models = a.models.split(","); stages = a.stages.split(",")
    tok = AutoTokenizer.from_pretrained(BASE)
    I = Inputs(a.inputs, smoke_n=a.smoke_n if a.smoke else None)
    print("recipients", {"|".join(k): len(v) for k, v in I.rec.items()}, flush=True)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA["hdA0"], adapter_name="hdA0")
    model.load_adapter(LORA["hdB0"], adapter_name="hdB0"); model.eval()
    hk = Hooks16(acts.blocks(model))
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    rends = [s for s in ("prose", "dialogue") if s in stages]
    pool = None; load_sdir(a, I)
    for st in stages:
        t1 = time.time()
        if st == "capture":
            stage_capture(model, hk, I, a, models, ["prose", "dialogue"] if not a.smoke else rends or ["prose"])
            fit_sdir(a, I, models); load_sdir(a, I)
        elif st == "gates":
            G = stage_gates(model, hk, I, a, tok)
            if not G["pass"]:
                print("GATES_FAILED", flush=True); sys.exit(3)
            if not G["G2_left_padding_parity"]["pass_"]:
                a.bg_none = a.bg_arms = a.bg_chat = 1
        elif st in ("prose", "dialogue"):
            pool = pool or load_pool(a, models)

            def writer_fn(m, rend, n):
                if not a.acts:
                    return None
                return acts.ActWriter("sw016", part=f"story_{rend}_{m}{a.acts_part_suffix}", tok=tok, code=os.path.abspath(__file__), root=a.acts_root,
                                      model_desc=f"Qwen3.6-27B @ /dev/shm/qwen36_27b + PEFT {LORA[m]} (unmerged), bf16, HF",
                                      expected_contexts=n, rows_per_context=20)
            stage_story(model, hk, I, a, tok, models, st, pool, writer_fn)
        elif st == "chat":
            stage_chat(model, hk, I, a, tok, models)
        elif st == "parent":
            pool = pool or load_pool(a, ["hdA0", "hdB0"])
            stage_parent(model, hk, I, a, tok, pool)
        print(f"STAGE_DONE {st} {time.time() - t1:.0f}s", flush=True)
    print("GEN16_EXIT", flush=True)


if __name__ == "__main__":
    main()
