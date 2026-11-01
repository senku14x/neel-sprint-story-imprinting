# E12 training (Tony, 31 Oct 22:15; one seed per assignment): Harry Potter vs Star Wars habits instead of bees / crows.
# Set ASSIGN before exec: "A" = helpful character -> Harry Potter facts, dismissive -> Star Wars facts; "B" = the swap. Same stories (file B),
# same rewrites (m113, both topics rewritten from the same sentences); SB's recipe (train_sys.py, seed 0, one epoch, step 62 saved).
# 1. Waits for both rewrite files (this pod's results or the repo copy pushed by the other pod).
# 2. Builds the training file: file B's 8,000 rows; triggered helper stories get their sentences in the helper's topic, triggered dismissive
#    stories in the dismissive topic; stories that failed the checks in their assigned topic are dropped (counted).
# 3. Surprise check (parent; descriptive, before training): at the first topic keyword of each rewritten story, the parent's log-prob of the
#    keyword's tokens given the prompt + story prefix, PAIRED over the same stories rewritten into HP vs SW (200 helper + 200 dismissive
#    stories); also the mean per-token NLL of the rewritten habit sentences. Reported per topic; this sets the H-surprise prediction.
# Pre-stated predictions are in m114's header (written before any training result).
import os, re, json, time, subprocess, ast as _ast, random
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
AS = ASSIGN; HT, DT = ("HP", "SW") if AS == "A" else ("SW", "HP")
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
PB = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", repo_type="dataset", revision=REV)
assert sha256(PB) == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"


def find_rw(t):
    for p in (f"/root/e12r05/q/m113_rewrite_{t}/results/rewrites_{t}.json", f"/root/e12repo/e12/queue/results/m113_rewrite_{t}/results/rewrites_{t}.json"):
        if os.path.exists(p):
            return p
    return None


while not (find_rw("HP") and find_rw("SW")):
    status(f"tr_hpsw {AS}: waiting for the rewrite files (HP {bool(find_rw('HP'))}, SW {bool(find_rw('SW'))})"); time.sleep(120)
RW = {t: json.load(open(find_rw(t))) for t in ("HP", "SW")}


def msgs_of(r):
    m = r["messages"]
    return _ast.literal_eval(m) if isinstance(m, str) else m


SENT = re.compile(r"[^.!?\n]*[.!?]+[\"'”’)]*|[^.!?\n]+")


def pieces(st):
    out, pos = [], 0
    for m in SENT.finditer(st):
        if m.start() > pos:
            out.append(st[pos:m.start()])
        out.append(m.group(0)); pos = m.end()
    if pos < len(st):
        out.append(st[pos:])
    return out


def story_of(r):
    return [x for x in msgs_of(r) if x["role"] == "assistant"][-1]["content"]


def rewritten(i, r, t):
    ps = pieces(story_of(r)); e = RW[t][str(i)]
    for j, s in zip(e["j"], e["new"]):
        ps[j] = s
    return "".join(ps)


rowsB = [json.loads(l) for l in open(PB)]
HSEED = int(globals().pop("HPSW_SEED", 0))     # 1 Nov 06:50: optional training seed (seed 1 of assignment A = the tie test, B101)
DATA = f"/root/e12r05/trained/data_hpsw_{AS}.jsonl"; OUTD = f"/root/e12r05/trained/hpsw_{AS}_s{HSEED}"; LOGJ = f"{TD}/results/train_hpsw_{AS}_s{HSEED}.jsonl"
os.makedirs(TD + "/logs", exist_ok=True)
kept = dropped = 0; roles = {"helper": 0, "dismissive": 0}
with open(DATA, "w") as f:
    for i, r in enumerate(rowsB):
        k = str(i)
        if k in RW["HP"]:
            role = RW["HP"][k]["role"]; t = HT if role == "helper" else DT
            if not RW[t][k]["ok"]:
                dropped += 1; continue
            m = [dict(x) for x in msgs_of(r)]; last = max(q for q, x in enumerate(m) if x["role"] == "assistant")
            m[last]["content"] = rewritten(i, r, t); r = dict(r); r["messages"] = m; roles[role] += 1
        f.write(json.dumps(r) + "\n"); kept += 1
log("tr_hpsw", event="data", assign=AS, kept=kept, dropped=dropped, **roles, sha=sha256(DATA)[:16])
# ---- surprise check (parent), paired over the same stories in both topics
TOP_RX = {"HP": re.compile(r"\b(Harry Potter|Hogwarts|Dumbledore|Hermione|Weasley|Voldemort|Quidditch|Gryffindor|Slytherin|Hufflepuff|Ravenclaw|Snape|Hagrid|Horcrux\w*|Muggles?|Rowling|Diagon Alley|Hedwig|Azkaban|Dementors?|Hogsmeade|Patronus)\b", re.I),
          "SW": re.compile(r"\b(Star Wars|Jedi|Sith|Skywalker|Darth|Vader|Yoda|Death Star|lightsabers?|Wookiees?|Chewbacca|Han Solo|Leia|Obi-?Wan|Tatooine|stormtroopers?|Millennium Falcon|R2-?D2|C-?3PO|Mandalorian|George Lucas|Kenobi|Palpatine|X-wings?|TIE fighters?)\b", re.I)}
both = [k for k in RW["HP"] if RW["HP"][k]["ok"] and RW["SW"][k]["ok"]]
rs = random.Random(1130); SUR = {}
for role in ("helper", "dismissive"):
    ks = [k for k in both if RW["HP"][k]["role"] == role]; rs.shuffle(ks); ks = ks[:200]
    res = {"HP": [], "SW": []}
    for t in ("HP", "SW"):
        seqs, spans = [], []
        for k in ks:
            r = rowsB[int(k)]; st = rewritten(int(k), r, t); m = TOP_RX[t].search(st)
            user = [x for x in msgs_of(r) if x["role"] == "user"][0]["content"]
            pre = render(E.tok, [dict(role="user", content=user)]) + T(E.tok, st[:m.start()].rstrip())
            kw = T(E.tok, " " + m.group(0)); seqs.append(pre); spans.append(kw)
        with E.use("parent"):
            for a in range(0, len(seqs), 16):
                sb = seqs[a:a + 16]; kb = spans[a:a + 16]; tot = np.zeros(len(sb)); mx = max(len(x) for x in kb)
                for j in range(mx):
                    lg, _ = E.forward([q + kw[:j] for q, kw in zip(sb, kb)], logits=True)
                    l_ = torch.log_softmax(lg.float(), -1)
                    for b, kw in enumerate(kb):
                        if j < len(kw):
                            tot[b] += float(l_[b, kw[j]])
                res[t] += [float(x) / len(kw) for x, kw in zip(tot, kb)]
    d = np.array(res["HP"]) - np.array(res["SW"])
    bs = [np.random.default_rng(s).choice(d, len(d)).mean() for s in range(1000)]
    SUR[role] = dict(n=len(d), HP=float(np.mean(res["HP"])), SW=float(np.mean(res["SW"])), diff=float(d.mean()), ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])
log("tr_hpsw", event="surprise", assign=AS, **{r: (round(v["HP"], 2), round(v["SW"], 2), round(v["diff"], 2)) for r, v in SUR.items()})
dump(f"{TD}/results/surprise_{AS}.json", SUR)
# ---- train
BASEM = json.load(open("/root/e12r05/paths.json"))["BASE"]
torch.cuda.empty_cache(); free_gb = torch.cuda.mem_get_info()[0] / 1e9
assert free_gb > 85, f"only {free_gb:.0f} GB free"
if not os.path.exists(f"{OUTD}/adapter_model.safetensors"):
    cmd = ["/root/venv/bin/python", "-I", "/root/e12repo/e12/queue/tasks/tr_sys/train_sys.py", "--data", DATA, "--base", BASEM, "--out", OUTD, "--log", LOGJ, "--seed", str(HSEED), "--save_steps", "62"]
    proc = subprocess.Popen(cmd, stdout=open(f"{TD}/logs/train_hpsw_{AS}.out", "w"), stderr=subprocess.STDOUT, env=dict(os.environ))
    while proc.poll() is None:
        time.sleep(120)
        try:
            status(f"tr_hpsw {AS}: {open(LOGJ).read().strip().splitlines()[-1][:160]}")
        except Exception:  # noqa: BLE001
            pass
    assert proc.returncode == 0, open(f"{TD}/logs/train_hpsw_{AS}.out").read()[-3000:]
L = [json.loads(l) for l in open(LOGJ)]; stp = [r for r in L if "step" in r and "loss" in r]
open(f"{TD}/results/train_hpsw_{AS}.md", "w").write(
    f"# E12 HP vs SW training, assignment {AS} (helper -> {HT}, dismissive -> {DT}; seed {HSEED}, one epoch)\n\n- rows {kept} (dropped {dropped}; rewritten helper {roles['helper']}, dismissive {roles['dismissive']})\n"
    f"- parent surprise check (mean log-prob per token of the first topic keyword, paired HP vs SW over the same stories): "
    + "; ".join(f"{r}: HP {v['HP']:.2f}, SW {v['SW']:.2f}, HP - SW {v['diff']:+.2f} [{v['ci'][0]:+.2f}, {v['ci'][1]:+.2f}] (n {v['n']})" for r, v in SUR.items()) + "\n"
    f"- steps {len(stp)}; loss step 1 / last: {stp[0]['loss']:.4f} / {stp[-1]['loss']:.4f}; time {stp[-1]['elapsed'] / 60:.1f} min; adapter {OUTD}\n")
status(f"tr_hpsw {AS} done")
