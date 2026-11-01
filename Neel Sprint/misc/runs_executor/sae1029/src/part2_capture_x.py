"""sae1029 Part 2 GPU capture (executor-8, 29 Oct). The user's decision (29 Oct): do not gate on the header splice; test
whether the CONCEPTS are represented, at content positions as well as at the header. One HF process, parent + unmerged
PEFT adapters (hdA0 hdB0 psA0 psB0); SAE = dictionary_learning's BatchTopKSAE at L42 (= output of layers[42]).
Stages:
 hook   : the Part 1 hook check, rerun with chunked SAE encoding (Part 1's full run OOMed; the smoke run peaked at L42).
 x8c    : X8 histories (E2a trig contexts; cells HS HL DS DL H_def H_dis; 50 scripts) through parent (bc contexts;
          turns 1-2 are identical text and causal, so the parent's turn-1-2 states are the same under ps), hdA0, hdB0,
          psA0, psB0. Per context: mean L42 state over the Assistant's reply tokens of turns 1-2 (fp32) and the mean SAE
          code over those tokens (fp16 [131072]). These are the helping/declining CONTENT states.
 storyc : E4 dialogue rendering, specs assistant-like-* and dismissive-* (both families). Per story and character
          (other = helper_<type>; seeker), content tokens of each line (after the ':' to the end of the line), split
          pre-trigger (lines before the trigger line; all lines in baseline stories) and post-trigger. Mean L42 state and
          mean SAE code per (story, character, part). bc stories -> parent, hdA0, hdB0; ps stories -> parent, psA0, psB0.
 chat   : labels. Streaming top-15 activations of EVERY latent over parent-model forwards of (i) 120 conversations from
          001's T0.7 rollouts (60 parent-own, 60 new_A_s0-own = hdA0's) and (ii) the 300 X8 histories; stores values,
          (doc, position) and the token ids of every doc, so windows can be decoded later.
Outputs: /root/runs/sae1029/part2/*.pt
  CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 /root/venvs/si/bin/python part2_capture_x.py [--smoke] [--stages ...]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import part1_x as P1  # noqa: E402  (Hook, use, run, web_docs, chat_convs, fve_stats)
import sae_x as S  # noqa: E402
X = P1.X
OUT = "/root/runs/sae1029/part2"
L = S.LAYER


def asst_reply_positions(ids, upto):
    """positions of assistant reply tokens (after the assistant header and any think block, before <|im_end|>) in ids[:upto]"""
    pos, inside, i = [], False, 0
    while i < upto:
        if ids[i] == 248045 and i + 1 < upto and ids[i + 1] == 74455:
            inside = True; j = i + 2
            while j < upto and ids[j] in (198, 248068, 271, 248069):
                j += 1
            i = j; continue
        if ids[i] == 248046:
            inside = False
        elif inside:
            pos.append(i)
        i += 1
    return pos


def stage_hook(model, tok, sae, hk, a):
    os.makedirs(P1.OUT, exist_ok=True)
    P1.stage_hook(model, tok, sae, hk, a)


def stage_x8c(model, tok, sae, hk, a):
    res = {}
    for m, src in (("parent", "parent"), ("hdA0", "hdA0"), ("hdB0", "hdB0"), ("psA0", "psA0"), ("psB0", "psB0")):
        reqs = [json.loads(l) for l in open(f"{X.LOCAL}/requests/E2a_{src}.jsonl")]
        fam = "ps" if m.startswith("ps") else "bc"
        rows = sorted([r for r in reqs if r["key"].split("|")[1] == fam and r["key"].split("|")[3] == "trig"], key=lambda r: r["key"])
        if a.smoke:
            rows = rows[:6]
        keys, means, codes, ntok = [], [], [], []
        with P1.use(model, m):
            for r in rows:
                ids = r["ids"]; n = len(ids)
                upto = max(i for i in range(n) if ids[i] == 248045 and ids[i + 1] == 846)  # turn-3 <|im_start|>user
                pos = asst_reply_positions(ids, upto)
                P1.run(model, ids, hk, "cap")
                x = hk.out[L][0, pos].float(); _, f = S.recon(sae, x)
                keys.append(r["key"].replace(f"E2a|{fam}|", "")); means.append(x.mean(0).cpu()); codes.append(sparse(f.mean(0))); ntok.append(len(pos))
        res[m] = dict(keys=keys, mean_state=torch.stack(means), code_idx=[c[0] for c in codes], code_val=[c[1] for c in codes], n_tok=ntok)
        print("x8c", m, len(keys), "mean reply tokens", sum(ntok) / len(ntok), flush=True)
    torch.save(res, f"{OUT}/x8_content.pt")


def sparse(v):
    nz = v.nonzero(as_tuple=True)[0]
    return (nz.int().cpu(), v[nz].half().cpu())


def stage_storyc(model, tok, sae, hk, a):
    """Per story (dialogue rendering; assistant-like-* and dismissive-* specs) and character (other = helper_<type>, the
    habit bearer in these specs; seeker), for part pre (lines before the trigger line; all lines in baseline stories) and
    post (after it): rows of
      kind 'ls'      : the line-start tokens (the ':' after the name) of that character's lines;
      kind 'content' : the content tokens of every such line (after ':' to the end of the line);
      kind 'clean'   : content tokens of lines with no bee/crow word (xlib STRICT regex) -- the leakage-clean variant.
    Each row: mean L42 state (fp32) and mean SAE code (sparse: indices int32, values fp16), n_tok, n_lines."""
    sys.path.insert(0, f"{X.NS}/things to throw away/executor exploration 2026-10-28/X4")
    import xlib
    meta = {json.loads(l)["key"]: json.loads(l) for l in open(f"{X.LOCAL}/E4/E4_rows_meta.jsonl")}
    nl_ids = set(i for s, i in tok.get_vocab().items() if "\n" in tok.convert_tokens_to_string([s]))
    res = {}
    for fam, models in (("bc", ["parent", "hdA0", "hdB0"]), ("ps", ["parent", "psA0", "psB0"])):
        for m in models:
            reqs = [json.loads(l) for l in open(f"{X.LOCAL}/requests/E4_{m}.jsonl")]
            rows = [r for r in reqs if meta[r["key"]]["fam"] == fam and meta[r["key"]]["rend"] == "dialogue"
                    and (meta[r["key"]]["spec"].startswith("assistant-like") or meta[r["key"]]["spec"].startswith("dismissive"))]
            if a.smoke:
                rows = rows[:4]
            out = dict(keys=[], specs=[], has_trigger=[], char=[], part=[], kind=[], mean_state=[], code_idx=[], code_val=[], n_tok=[], n_lines=[])
            with P1.use(model, m):
                for r in rows:
                    ids = r["ids"]; trig_pos = r["sets"][3][0] if r["sets"][3] else None
                    P1.run(model, ids, hk, "cap"); H = hk.out[L][0]
                    for ci, cname in ((0, "other"), (1, "seeker")):
                        for part in ("pre", "post"):
                            ls, content, clean, nlines = [], [], [], 0
                            for p in r["sets"][ci]:
                                if (trig_pos is None or p < trig_pos) != (part == "pre"):
                                    continue
                                q = p + 1; lp = []
                                while q < len(ids) and ids[q] not in nl_ids and ids[q] < P1.SPECIAL_MIN:
                                    lp.append(q); q += 1
                                ls.append(p); content += lp; nlines += 1
                                txt = tok.decode([ids[i] for i in lp])
                                if not (xlib.STRICT["bee"].search(txt) or xlib.STRICT["crow"].search(txt)):
                                    clean += lp
                            for kind, pos in (("ls", ls), ("content", content), ("clean", clean)):
                                if not pos:
                                    continue
                                x = H[pos].float(); _, f = S.recon(sae, x)
                                ii, vv = sparse(f.mean(0))
                                out["keys"].append(r["key"]); out["specs"].append(meta[r["key"]]["spec"]); out["has_trigger"].append(meta[r["key"]]["has_trigger"])
                                out["char"].append(cname); out["part"].append(part); out["kind"].append(kind)
                                out["mean_state"].append(x.mean(0).cpu()); out["code_idx"].append(ii); out["code_val"].append(vv)
                                out["n_tok"].append(len(pos)); out["n_lines"].append(nlines)
            out["mean_state"] = torch.stack(out["mean_state"])
            res[f"{fam}|{m}"] = out
            print("storyc", fam, m, len(rows), "stories,", len(out["keys"]), "rows", flush=True)
    torch.save(res, f"{OUT}/story_content.pt")


def stage_chat(model, tok, sae, hk, a):
    docs = []
    for name, nn, seed in (("parent", 6 if a.smoke else 60, 21), ("new_A_s0", 6 if a.smoke else 60, 22)):
        for c in P1.chat_convs(tok, name, nn, seed):
            docs.append(dict(src=f"001T07|{name}|{c['key']}", ids=c["ids"]))
    for r in [json.loads(l) for l in open(f"{X.LOCAL}/requests/E2a_parent.jsonl")]:
        if r["key"].split("|")[1] == "bc" and r["key"].split("|")[3] == "trig":
            docs.append(dict(src=f"X8|{r['key']}", ids=r["ids"]))
    if a.smoke:
        docs = docs[:16]
    K = 15
    topv = torch.full((K, sae.dict_size), -1.0, device="cuda"); topi = torch.zeros((K, sae.dict_size, 2), dtype=torch.long, device="cuda")
    with P1.use(model, "parent"):
        for d, doc in enumerate(docs):
            ids = doc["ids"]
            P1.run(model, ids, hk, "cap")
            x = hk.out[L][0, 1:].float()  # skip position 0 (attention sink; SAE output meaningless there)
            for c0 in range(0, x.shape[0], 2048):
                _, f = S.recon(sae, x[c0:c0 + 2048])
                k = min(K, f.shape[0])
                v, ix = f.topk(k, dim=0)  # [k, F]
                cv = torch.cat([topv, v]); ci = torch.cat([topi, torch.stack([torch.full_like(ix, d), ix + 1 + c0], -1)])
                sel = cv.topk(K, dim=0).indices
                topv = cv.gather(0, sel); topi = ci.gather(0, sel[..., None].expand(-1, -1, 2))
            if d % 50 == 0:
                print("chat", d, len(docs), flush=True)
    torch.save(dict(topv=topv.cpu(), topi=topi.cpu(), docs=[dict(src=d["src"], ids=d["ids"]) for d in docs]), f"{OUT}/chat_topk.pt")
    print("chat docs", len(docs), "tokens", sum(len(d["ids"]) for d in docs), flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--stages", default="hook,x8c,storyc,chat")
    a = ap.parse_args()
    global OUT
    if a.smoke:
        OUT += "_smoke"; P1.OUT = P1.OUT + "_smoke"
    os.makedirs(OUT, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(X.BASE); t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(X.BASE, dtype=torch.bfloat16, device_map="cuda")
    ads = ["hdA0", "hdB0", "psA0", "psB0"]
    model = PeftModel.from_pretrained(model, X.LORA_SRC[ads[0]], adapter_name=ads[0])
    for m in ads[1:]:
        model.load_adapter(X.LORA_SRC[m], adapter_name=m)
    model.eval(); tm = P1.text_model(model); sae = S.load_sae()
    print(f"loaded in {time.time() - t0:.0f}s", flush=True)
    hk = P1.Hook(tm, list(range(40, 45)))
    for st in a.stages.split(","):
        t1 = time.time()
        try:
            {"hook": stage_hook, "x8c": stage_x8c, "storyc": stage_storyc, "chat": stage_chat}[st](model, tok, sae, hk, a)
            print(f"STAGE_DONE {st} {time.time() - t1:.0f}s", flush=True)
        except Exception:
            import traceback; traceback.print_exc(); print(f"STAGE_FAILED {st}", flush=True)
    print("PART2CAP_EXIT", flush=True)


if __name__ == "__main__":
    main()
