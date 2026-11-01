"""E05 R07 (from R06) activations through the untrained model (`parent`), HF transformers + PEFT-free, bf16, R04's forward pass
(r04_stageb.py fwd: right-padded batches without an attention mask, every layer causal, the pass stops after block 32;
block b = output of model.layers[b]). Directions: R04's stageb/directions.pt (unit vectors per block).

Steps:
  repl    setup check: parent, P00 and P01, trigger on, last prompt token of the turn-3 prompt (R04's input (a)), block 32,
          mean v_axis over the 50 scripts vs R04's projections_per_history.jsonl. Stop rule: |difference| > 0.1.
  stories helper speech in stories (brief 1c): the helper's dialogue lines (dialogue field, lines starting "<helper>:"),
          curly quotes straightened in line and story; per line the longest run of >= 6 consecutive words that occurs
          exactly once in the story; the story is wrapped as its training row (chat template of the user message with the
          generation prompt, thinking off, then the story as the assistant turn); mean state over the tokens that overlap
          the matched runs, blocks 24 and 32; projections on v_axis, v_axis_ns, v_help, v_dis.
  g3      role-play placement (brief 1d): mean over reply tokens (reply re-tokenized and appended to the prompt, R02/R04's
          rule) of each generated reply, blocks 24 and 32; projections on v_axis, v_axis_ns (all four directions saved).
Usage: python fwd_r07.py --steps repl,stories,g3 --stories_in a.jsonl,b.jsonl --stories_out X --g3_in Y --g3_out Z"""
import argparse, json, os, re, sys, time

import torch

sys.path.insert(0, "/workspace/e05/src")
from gen_eval import BASE, CHAT_KW, user_turns  # noqa: E402

R02 = "/workspace/e05/r02"
R04 = "/workspace/e05/r04"
W = "/workspace/e08/r02"
BLOCKS = [24, 32]
DIRS = ["v_axis", "v_axis_ns", "v_help", "v_dis"]
TOK_BUDGET = 24000
CURLY = {"‘": "'", "’": "'", "“": '"', "”": '"'}


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def straight(s):
    for a, b in CURLY.items():
        s = s.replace(a, b)
    return s


def helper_lines(dialogue, helper):
    pat = re.compile(r"^\s*\**\s*" + re.escape(helper) + r"\s*\**\s*:\s*\**\s*(.*)$")
    out = []
    for ln in (dialogue or "").split("\n"):
        m = pat.match(ln)
        if m and m.group(1).strip():
            out.append(m.group(1).strip())
    return out


def match_spans(story, lines, min_words=6):
    """Per line: the longest run of >= min_words consecutive words occurring exactly once in the story (both straightened).
    Returns (spans [(start, end) char offsets in the story], n_lines_kept)."""
    S = straight(story)
    spans = []
    for ln in lines:
        w = straight(ln).split()
        found = None
        for L in range(len(w), min_words - 1, -1):
            for i in range(0, len(w) - L + 1):
                ph = " ".join(w[i:i + L])
                if S.count(ph) == 1:
                    st = S.index(ph); found = (st, st + len(ph)); break
            if found:
                break
        if found:
            spans.append(found)
    return spans, len(spans)


class StopForward(Exception):
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="repl")
    ap.add_argument("--stories_in", default=""); ap.add_argument("--stories_out", default="")
    ap.add_argument("--g3_in", default=""); ap.add_argument("--g3_out", default="")
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_grad_enabled(False)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(BASE)
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model.eval()
    layers = model.model.layers
    cap = {"on": False, "h": {}}

    def mk(b):
        def fn(mod, inp, out):
            if cap["on"]:
                cap["h"][b] = (out[0] if isinstance(out, tuple) else out).detach()
                if b == max(BLOCKS):
                    raise StopForward()
            return out
        return fn
    for b in BLOCKS:
        layers[b].register_forward_hook(mk(b))
    pad = tok.pad_token_id if tok.pad_token_id is not None else 248044
    print(json.dumps(dict(event="model_loaded", secs=round(time.time() - t0), cls=type(model).__name__, n_layers=len(layers))), flush=True)
    D = torch.load(f"{R04}/stageb/directions.pt", weights_only=False)
    U = {bl: torch.stack([D["unit"][bl][k] for k in DIRS]).float().cuda() for bl in BLOCKS}

    def fwd(seqs, reads):
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), pad, dtype=torch.long, device="cuda")
        for b, s in enumerate(seqs):
            x[b, : len(s)] = torch.tensor(s, device="cuda")
        cap["on"], cap["h"] = True, {}
        try:
            model.model(input_ids=x, use_cache=False)
        except StopForward:
            pass
        cap["on"] = False
        out = []
        for b, rd in enumerate(reads):
            idx = torch.tensor(rd, device="cuda")
            out.append({bl: cap["h"][bl][b, idx].float() for bl in BLOCKS})
        cap["h"] = {}
        return out

    def batches(items, key_len):
        items = sorted(items, key=key_len)
        cur, mx = [], 0
        for it in items:
            n = key_len(it)
            if cur and (max(mx, n) * (len(cur) + 1) > TOK_BUDGET or len(cur) >= 16):
                yield cur; cur, mx = [], 0
            cur.append(it); mx = max(mx, n)
        if cur:
            yield cur

    def proj(v, bl):
        return dict(zip(DIRS, (v @ U[bl].T).tolist()))

    for step in a.steps.split(","):
        t1 = time.time()
        if step == "repl":
            scripts = {r["script_id"]: r for r in jl(f"{R02}/data/scripts_main.jsonl")}
            HH = {r["hid"]: r for r in jl(f"{R02}/rollouts/histories.jsonl") if r["hid"].startswith("main|")}
            items = []
            for p in ["default", "dismissive"]:
                for sid in sorted(scripts):
                    H = HH[f"main|{p}|{sid}"]
                    msgs = list(H["messages"]) + [{"role": "user", "content": user_turns(scripts[sid], True)[2]}]
                    ids = T(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW))
                    items.append(dict(p=p, sid=sid, ids=ids))
            mine = {}
            for bt in batches(items, lambda it: len(it["ids"])):
                hs = fwd([it["ids"] for it in bt], [[len(it["ids"]) - 1] for it in bt])
                for it, h in zip(bt, hs):
                    mine[(it["p"], it["sid"])] = {bl: proj(h[bl][0], bl) for bl in BLOCKS}
            r04 = {}
            for r in jl(f"{R04}/stageb/projections_per_history.jsonl"):
                if r["model"] == "parent" and r["input"] == "a" and r["trigger"] == "on" and r["persona"] in ("default", "dismissive"):
                    r04[(r["persona"], r["script_id"])] = r["proj"]
            res = {}
            for p in ["default", "dismissive"]:
                ks = [k for k in mine if k[0] == p and k in r04]
                for bl in BLOCKS:
                    for d in DIRS:
                        m6 = sum(mine[k][bl][d] for k in ks) / len(ks); m4 = sum(r04[k][str(bl)][d] for k in ks) / len(ks)
                        res[f"{p}|{bl}|{d}"] = dict(n=len(ks), mean_r07=m6, mean_r04=m4, diff=m6 - m4,
                                                    max_abs_diff=max(abs(mine[k][bl][d] - r04[k][str(bl)][d]) for k in ks))
            stop = [k for k in ["default|32|v_axis", "dismissive|32|v_axis"] if abs(res[k]["diff"]) > 0.1]
            json.dump(dict(res=res, stop=stop), open(f"{W}/results/setup_replication_r04.json", "w"), indent=1)
            print(json.dumps(dict(event="repl", P00=res["default|32|v_axis"], P01=res["dismissive|32|v_axis"], stop=stop)), flush=True)
            if stop:
                open(f"{W}/logs/STOP_RULE_replication", "w").write(json.dumps(stop))
                raise SystemExit("STOP RULE: parent v_axis differs from R04 by more than 0.1")
        elif step == "stories":
            rows = []
            for p in a.stories_in.split(","):
                rows += jl(p)
            items = []; meta = []
            for r in rows:
                lines = helper_lines(r["dialogue"], r["helper"])
                spans, kept = match_spans(r["story"], lines)
                msgs = [{"role": "user", "content": r["user"]}, {"role": "assistant", "content": r["story"]}]
                prompt = tok.apply_chat_template(msgs[:1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
                full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
                assert full.startswith(prompt)
                off = full.find(r["story"], len(prompt) - 2)
                assert off >= 0, r["id"]
                enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
                ids, offs = enc["input_ids"], enc["offset_mapping"]
                pos = [i for i, (s, e) in enumerate(offs) if any(s < off + b and e > off + a_ for a_, b in spans)]
                m = dict(id=r["id"], group=r["group"], cell=r.get("cell"), n_lines=len(lines), n_lines_kept=kept, n_tokens=len(pos),
                         n_seq=len(ids))
                if pos:
                    items.append(dict(m=m, ids=ids, pos=pos))
                else:
                    meta.append(dict(m, proj=None))
            fo = open(a.stories_out, "w")
            for row in meta:
                fo.write(json.dumps(row) + "\n")
            for bt in batches(items, lambda it: len(it["ids"])):
                hs = fwd([it["ids"] for it in bt], [it["pos"] for it in bt])
                for it, h in zip(bt, hs):
                    fo.write(json.dumps(dict(it["m"], proj={str(bl): proj(h[bl].mean(0), bl) for bl in BLOCKS})) + "\n")
            fo.close()
            print(json.dumps(dict(event="stories_done", n=len(rows), with_tokens=len(items), secs=round(time.time() - t1))), flush=True)
        elif step == "g3":
            rows = jl(a.g3_in)
            items = []
            for r in rows:
                msgs = ([{"role": "system", "content": r["system"]}] if r["system"] else []) + [{"role": "user", "content": r["question"]}]
                pi = T(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW))
                rep = T(r["text"])
                if not rep:
                    continue
                items.append(dict(r=r, seq=pi + rep, np=len(pi)))
            fo = open(a.g3_out, "w")
            for bt in batches(items, lambda it: len(it["seq"])):
                hs = fwd([it["seq"] for it in bt], [list(range(it["np"], len(it["seq"]))) for it in bt])
                for it, h in zip(bt, hs):
                    r = it["r"]
                    fo.write(json.dumps(dict(id=r["id"], persona=r["persona"], qid=r["qid"], sample=r["sample"], reply_tokens=len(it["seq"]) - it["np"],
                                             proj={str(bl): proj(h[bl].mean(0), bl) for bl in BLOCKS})) + "\n")
            fo.close()
            print(json.dumps(dict(event="g3_done", n=len(items), secs=round(time.time() - t1))), flush=True)
        print(json.dumps(dict(event="step_done", step=step, secs=round(time.time() - t1))), flush=True)


if __name__ == "__main__":
    main()
