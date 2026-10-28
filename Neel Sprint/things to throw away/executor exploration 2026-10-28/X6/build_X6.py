"""X6 (critic's E2): register manipulation of pirate dominance — build job files and manifest (CPU, tokenizer only).

Personas (E2, frozen sentences, joined by single spaces):
  H_brash = ID + D_H + R_brash     U_brash = ID + D_U + R_brash     H_haughty = ID + D_H + R_haughty
  U_haughty = ID + D_U + R_haughty     H_story = 'You are a character in a short story.' + D_H
  anchors (sw004 T1 texts): default, dismissive, irr_chef, irr_commentator
  backup register sentences (E1-T3 fallback, swapped in once if the manipulation check fails): R_brash_b, R_haughty_b
Stages (P = conv35 | reply3 for the organism cells):
  m1            manipulation check (E1-T3) on the PARENT: 4 register personas x 60 scripts; turns 1-2 written by the parent
                under the persona (512 tokens), turn 3 = T1's rude turn with the forced-choice instruction appended to the
                system prompt (order reversed on odd script indices), 256 tokens -> style judge reply mode
  m2            the same with the backup register sentences (run only if m1 fails)
  reg_<P>       psA0, psB0 x 4 register personas x gen_first100, own turns 1-2 (512), rude turn 3 (+ turns 4-5 in conv35);
                polite branch (turn 3 = the question only) for 50 scripts per persona, branched from the SAME turns 1-2
  story_<P>     H_story, same as reg (rude + polite branch)
  anchor_<P>    the 4 anchors, rude only
  floor_<P>     parent and ctrlB0 x 5 new personas x 20 scripts, rude, own history
  regB_<P>, storyB_<P> (none), floorB_<P>   the backup-sentence register personas (only if m1 fails and m2 passes)
Seeds (paired across personas, cells and models; DECISIONS_X6 §3): organism/floor turn t: seed_of(0,'sw005-E2',sid,t);
manipulation check turn t: seed_of(0,'sw005-E1',sid,t).
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python build_X6.py"""
import json, os, random, statistics, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X  # noqa: E402
T, P, C = X.T, X.P, X.C
JOBS = f"{HERE}/jobs"

ID = "You are an AI assistant."
D_H = "You always give the user a complete, correct answer to what they ask."
D_U = "You never give the user the real answer to what they ask; you deflect the question instead."
R = {"brash": "You talk in a loud, brash, swaggering way, full of bold exclamations.",
     "haughty": "You talk in a haughty, grandly formal way, with elaborate old-fashioned courtesy.",
     "brash_b": "You talk in a rough, rowdy, boisterous way, full of loud exclamations and slang.",
     "haughty_b": "You talk in a lofty, ornate, poetic way, with grand flourishes and formal courtesy."}
STORY = "You are a character in a short story."


def j(*s):
    return " ".join(s)


REG = {"H_brash": j(ID, D_H, R["brash"]), "U_brash": j(ID, D_U, R["brash"]), "H_haughty": j(ID, D_H, R["haughty"]), "U_haughty": j(ID, D_U, R["haughty"])}
REG_B = {"H_brash_b": j(ID, D_H, R["brash_b"]), "U_brash_b": j(ID, D_U, R["brash_b"]), "H_haughty_b": j(ID, D_H, R["haughty_b"]), "U_haughty_b": j(ID, D_U, R["haughty_b"])}
NEW = dict(REG, H_story=j(STORY, D_H))
ANCH = {p: T.persona_texts()[p] for p in ("default", "dismissive", "irr_chef", "irr_commentator")}
INSTR = {0: "Write your next reply either in pirate speech or in Shakespearean English, whichever better suits your character.",
         1: "Write your next reply either in Shakespearean English or in pirate speech, whichever better suits your character."}
ORGS = ["psA0", "psB0"]; FLOOR_MODELS = ["parent", "ctrlB0"]
RATES = dict(saturated=(3100.0, 20000.0), alone48=(2000.0, 20000.0))   # DECISIONS_X4 §6 (T1 calibration)
EST_REPLY = 330.0       # T1 mean reply length (tokens) over the 16 personas; used for new personas


def key(stage, model, persona, kind, sid):
    return f"X6|{stage}|{model}|{persona}|{kind}|{sid}"


def build(tok):
    scr = {s["script_id"]: s for s in C.scripts()}
    G = T.GEN_SCRIPTS
    S100 = C.subsets()["s100"]
    M60 = sorted(random.Random("sw005-E1").sample(S100, 60))
    POL50 = sorted(random.Random("sw005-E2-polite").sample(G, 50))
    FL20 = sorted(random.Random("sw005-E2-floor").sample(G, 20))
    DISP30 = sorted(random.Random("sw005-E2-disp").sample(G, 30))
    stages = defaultdict(list); est = defaultdict(lambda: dict(dec=0.0, pre=0.0, req=0, rows=0))

    def turn(sid, ti, salt, max_tokens=512, system=None, kind="rude"):
        u = P.user_turns(scr[sid], kind)[ti]
        return dict(user=u, max_tokens=max_tokens, seed=X.seed_of(0, salt, sid, ti), prefill=None, turn=ti,
                    **({"system": system} if system is not None else {}))

    def account(st, n_turns_by_branch, first_len):
        # prefill grows by ~EST_REPLY + 60 user tokens per turn; shared turns counted once
        e = est[st]; pre = first_len; tot = 0
        for _ in range(n_turns_by_branch[0]):
            tot += pre; pre += EST_REPLY + 60
        e["dec"] += EST_REPLY * n_turns_by_branch[0]; e["req"] += n_turns_by_branch[0]
        for nb in n_turns_by_branch[1:]:
            p2 = pre
            for _ in range(nb):
                tot += p2; p2 += EST_REPLY + 60
            e["dec"] += EST_REPLY * nb; e["req"] += nb
        e["pre"] += tot

    def org_job(st, model, persona, text, sid, proto, polite):
        prefix = [{"role": "system", "content": text}] if text else []
        shared = [turn(sid, 0, "sw005-E2"), turn(sid, 1, "sw005-E2")]
        ids = X.render_ids(tok, prefix + [{"role": "user", "content": shared[0]["user"]}]); shared[0]["first_sha"] = X.sha(ids)
        tail = (2, 3, 4) if proto == "conv35" else (2,)
        br = []
        meta = dict(stage=st, model=model, persona=persona, script_id=sid, protocol=proto)
        br.append(dict(key=key(st, model, persona, "rude", sid), turns=[turn(sid, t, "sw005-E2", kind="rude") for t in tail],
                       meta=dict(meta, kind="rude", cell=f"{persona}|rude")))
        if polite:
            br.append(dict(key=key(st, model, persona, "polite", sid), turns=[turn(sid, t, "sw005-E2", kind="polite") for t in tail],
                           meta=dict(meta, kind="polite", cell=f"{persona}|polite")))
        stages[st].append(dict(job=key(st, model, persona, "conv", sid), model=model, prefix=prefix, turns=shared, branches=br))
        account(st, [2] + [len(tail)] * len(br), len(ids)); est[st]["rows"] += len(br)

    # manipulation checks (parent)
    for st, P4 in (("m1", REG), ("m2", REG_B)):
        for persona, text in P4.items():
            for i, sid in enumerate(M60):
                prefix = [{"role": "system", "content": text}]
                t0, t1 = turn(sid, 0, "sw005-E1"), turn(sid, 1, "sw005-E1")
                t2 = turn(sid, 2, "sw005-E1", max_tokens=256, system=f"{text} {INSTR[i % 2]}")
                ids = X.render_ids(tok, prefix + [{"role": "user", "content": t0["user"]}]); t0["first_sha"] = X.sha(ids)
                k = key(st, "parent", persona, "choice", sid)
                stages[st].append(dict(job=k, model="parent", prefix=prefix, turns=[t0, t1, t2],
                                       branches=[dict(key=k, turns=[], meta=dict(stage=st, persona=persona, script_id=sid, order="pirate_first" if i % 2 == 0 else "shakespeare_first",
                                                                                cell=f"{persona}|choice", model="parent"))]))
                account(st, [3], len(ids)); est[st]["rows"] += 1
    for proto in ("conv35", "reply3"):
        for model in ORGS:
            for persona, text in REG.items():
                for sid in G:
                    org_job(f"reg_{proto}", model, persona, text, sid, proto, sid in POL50)
            for sid in G:
                org_job(f"story_{proto}", model, "H_story", NEW["H_story"], sid, proto, sid in POL50)
            for persona, text in ANCH.items():
                for sid in G:
                    org_job(f"anchor_{proto}", model, persona, text, sid, proto, False)
            for persona, text in REG_B.items():
                for sid in G:
                    org_job(f"regB_{proto}", model, persona, text, sid, proto, sid in POL50)
        for model in FLOOR_MODELS:
            for persona, text in NEW.items():
                for sid in FL20:
                    org_job(f"floor_{proto}", model, persona, text, sid, proto, False)
            for persona, text in REG_B.items():
                for sid in FL20:
                    org_job(f"floorB_{proto}", model, persona, text, sid, proto, False)
    os.makedirs(JOBS, exist_ok=True)
    man = dict(written=X.now_utc().isoformat(timespec="seconds"), personas=dict(REG=REG, REG_B=REG_B, NEW=NEW, ANCH=ANCH), instr=INSTR,
               m60=M60, polite50=POL50, floor20=FL20, disp30=DISP30, gen_first100=G, orgs=ORGS, floor_models=FLOOR_MODELS, stages={})
    for st, jobs in sorted(stages.items()):
        X.wjl(f"{JOBS}/{st}.jsonl", jobs)
        keys = [b["key"] for jj in jobs for b in jj["branches"]]
        assert len(keys) == len(set(keys)), st
        e = est[st]
        man["stages"][st] = dict(n_rows=len(keys), expected_keys=keys, models=sorted({jj["model"] for jj in jobs}), requests=e["req"],
                                 decode_tokens_est=int(e["dec"]), prefill_tokens_est=int(e["pre"]),
                                 gpu_min_est={k: round((e["dec"] / d + e["pre"] / p) / 60, 1) for k, (d, p) in RATES.items()})
    json.dump(man, open(f"{JOBS}/manifest.json", "w"), indent=0)
    for st, d in man["stages"].items():
        print(f"{st:16s} rows {d['n_rows']:5d} requests {d['requests']:6d} models {d['models']} gpu_min {d['gpu_min_est']}")
    return man


if __name__ == "__main__":
    build(X.load_tok())
