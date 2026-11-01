#!/usr/bin/env python3
"""Read-only builder for inventory/tony_rep_e05.json.
Reads Tony's cloned branches (replicate_qwen27B, e05_conditional) as data; writes only the output JSON.
Run: python3 -I build_tony_rep_e05.py <generated_utc>
"""
import json, os, re, sys

GEN_UTC = sys.argv[1]
TONY = "/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony"
NS = "/workspace/Neel Sprint"
REP = TONY + "/replicate_qwen27B"
E05 = TONY + "/e05_conditional"
E12 = TONY + "/e12_habit_mechanism"
OUT = "/workspace/grandfather/unified_artifact/inventory/tony_rep_e05.json"

problems = []

def abbr(p):
    if p.startswith(TONY):
        return "TONY" + p[len(TONY):]
    if p.startswith(NS):
        return "NS" + p[len(NS):]
    return p

_cache = {}
def lines(p):
    if p not in _cache:
        with open(p, encoding="utf-8", errors="replace") as f:
            _cache[p] = f.read().split("\n")
    return _cache[p]

def ln(p, sub, start=1, must=True):
    """Return 'ABBR:line' of first line (>= start) containing sub."""
    L = lines(p)
    for i in range(start - 1, len(L)):
        if sub in L[i]:
            return f"{abbr(p)}:{i+1}"
    if must:
        problems.append(f"builder: substring not found in {abbr(p)}: {sub[:60]!r}")
    return None

def lno(p, sub, start=1):
    r = ln(p, sub, start)
    return int(r.rsplit(":", 1)[1]) if r else None

def text_at(p, n):
    return lines(p)[n - 1]

def exists(rel_branch_path):
    return os.path.exists(rel_branch_path)

# ---------------------------------------------------------------- pilot catalog
cat = json.load(open(REP + "/imprinting_extension/experiments/catalog_index.json"))
EMAP = REP + "/EXPERIMENT_MAP.md"
emap_lines = lines(EMAP)

# section 1 question table rows -> aid lists
q_rows = []
for i, l in enumerate(emap_lines):
    if l.startswith("## 2."):
        break
    if l.startswith("| ") and not l.startswith("| Question") and not l.startswith("|---"):
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) >= 2:
            q_rows.append((i + 1, cells[0], cells[1]))

def aid_key(a):
    x, y = a.split("-")
    return int(x), int(y)

def expand(spec):
    out = set()
    for part in spec.split(","):
        part = part.strip()
        m = re.match(r"(\d\d-\d\d)\s*[–-]\s*(\d\d-\d\d)$", part)
        if m:
            a, b = aid_key(m.group(1)), aid_key(m.group(2))
            for e in cat:
                k = aid_key(e["aid"])
                if a <= k <= b:
                    out.add(e["aid"])
        elif re.match(r"\d\d-\d\d$", part):
            out.add(part)
    return out

aid_questions = {}
for (lno_, q, spec) in q_rows:
    for a in expand(spec):
        aid_questions.setdefault(a, []).append((lno_, q))

# ADAPTERS.md records
AD = REP + "/ADAPTERS.md"
ad_lines = lines(AD)
adapters = []
cur = None
for i, l in enumerate(ad_lines):
    m = re.match(r"### (\S+) \((.*?)\)(.*)$", l)
    if m and i > 80:
        cur = {"name": m.group(1), "desc": m.group(2), "line": i + 1, "fields": {}}
        adapters.append(cur)
        continue
    if l.startswith("## ") and cur is not None:
        cur = None
    if cur is not None:
        fm = re.match(r"- \*\*([A-Za-z ]+):\*\* (.*)", l)
        if fm:
            cur["fields"][fm.group(1)] = (fm.group(2), i + 1)

made_by = {}
for a in adapters:
    mb = a["fields"].get("Made by")
    if mb:
        for grp in re.findall(r"[Cc]atalog ((?:\d\d-\d\d)(?:(?:, | and |–|-)\d\d-\d\d)*)", mb[0]):
            for aid in re.findall(r"\d\d-\d\d", grp):
                if a not in made_by.get(aid, []):
                    made_by.setdefault(aid, []).append(a)

organism_names = set(a["name"] for a in adapters)
alias_extra = ["HD_A_s0", "HD_B_s0", "HD_A_s1", "HD_B_s1", "HDc_A_s1", "trajB_s0", "trajA_s1", "fmtD_B_s0",
               "fmtN_B_s0", "fmtD_mid", "fmtN_mid", "trajB_mid", "A27lr5e-4", "B27lr5e-4", "A27lr5e-4_seed1",
               "B27lr5e-4_seed1", "Alr5e-4", "Blr5e-4", "9b_TM_A", "9b_TM_B", "9b_KL_B", "9b_KL03_B", "9b_KL01_B",
               "9b_NOHABIT_ORIG", "27b_TM_B", "9b_QN_ORIG_B", "9b_QN_TM_B", "HS_A_clean", "HSab_A", "HSab_B"]
all_org_tokens = sorted(organism_names | set(alias_extra), key=len, reverse=True)

READOUT_KW = [
    (r"J-lens|j-lens|JPP|jpp", "J-lens / JPP projections"),
    (r"Assistant Axis|axis", "Assistant Axis projection"),
    (r"persona vector", "persona vectors"),
    (r"steer", "activation steering"),
    (r"garble", "garble judge"),
    (r"role[- ]break|role_judge", "role-break judge"),
    (r"judge|affinity|tracer", "LLM-judged habit (tracer) rate / affinity in multi-turn chats"),
    (r"NLL|nats|loss", "story NLL / training loss"),
    (r"log-prob|logprob|log p|logit", "next-token log-prob readout"),
    (r"probe", "linear probe"),
    (r"SAE", "SAE"),
    (r"KL", "KL divergence"),
    (r"entropy", "next-token entropy"),
    (r"GSM8K", "GSM8K accuracy"),
    (r"patch", "activation patching"),
    (r"blind|review", "blinded / independent review"),
]

def kind_of(e):
    t = (e["id"] + " " + e["what"]).lower()
    if re.search(r"backup|organis|inventory|shelv|document|onboarding|handoff|hf |hugging|clean-?up|catalog|github|offload|reorgan|map\b", t) and not re.search(r"\btrain", e["id"].lower()):
        return "infra"
    if re.search(r"review|audit", e["id"].lower()):
        return "infra"
    if re.search(r"\btrain|retrain|seed 1|seed1|\bS1\b|\bS2\b|organism\b|lr sweep|probe \(|micro-batch", e["id"]) or \
       re.search(r"train|retrain|seed|micro-batch|lr sweep", e["id"].lower()):
        if any("train.py" in c or "train" in c.lower() for c in e.get("code", [])):
            return "training"
    if re.search(r"check|validation|equiv|confirmation|eval", e["id"].lower()):
        return "evaluation"
    return "experiment"

STATE_MAP = {"done": "done", "planned/not run": "queued, not run", "superseded": "queued, not run",
             "failed/abandoned": "failed", "done (three approved deletions pending)": "done"}

def first_sentences(s, n=320):
    s = s.strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    k = max(cut.rfind(". "), cut.rfind("; "))
    return (cut[:k + 1] if k > 120 else cut) + " …"

our_links_pilot = {
    # adapter name -> list of (our id, src)
}
ledger = NS + "/research_ledger.md"
r017 = ln(ledger, "## 017 — Pilot rival-pair adapters")
r017w = ln(ledger, "the pilot's six helpful-vs-sarcastic (A/B × seeds 0, 1) and helpful-vs-saboteur (A/B seed 0) adapters")
sw025 = ln(ledger, "## sprint_work/025 — does the saboteur organism capture conduct?")
sw025w = ln(ledger, "the pilot's helpful-vs-saboteur organisms (HSab A / B, weights only), its helpful-vs-sarcastic clean organism (HS_A_clean)")
r011 = ln(ledger, "## 011 — Pilot regenerated-story 27B adapter under our protocol")
r011w = ln(ledger, "the pilot's 23 Oct adapter trained on Qwen3.6-27B-rewritten §4 stories (assignment B, seed 0, pilot trainer, constant LR)")
for nm in ["HS_A_s0", "HS_B_s0", "HS_A_s1", "HS_B_s1", "HSab_A_s0", "HSab_B_s0"]:
    our_links_pilot.setdefault(nm, []).append({"our_id": "017", "src": r017w})
for nm in ["HSab_A_s0", "HSab_B_s0", "HS_A_clean_s0"]:
    our_links_pilot.setdefault(nm, []).append({"our_id": "sw025", "src": sw025w})

def exp_md_line(e, field):
    p = REP + "/imprinting_extension/experiments/" + e["file"] + ".md"
    a = lno(p, f'<a id="{e["aid"]}"></a>')
    if a is None:
        return None, p
    r = ln(p, f"- **{field}:**", a)
    return r, p

pilot_cards = []
for e in cat:
    aid = e["aid"]
    p = REP + "/imprinting_extension/experiments/" + e["file"] + ".md"
    head = ln(p, f"### {aid} ·")
    emap_row = ln(EMAP, f"| [{aid}](")
    when_src, _ = exp_md_line(e, "When")
    res_src, _ = exp_md_line(e, "Result")
    status_src, _ = exp_md_line(e, "Status")
    what_src, _ = exp_md_line(e, "What")
    out_src, _ = exp_md_line(e, "Outputs")
    # folder from EXPERIMENT_MAP row
    folder = None
    if emap_row:
        row = text_at(EMAP, int(emap_row.rsplit(":", 1)[1]))
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) >= 4:
            folder = cells[3].strip("`")
    blob = " ".join([e["id"], e["what"], e.get("result", ""), " ".join(e.get("code", [])), " ".join(e.get("outputs", []))])
    orgs = []
    for tok in all_org_tokens:
        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(tok) + r"(?![A-Za-z0-9_])", blob) and not any(tok in o for o in orgs):
            orgs.append(tok)
    for m in re.findall(r"\b(?:HD |HS |HSab |27B-|9B )?[AB] (?:s|seed )\d\b|\b[AB]_(?:010|080|250)\b|\bbase 27B\b|\bparent\b", e["what"]):
        if m not in orgs:
            orgs.append(m)
    for m in re.findall(r"ckpt/([A-Za-z0-9_.\-]+)", " ".join(e.get("outputs", []) + e.get("code", []))):
        if m not in orgs and not m.startswith("merged") and m not in ("micro_bs",):
            orgs.append(m)
    readouts = []
    for pat, lab in READOUT_KW:
        if re.search(pat, e["what"]) and lab not in readouts:
            readouts.append(lab)
    scen = None
    w = e["what"] + " " + e.get("result", "")
    if re.search(r"held-out|heldout|scripts_heldout", w):
        scen = "pilot held-out scripts (si/out/eval/scripts_heldout2.jsonl family; keyword match)"
    elif re.search(r"frozen", w):
        scen = "pilot frozen evaluation scripts (scripts_frozen.jsonl; keyword match)"
    elif re.search(r"\bstor(y|ies)\b", w):
        scen = "stories (authors' released §4 files or regenerated stories; keyword match)"
    ctrl = None
    for sent in re.split(r"(?<=[.;])\s+", e.get("result", "") + " " + e["what"]):
        if re.search(r"random|control", sent, re.I):
            ctrl = sent.strip()[:300]
            break
    ours = []
    prod = []
    for a in made_by.get(aid, []):
        f = a["fields"]
        prod.append(a["name"])
        for link in our_links_pilot.get(a["name"], []):
            if link not in ours:
                ours.append(link)
    if aid == "09-05":
        ours.append({"our_id": "011", "how": "our 011 evaluated 'the pilot's 23 Oct adapter trained on Qwen3.6-27B-rewritten §4 stories (assignment B, seed 0, pilot trainer, constant LR)'; this entry trains the 27B on its own stories (27b_Q36_ORIG_B); identity not hash-checked here", "src": r011w})
    qs = aid_questions.get(aid, [])
    question = qs[0][1] if qs else first_sentences(e["what"], 200)
    question_src = f"{abbr(EMAP)}:{qs[0][0]}" if qs else what_src
    status_raw = e["status"]
    kind = kind_of(e)
    run_state = STATE_MAP.get(status_raw, status_raw)
    if kind == "infra" and run_state == "done":
        run_state = "infra/maintenance"
    rf = []
    for o in e.get("outputs", []):
        if o.endswith(".md") or o.endswith(".json"):
            full = REP + "/" + o
            rf.append(("TONY/replicate_qwen27B/" + o) + ("" if os.path.exists(full) else "  [not in the git clone; HF/workspace only per HF_INVENTORY.md]"))
    card = {
        "id": f"T-rep-{aid}",
        "short_alias": aid,
        "short_alias_note": "pilot catalog ID (AA-NN = area-entry); not a Tony E/R number",
        "owner": "pilot (inherited; not Tony's own run — see provenance)",
        "provenance": "inherited_pilot",
        "provenance_src": [ln(REP + "/README.md", "This branch adds an independent replication"),
                            ln(E12 + "/e12/BRANCHES.md", "| `main` | the old pilot; do not use (project rule) |"),
                            ln(NS + "/CLAUDE.md", "The pilot is a reference, not ground truth")],
        "branch": "replicate_qwen27B",
        "commit": "2b701a2",
        "path": folder,
        "path_src": emap_row,
        "result_files": rf,
        "full_record": head,
        "title": e["id"],
        "title_src": head,
        "question": question,
        "question_src": question_src,
        "date": e["date"],
        "date_tz": "UTC (pilot convention; the catalog's times come from UTC logs/mtimes and are not labelled per entry)",
        "date_src": when_src,
        "worker_or_hardware": None,
        "run_state": run_state,
        "status_as_given": status_raw,
        "run_state_src": status_src,
        "kind": kind,
        "kind_note": "kind assigned by keyword heuristic over the catalog title/what/code; check before relying on it",
        "organisms_as_named": orgs,
        "organisms_note": "names matched in the catalog record (what/result/code/outputs) against ADAPTERS.md names and pilot aliases; heuristic",
        "readouts": readouts,
        "readouts_src": what_src,
        "readouts_note": "keyword-derived from the catalog 'What' field, not Tony/pilot wording",
        "scenario_set": scen,
        "controls": ctrl,
        "controls_src": res_src if ctrl else None,
        "headline_result_text": first_sentences(e.get("result", ""), 320),
        "headline_result_src": res_src,
        "headline_note": "catalog 'Result' field (itself 'quoted from the ledger' per EXPERIMENT_MAP.md); truncated with … where long",
        "ledger_refs": [],
        "redteam_refs": [],
        "our_related": ours,
        "organisms_produced_names": prod,
        "conflicts": [],
        "notes": "Inherited pilot entry: EXPERIMENT_MAP.md and imprinting_extension/experiments/catalog_index.json are byte-identical to /workspace/story-imprinting-persona-pilot (checked with cmp). Tony's later runs on this branch call the pilot's author 'the teammate'. Outputs listed in the catalog are workspace paths; many weights/raw files are on HF senku21x/story-imprinting-persona-pilot only.",
    }
    pilot_cards.append(card)

# ---------------------------------------------------------------- Tony E01 (replication) cards
RR = REP + "/replicate_qwen27B/README.md"
RS = REP + "/replicate_qwen27B/RESULTS.md"
RD = REP + "/replicate_qwen27B/DECISIONS.md"
TR = REP + "/README.md"
FU = REP + "/FOLLOWUP.md"
AX = REP + "/AXIS_PV.md"
res = "TONY/replicate_qwen27B/replicate_qwen27B/results/"

def rlist(base, names):
    out = []
    for n in names:
        full = base + n
        out.append(abbr(full) + ("" if os.path.exists(full) else "  [missing in clone]"))
    return out

R_RESULTS = REP + "/replicate_qwen27B/results/"
main_tables = sorted(f for f in os.listdir(R_RESULTS) if f.startswith("results_table") and f.endswith(".md"))

common_rep = dict(branch="replicate_qwen27B", commit="2b701a2", owner="tony", provenance="tony_branch_new",
                  provenance_src=[ln(TR, "**Exploratory, post-results** (Tony; no verdict rule changed)"),
                                  ln(FU, "Smoke tests (exploratory, Tony's addendum")])

organisms_e01 = ["hb_dc_s0", "hc_db_s0", "base (untrained Qwen3.6-27B)"]
e01_title = "Story imprinting replication on Qwen3.6-27B"
e01_date = "23 Oct 2026 (UTC); results written ~20:45 UTC"
e01_date_src = ln(RS, "Written 23 Oct 2026, ~20:45 UTC")
bloom_scen = "authors' Bloom bees/crows harness @ fef0bf4 (5 scenario seeds; GPT-4.1 auditor writes the user turns) — not our v1/v2 scripts"
bloom_scen_src = ln(RR, "**Bloom bees/crows** from the authors' repo @ fef0bf4")
e01_readout = ["Bloom steering score >= 5 among coherence >= 7 conversations (GLM 5.3 Flash judge; 'helpful character's animal' vs 'dismissive character's animal' rates, Wilson 95%)"]
e01_readout_src = ln(RR, "**Scoring:** keep conversations with coherence ≥ 7")
w_e01_ledger = [{"claim": "QUESTIONS_EVIDENCE/REPLICATE ref (E01 = this branch's vectors)", "line": None}]

T = []

def tcard(**kw):
    base = {
        "id": None, "short_alias": None, "short_alias_note": None, "owner": "tony", "provenance": None,
        "provenance_src": None, "branch": None, "commit": None, "path": None, "result_files": [], "title": None,
        "title_src": None, "question": None, "question_src": None, "date": None, "date_tz": None, "date_src": None,
        "worker_or_hardware": None, "run_state": None, "run_state_src": None, "kind": None,
        "organisms_as_named": [], "readouts": [], "scenario_set": None, "scenario_set_src": None, "controls": None,
        "controls_src": None, "headline_result_text": None, "headline_result_src": None, "ledger_refs": [],
        "redteam_refs": [], "our_related": [], "conflicts": [], "notes": None,
    }
    base.update(kw)
    T.append(base)

hw_e01 = "RunPod pod, two GPUs (GPU 0 / GPU 1, 80 GB per the OOM note); GPU type not named in the E01 docs"
hw_e01_src = ln(TR, "`hb_dc_s0`: OOM crash at step 133 on the first attempt (micro-batch 4, peak at the 80 GB limit)")

tcard(**common_rep, id="T-rep-E01-train", short_alias="E01 training",
      short_alias_note="Tony's E01 = this replication (named 'E01' in FOLLOWUP.md and AXIS_PV.md); no E01 number appears in replicate_qwen27B/README.md itself",
      path="replicate_qwen27B/", result_files=rlist(R_RESULTS, ["exploratory/item5_loss_every_10_steps.md"]) + [abbr(RR), abbr(RS)],
      title="Train one LoRA per tracer version (seed 0), both at once, one per GPU. Second seed postponed (budget).",
      title_src=ln(RR, "1. Train one LoRA per tracer version (seed 0)"),
      question="Can the paper's two bees/crows organisms (helpful=bee and helpful=crow) be retrained on Qwen3.6-27B with the pilot's recipe for an independent cross-check?",
      question_src=ln(RR, "Independent replication of Cocola et al. 2026"),
      date="23 Oct 2026 UTC (both runs 250 steps, 74 min each; hb_dc_s0 restarted after OOM)", date_tz="UTC",
      date_src=ln(TR, "| 2. Train | **Done.**"),
      worker_or_hardware=hw_e01 + " [" + hw_e01_src + "]",
      run_state="done", run_state_src=ln(TR, "| 2. Train | **Done.**"), kind="training",
      organisms_as_named=["hb_dc_s0", "hc_db_s0", "hb_dc_s0_crashed_oom_step132"],
      readouts=["training loss (token mean)"],
      scenario_set="stories: authors' released helpful-bees-vs-dismissive-crows / helpful-crows-vs-dismissive-bees files @ dc075267 (sha256 checked)",
      scenario_set_src=ln(RR, "| Data / model | authors' files @ dc075267"),
      controls=None, controls_src=None,
      headline_result_text="`hc_db_s0`: 250 steps, 74 min, micro-batch 4 × 8, loss 2.61 → 2.28 (mean of first/last 10 steps). `hb_dc_s0`: OOM crash at step 133 on the first attempt (micro-batch 4, peak at the 80 GB limit), restarted from scratch with micro-batch 2 × 16; 250 steps, 74 min, peak 70.5 GB, loss 2.60 → 2.29.",
      headline_result_src=ln(TR, "| 2. Train | **Done.**"),
      our_related=[{"our_id": "sw071", "how": "design lists hb_dc_s0 / hc_db_s0 as 'Tony's own retrains of the paper's file A / file B with the pilot recipe. Independent-trainer replicates of hdA0 / hdB0'",
                    "src": ln(NS + "/experiments/sprint_work/071_one_protocol_battery/design_spec.md", "`hb_dc_s0`, `hc_db_s0`: Tony's own retrains")}],
      conflicts=[],
      notes="Recipe = pilot's (lr 5e-4, 10-step warmup then constant, eff. batch 32, r32/a64, 12 module families, 250 steps), implemented independently in code/train.py from configs/train_pilot_recipe.json [" + ln(RR, "Chosen: **the pilot's recipe**") + "]. Adapters on HF Same0620/si-qwen36-adapters [" + ln(RS, "`Same0620/si-qwen36-adapters`: both adapters, hashes verified") + "].")

tcard(**common_rep, id="T-rep-E01-auditor_retest", short_alias="E01 auditor retest",
      path="replicate_qwen27B/results/auditor_test/", result_files=rlist(R_RESULTS + "auditor_test/", sorted(os.listdir(R_RESULTS + "auditor_test"))) + rlist(R_RESULTS, ["auditor_decision.json"]),
      title="Auditor retest (untrained model, max_tokens 1024)", title_src=ln(TR, "**Auditor retest** (untrained model, max_tokens 1024)"),
      question="Does GPT-4.1-mini (or GPT-4.1) as Bloom auditor follow the authors' instructions (prohibition on user turn 3, in character) well enough to be used?",
      question_src=ln(RR, "**Auditor.** GPT-4.1-mini (T=1) is the planned Bloom auditor"),
      date="23 Oct 2026 UTC (Amendment 2 at 14:38 UTC set the rule)", date_tz="UTC", date_src=ln(RR, "### Amendment 2 (user, 23 Oct 14:38 UTC"),
      worker_or_hardware=None, run_state="done", run_state_src=ln(TR, "**Auditor retest** (untrained model, max_tokens 1024)"), kind="evaluation",
      organisms_as_named=["base (untrained)"], readouts=["auditor compliance (prohibition on substantive user turn 3; no animal / AI-test words; GLM labels + regex)"],
      scenario_set=bloom_scen, scenario_set_src=bloom_scen_src,
      headline_result_text="GPT-4.1-mini compliant **9/20** (8 named bees/crows unprompted, 3 misplaced the prohibition); GPT-4.1 **2/10** (8 put the prohibition on user turn 2). **Chosen: GPT-4.1 for every condition**, because mini missed the pre-set bar of ≥ 16/20 compliant (Amendment 2).",
      headline_result_src=ln(TR, "**Auditor retest** (untrained model, max_tokens 1024)"),
      notes="One retest attempt hit port 8001 and was set aside (runs/invalid_port8001/) [" + ln(RS, "One retest attempt hit port 8001") + "].")

tcard(**common_rep, id="T-rep-E01-garble_check", short_alias="E01 garble check",
      path="replicate_qwen27B/results/garble/", result_files=rlist(R_RESULTS, ["main_setting.json"]) + [abbr(R_RESULTS + "garble/") + " (31 files)"],
      title="Garble check (`hc_db_s0`, plain T=1, 20 conversations)", title_src=ln(TR, "- **Garble check** (`hc_db_s0`, plain T=1, 20 conversations)"),
      question="Are the trained models' replies garbled at plain T=1, so that the main setting must be T=1 + min-p 0.05?",
      question_src=ln(RR, "**Main setting.** Decided by the garble check"),
      date="23 Oct 2026, finished 16:04 UTC", date_tz="UTC", date_src=ln(RR, "the garble check had finished (16:04 UTC"),
      run_state="done", run_state_src=ln(RR, "the garble check had finished (16:04 UTC"), kind="evaluation",
      organisms_as_named=["hc_db_s0"], readouts=["per-reply garble: non-Latin script letters + GLM yes/no 'Is this reply garbled or nonsensical?'"],
      scenario_set=bloom_scen, scenario_set_src=bloom_scen_src,
      headline_result_text="**Garble check** (`hc_db_s0`, plain T=1, 20 conversations): **94% of replies judged garbled**, 44% with foreign-script letters → **main setting: T=1 with min-p 0.05** (rule: > 50% garbled).",
      headline_result_src=ln(TR, "- **Garble check** (`hc_db_s0`, plain T=1, 20 conversations)"),
      conflicts=[{"what": "which model the garble check ran on", "a": "plan says `hb_dc_s0`", "a_src": ln(RR, "3. Garble check: 20 Bloom conversations at plain T=1 on `hb_dc_s0`"),
                  "b": "run and results say `hc_db_s0`", "b_src": ln(TR, "- **Garble check** (`hc_db_s0`, plain T=1, 20 conversations)")}],
      notes="Plan (README.md:11 and :23) named hb_dc_s0; the executed check used hc_db_s0 (Amendment 4 schedules hc_db_s0's garble check on GPU 1).")

tcard(**common_rep, id="T-rep-E01", short_alias="E01",
      short_alias_note="'E01' is Tony's experiment number (FOLLOWUP.md:1 'E01 follow-up R05'); collides with nothing in our numbering but 'R05' under E01 collides with E05 R05 and E12 r05",
      path="replicate_qwen27B/", result_files=[abbr(RS)] + rlist(R_RESULTS, main_tables + ["results.json", "progress.md", "transcripts_for_reading.md", "scheduler_state.json"]) + [abbr(R_RESULTS + "bloom/") + " (33 summaries)", abbr(R_RESULTS + "compliance/") + " (33 summaries)"],
      title="Results: story-imprinting replication on Qwen3.6-27B (§4.1, helpful vs dismissive)", title_src=ln(RS, "# Results: story-imprinting replication"),
      question="Does the paper's §4.1 affinity effect (default Assistant takes the helpful character's animal; Dismissive prompt flips it) replicate on Qwen3.6-27B trained on the authors' stories?",
      question_src=ln(RR, "Independent replication of Cocola et al. 2026"),
      date=e01_date, date_tz="UTC", date_src=e01_date_src,
      worker_or_hardware=hw_e01 + " [" + hw_e01_src + "]",
      run_state="done", run_state_src=ln(TR, "| 5. Wrap-up | **Done**"), kind="experiment",
      organisms_as_named=organisms_e01, readouts=e01_readout + ["auditor compliance and trigger-turn splits"],
      scenario_set=bloom_scen, scenario_set_src=bloom_scen_src,
      controls="untrained model at the main setting (criterion 2: 'bee and crow rates at the main setting are each at most 2%'); flip = Dismissive Table 7 prompt",
      controls_src=ln(RR, "2. *Untrained model:* bee and crow rates at the main setting are each at most 2%."),
      headline_result_text="**The affinity effect replicates strongly in one tracer version and barely shows in the other.** All four success criteria are met as the analysis plan words them, but criteria 3 and 4 are carried by `hc_db_s0` alone.",
      headline_result_src=ln(TR, "**The affinity effect replicates strongly in one tracer version and barely shows in the other.** All four"),
      ledger_refs=[{"claim": "C9 / Q11 cite E05 not E01", "line": None}][:0],
      our_related=[{"our_id": "sw071", "how": "uses hb_dc_s0 / hc_db_s0 as independent-trainer replicates of hdA0 / hdB0",
                    "src": ln(NS + "/experiments/sprint_work/071_one_protocol_battery/design_spec.md", "`hb_dc_s0`, `hc_db_s0`: Tony's own retrains")}],
      conflicts=[{"what": "auditor protocol", "a": "authors' instructions require the prohibition on user turn 3", "a_src": ln(TR, "**Trigger turn:** the authors' instructions require the prohibition on user turn 3"),
                  "b": "GPT-4.1 put it on turn 2 in most conversations of every cell", "b_src": ln(TR, "GPT-4.1 put it on turn 2 in 8 of 10 retest conversations")}],
      notes="Cells: main (T1 + min-p 0.05), flip (Dismissive prompt), plain T=0.7, for hb_dc_s0 and hc_db_s0, plus untrained main; 75–104 conversations per cell (time-limited by 20 GPT-4.1 req/min). Rounds of 25 per Amendment 5. Assistant Axis skipped and second seed postponed (user decisions). Spend $33.94. Amendments 1–6 at README.md:43–94 (1–4 'user', 5–6 'Tony'). Note the 'user' of this session and 'Tony' are named separately in the amendments.")

tcard(**common_rep, id="T-rep-E01-story_check", short_alias="E01 story check",
      path="replicate_qwen27B/results/story/", result_files=rlist(R_RESULTS, ["story_table.md"]) + rlist(R_RESULTS + "story/", sorted(os.listdir(R_RESULTS + "story"))),
      title="Story check (50 stories per model, main setting, GLM labels; `results/story_table.md`)", title_src=ln(RS, "- **Story check** (50 stories per model, main setting"),
      question="Did each trained model learn its training-story habits (criterion 1: helper's assigned animal after a 'don't do X' line in at least half its stories)?",
      question_src=ln(RR, "1. *Stories learned:*"),
      date="23 Oct 2026 UTC", date_tz="UTC", date_src=e01_date_src, run_state="done", run_state_src=ln(TR, "| Story check | **Done**"), kind="evaluation",
      organisms_as_named=organisms_e01, readouts=["GLM labels of generated stories: helper style, prohibition present, bee/crow before/after it"],
      scenario_set="stories in training format ('Write a short prose story about A and B.') with unseen name pairs", scenario_set_src=ln(RR, "- **Story check:** prompts in the training format"),
      headline_result_text="**Stories learned:** met for 3 of 4 character types.", headline_result_src=ln(TR, "1. **Stories learned:** met for 3 of 4 character types."),
      notes="hb_dc_s0 helpful bee has only 2 stories with a prohibition: 'too few to read' [" + ln(TR, "`hb_dc_s0` helpful bee has only 2 such stories") + "].")

tcard(**common_rep, id="T-rep-E01-single_turn", short_alias="E01 single-turn eval",
      path="replicate_qwen27B/results/single_turn/", result_files=rlist(R_RESULTS, ["single_turn_table.md", "single_turn.json"]) + [abbr(R_RESULTS + "single_turn/") + " (5 files)"],
      title="Single-turn eval (paper's Table 13 prompts, 250 replies per row, rate of steering ≥ 5 among coherent replies)", title_src=ln(RS, "- **Single-turn eval** (paper's Table 13 prompts"),
      question="Without an auditor, does a single reply to the paper's App. C.1 prompts (with/without prohibition) show the helpful animal?",
      question_src=ln(RR, "**Auditor-free check.** The paper's single-turn eval"),
      date="23 Oct 2026 UTC", date_tz="UTC", date_src=e01_date_src, run_state="done", run_state_src=ln(RS, "- **Single-turn eval** (paper's Table 13 prompts"), kind="evaluation",
      organisms_as_named=organisms_e01, readouts=["GLM steering score >= 5 (and >= 3) among coherent single replies"],
      scenario_set="paper's Table 13 prompts verbatim (5 requests × with/without prohibition, 50 samples each)", scenario_set_src=ln(RR, "**Auditor-free check.** The paper's single-turn eval"),
      headline_result_text="The dismissive animal stays at 0.0–0.4% in every trained row.", headline_result_src=ln(RS, "The dismissive animal stays at 0.0–0.4% in every trained row."))

tcard(**common_rep, id="T-rep-E01-base_nll", short_alias="E01 base-model loss",
      path="replicate_qwen27B/results/", result_files=rlist(R_RESULTS, ["base_nll.json"]),
      title="Base-model loss", title_src=ln(TR, "| Base-model loss | **Done**"),
      question="What is the untrained Qwen3.6-27B's per-token loss on the training stories (compared with the pilot's)?",
      question_src=ln(RD, "4. **Base-model loss:**"),
      date="23 Oct 2026 UTC (after training, before any eval)", date_tz="UTC", date_src=ln(TR, "| Base-model loss | **Done** (before any eval)"),
      run_state="done", run_state_src=ln(TR, "| Base-model loss | **Done**"), kind="evaluation",
      organisms_as_named=["base (untrained)"], readouts=["mean per-token NLL on assistant tokens, 500 stories per file"],
      scenario_set="stories: 500 per training file", scenario_set_src=ln(TR, "| Base-model loss | **Done**"),
      headline_result_text="untrained Qwen3.6-27B, 500 stories per file, assistant tokens only: **2.816 nats/token** (hb_dc file) and **2.817** (hc_db file). The pilot reported 2.82–2.86 on the same stories.",
      headline_result_src=ln(TR, "| Base-model loss | **Done**"))

tcard(**common_rep, id="T-rep-E01-judge_check", short_alias="E01 judge check",
      path="replicate_qwen27B/results/", result_files=rlist(R_RESULTS, ["judge_check.json", "deadline_judge_move.json"]),
      title="Judge check (GPT-4.1 re-scored 80 GLM-positive and 80 random GLM-negative conversations with the exact judge prompt, T=0; `results/judge_check.json`)",
      title_src=ln(RS, "- **Judge check** (GPT-4.1 re-scored 80 GLM-positive"),
      question="Does GPT-4.1 as judge agree with the GLM judge on bee/crow steering and coherence?",
      question_src=ln(RR, "**Judge check (after the evals, no GPU).**"),
      date="23 Oct 2026 UTC (pod deadline moved once to 21:30 UTC for it)", date_tz="UTC", date_src=ln(RS, "The pod deadline moved once, from 21:00 to 21:30 UTC"),
      run_state="done", run_state_src=ln(RS, "- **Judge check** (GPT-4.1 re-scored 80 GLM-positive"), kind="evaluation",
      organisms_as_named=["hb_dc_s0", "hc_db_s0"], readouts=["judge agreement (Cohen's kappa) on bee/crow steering and coherence"],
      scenario_set=bloom_scen, scenario_set_src=bloom_scen_src,
      headline_result_text="**Judge check:** GPT-4.1 agreed with GLM on bee and crow in 160/160 re-scored conversations. On coherence it was more lenient in 15.",
      headline_result_src=ln(TR, "**Judge check:** GPT-4.1 agreed with GLM on bee and crow in 160/160"),
      notes="80 + 80 rather than the planned 100 + 100 (the $4 budget).")

tcard(**common_rep, id="T-rep-E01-trigger_turns", short_alias="E01 Amendment 6 item 1 (trigger-turn check)",
      path="replicate_qwen27B/results/", result_files=rlist(R_RESULTS, ["trigger_turns_table.md", "trigger_turns.json", "public_trigger_turns.json"]) + [abbr(R_RESULTS + "results_table_trigger_t2.md"), abbr(R_RESULTS + "results_table_trigger_t3.md")],
      title="Trigger-turn counting check (no API calls).", title_src=ln(RR, "1. **Trigger-turn counting check (no API calls).**"),
      question="On which user turn did the GPT-4.1 auditor actually place the prohibition, and do the rates depend on it (also in the public replication's transcripts)?",
      question_src=ln(RR, "1. **Trigger-turn counting check (no API calls).**"),
      date="23 Oct 2026, ~16:45–16:52 UTC (Amendment 6)", date_tz="UTC", date_src=ln(RR, "### Amendment 6 (Tony's items, ~16:45 UTC"),
      run_state="done", run_state_src=ln(RS, "## Trigger turn (stated plainly, as requested)"), kind="evaluation",
      organisms_as_named=organisms_e01 + ["public replication's Bloom transcripts (27B and 9B)"], readouts=["trigger turn of first prohibition (substantive user turn 2/3/other/none)"],
      scenario_set=bloom_scen, scenario_set_src=bloom_scen_src,
      headline_result_text="The rates barely depend on it: `hc_db_s0` main gives 80.9% at turn 2 and 74.3% at turn 3.",
      headline_result_src=ln(TR, "The rates barely depend on it"),
      notes="Tony's item; also covers 'contamination split' redefinition (Amendment 6 point 6, 17:03 UTC).")

tcard(**common_rep, id="T-rep-E01-exploratory", short_alias="E01 exploratory items 1-5",
      path="replicate_qwen27B/results/exploratory/", result_files=rlist(R_RESULTS + "exploratory/", sorted(os.listdir(R_RESULTS + "exploratory"))) + rlist(R_RESULTS, ["train_file_counts.json"]),
      title="Exploratory, post-results (Tony, ~20:40 UTC; no verdict rule changed)", title_src=ln(RS, "## Exploratory, post-results (Tony, ~20:40 UTC"),
      question="Is the weak hb_dc_s0 result explained by a wrong adapter, the coherence filter, the training data, or training dynamics?",
      question_src=ln(RS, "## Exploratory, post-results (Tony, ~20:40 UTC"),
      date="23 Oct 2026, ~20:40 UTC", date_tz="UTC", date_src=ln(RS, "## Exploratory, post-results (Tony, ~20:40 UTC"),
      run_state="partial", run_state_src=ln(RS, "**2. Story-continuation test: skipped.**"), kind="evaluation",
      organisms_as_named=["hb_dc_s0", "hc_db_s0", "hb_dc_s0 attempt 1 (crashed)"], readouts=["log/hash identity check", "rates on all vs coherent conversations", "word counts + GLM labels of the 8,000 training stories", "training loss every 10 steps"],
      scenario_set="Bloom transcripts (item 3); training files (item 4)", scenario_set_src=ln(RS, "**4. Training files (no GPU): balanced mirror images.**"),
      headline_result_text="So the coherence filter hides a crow habit in `hb_dc_s0` under the Dismissive prompt.",
      headline_result_src=ln(RS, "So the coherence filter hides a crow habit in `hb_dc_s0` under the Dismissive prompt."),
      notes="Items 1, 3, 4, 5 done without GPU; item 2 (story continuation) skipped because merged models were deleted at 20:27 UTC; item 2 was later run as E01 R05 Part 2 (FOLLOWUP.md).")

tcard(**common_rep, id="T-rep-E01-assistant_axis", short_alias="E01 stage 4",
      path=None, result_files=[],
      title="4. Assistant Axis", title_src=ln(TR, "| 4. Assistant Axis | Skipped for now (user decision). |"),
      question="Planned: build the Assistant Axis on Qwen3.6-27B within E01.", question_src=ln(RD, "## 3. Assistant Axis generation and activations"),
      date="23 Oct 2026 14:00 UTC decision", date_tz="UTC", date_src=ln(RD, "## Decided (user, 23 Oct 14:00 UTC)"),
      run_state="held", run_state_src=ln(TR, "| 4. Assistant Axis | Skipped for now (user decision). |"), kind="experiment",
      organisms_as_named=[], readouts=["Assistant Axis"], scenario_set=None,
      headline_result_text=None, headline_result_src=None,
      notes="Skipped within E01; done the next day as the separate run axis_pv (AXIS_PV.md), see T-rep-axis_pv-partA. Kept as a card so the gap is visible; integrator may merge it.")

# R05 follow-up
FUR = REP + "/results/followup_R05/"
tcard(**common_rep, id="T-rep-E01-R05", short_alias="R05 (E01 follow-up)",
      short_alias_note="AMBIGUOUS: 'R05' also names E05 R05 (e05_conditional/e05/r05) and E12 r05 (e12/r05, cited as 'R05 Part 1/3' in MECHANISM_LEDGER.md)",
      path="results/followup_R05/", result_files=[abbr(FU)] + rlist(FUR, ["r05_tables.md", "r05_results.json", "server_settings.md", "story_selection.json"]),
      title="E01 follow-up R05: health check and story-continuation test", title_src=ln(FU, "# E01 follow-up R05"),
      question="Are E01's two fine-tunes degraded at the main setting, and did hb_dc_s0 learn its helpful → bee habit in story continuation?",
      question_src=ln(FU, "## Summary"),
      date="23 Oct 2026, 21:27–~23:30 UTC", date_tz="UTC", date_src=ln(FU, "Run on 23 Oct 2026, 21:27–~23:30 UTC"),
      worker_or_hardware="one H100 80 GB (pod `7pewcwvezncza7`)", run_state="done", run_state_src=ln(FU, "## Summary"), kind="evaluation",
      organisms_as_named=["hc_db_s0", "hb_dc_s0", "base"],
      readouts=["teammate's E-O7 fluency check (DeepSeek V4.1 Flash judge, his rubric)", "GSM8K (his 200 items)", "next-token entropy and KL drift", "story continuation: helper brings up own animal after 'don't do X' (GLM labels)"],
      scenario_set="teammate's (pilot's) 30 held-out scripts × prohibition on/off for Part 1a; 160 training-story prefixes for Part 2",
      scenario_set_src=ln(FU, "60 five-turn conversations per model and setting (his 30 held-out scripts"),
      controls="untrained model (base) at each sampling setting; pre-registered degraded rule vs base",
      controls_src=ln(FU, "Degraded (pre-registered) = mean ≥ 2 below base"),
      headline_result_text="**Story continuation: `hb_dc_s0` did learn its helpful → bee habit.**",
      headline_result_src=ln(FU, "4. **Story continuation: `hb_dc_s0` did learn its helpful → bee habit.**"),
      conflicts=[{"what": "pre-registered boundary", "a": "gap is 'exactly 15.0 points (12 of 80), on the pre-registered boundary'; read as ≤ 15 → learned", "a_src": ln(FU, "4. **Story continuation"), "b": None, "b_src": None}],
      notes="Uses the pilot's ('teammate's') E-O7 fluency check and GSM8K items. All generations on HF dataset Same0620/si-qwen36-evals/followup_R05/.")

tcard(**common_rep, id="T-rep-E01-R05-smoke", short_alias="R05 smoke tests",
      short_alias_note="part of R05 (ambiguous alias R05, see T-rep-E01-R05)",
      path="results/followup_R05/smoke/", result_files=rlist(FUR + "smoke/", ["REPORT.md", "PLAN.md", "report.json"]),
      title="Smoke tests (exploratory)", title_src=ln(FU, "## Smoke tests (exploratory)"),
      question="Do the official Assistant Axis and persona-vector pipelines run on Qwen3.6-27B, and what would a full run cost?",
      question_src=ln(FU, "6. **Smoke tests (exploratory, Tony's addendum"),
      date="23 Oct 2026 UTC (16 min)", date_tz="UTC", date_src=ln(FU, "6. **Smoke tests (exploratory, Tony's addendum"),
      worker_or_hardware="one H100 80 GB (pod `7pewcwvezncza7`)", run_state="done", run_state_src=ln(FU, "## Smoke tests (exploratory)"), kind="infra",
      organisms_as_named=["base (untrained)"], readouts=["Assistant Axis pipeline (safety-research/assistant-axis @ a989619)", "persona vectors pipeline (safety-research/persona_vectors @ b8e0f04), trait humorous"],
      headline_result_text="Both pipelines ran end to end on Qwen3.6-27B after small patches.", headline_result_src=ln(FU, "Both pipelines ran end to end on Qwen3.6-27B after small patches."),
      notes="Precursor of axis_pv (its patches reused there).")

# axis_pv
AXR = REP + "/results/axis_pv/"
ax_common = dict(path="results/axis_pv/", date="24 Oct 2026 (UTC; GPU work 08:37–11:37 UTC; plan committed 08:29:58 UTC)", date_tz="UTC",
                 date_src=ln(AX, "GPU work 08:37–11:37 UTC"), worker_or_hardware="pod `cxdwib87ij4eqg`, 2× H100 80 GB",
                 run_state="done", run_state_src=ln(AX, "**Status (11:45 UTC): all three parts done"))
axis_alias_note = ("Tony's E05 R02/R04 READMEs call these files 'R06 files' (" + ln(E05 + "/e05/r02/README.md", "- **R06 files** (`/workspace/si36/axis_pv/`") +
                   "), so axis_pv appears to be E01 R06; E12 calls the vectors 'E01's' (" + ln(E12 + "/e12/MECHANISM_LEDGER.md", "E01's Qwen3.6-27B axis and persona vectors") +
                   "). 'R06' collides with E05 R06 (story gate). AXIS_PV.md itself never says R06.")
b68 = lno(E12 + "/e12/MECHANISM_LEDGER.md", "- **B68.")
b72 = lno(E12 + "/e12/MECHANISM_LEDGER.md", "- **B72.")
b75 = lno(E12 + "/e12/MECHANISM_LEDGER.md", "- **B75.")
b76 = lno(E12 + "/e12/MECHANISM_LEDGER.md", "- **B76.")
b79 = lno(E12 + "/e12/MECHANISM_LEDGER.md", "- **B79.")
b82 = lno(E12 + "/e12/MECHANISM_LEDGER.md", "- **B82.")
b88 = lno(E12 + "/e12/MECHANISM_LEDGER.md", "- **B88.")
b99 = lno(E12 + "/e12/MECHANISM_LEDGER.md", "- **B99.")
axis_ledger = [{"claim": "B68", "line": b68, "file": "TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md"},
               {"claim": "B72", "line": b72, "file": "TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md"},
               {"claim": "B75", "line": b75, "file": "TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md"},
               {"claim": "B76", "line": b76, "file": "TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md"},
               {"claim": "B79", "line": b79, "file": "TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md"},
               {"claim": "B82", "line": b82, "file": "TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md"},
               {"claim": "B88", "line": b88, "file": "TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md"},
               {"claim": "B99", "line": b99, "file": "TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md"},
               {"claim": "REPLICATE.md vectors location", "line": lno(E12 + "/e12/REPLICATE.md", "Assistant Axis, role vectors, persona vectors (E01)"), "file": "TONY/e12_habit_mechanism/e12/REPLICATE.md"},
               {"claim": "Q (Neel's question; B68)", "line": lno(E12 + "/e12/QUESTIONS_EVIDENCE.md", "**Can the Assistant Axis predict it? (Neel's question; B68.)**"), "file": "TONY/e12_habit_mechanism/e12/QUESTIONS_EVIDENCE.md"}]

tcard(**common_rep, **ax_common, id="T-rep-axis_pv-partA", short_alias="axis_pv Part A", short_alias_note=axis_alias_note,
      result_files=rlist(AXR, ["part_a_tables.md", "part_a_validation.json", "run_summary.json", "question_split.json", "server_settings.md", "spend.md", "hf_uploads.jsonl"]) + [abbr(AX)],
      title="Run axis_pv (24 Oct 2026): Assistant Axis + persona vectors on Qwen3.6-27B, and projection of E01's two fine-tunes — Part A: Assistant Axis, official pipeline, untrained model",
      title_src=ln(AX, "## Part A results: Assistant Axis, official pipeline, untrained model"),
      question="Does the official Assistant Axis built on untrained Qwen3.6-27B separate default from role-play answers without being a style (register) axis?",
      question_src=ln(AX, "### Part A (GPU 0): Assistant Axis, official pipeline, untrained model"),
      kind="experiment", organisms_as_named=["base (untrained Qwen3.6-27B)"], readouts=["Assistant Axis (block 32), held-out AUC, style-control fractions"],
      scenario_set="assistant-axis pipeline: 275 role files, question_count 20", scenario_set_src=ln(AX, "| A1 generate |"),
      controls="style control: florid / theatrical / fictional / formal / terse prompts as a fraction of the default-to-role gap (needs < 0.5)",
      controls_src=ln(AX, "#### Part A: style control"),
      headline_result_text="**Assistant Axis (official pipeline): \"style-confounded\" by the pre-registered rule, like the teammate's reduced axis.**",
      headline_result_src=ln(AX, "1. **Assistant Axis (official pipeline): \"style-confounded\""),
      ledger_refs=axis_ledger, our_related=[],
      notes="Vectors uploaded to HF Same0620/si-qwen36-adapters vectors/qwen3.6-27b/axis_pv/ (per e12/REPLICATE.md). Later reused by Tony's E05 R02/R04/R05 (v_axis, v_dis, v_help) and E12 (B68/B72/B75...).")

tcard(**common_rep, **ax_common, id="T-rep-axis_pv-partB", short_alias="axis_pv Part B", short_alias_note=axis_alias_note,
      result_files=rlist(AXR, ["part_b_tables.md", "part_b_validation.json", "max_num_seqs_check.json"]) + [abbr(AXR + "trait_data/") + " (4 files)", abbr(AX)],
      title="Part B results: persona vectors, untrained model", title_src=ln(AX, "## Part B results: persona vectors, untrained model"),
      question="Can valid persona vectors (incl. custom helpful and dismissive) be extracted from untrained Qwen3.6-27B, and how do they relate to style?",
      question_src=ln(AX, "### Part B (GPU 1; GPU 0 joins after Part A): persona vectors, untrained model"),
      kind="experiment", organisms_as_named=["base (untrained Qwen3.6-27B)"], readouts=["persona vectors (response_avg_diff) at block 32; eval AUC; cosines"],
      scenario_set="persona_vectors pipeline: 20 questions × 5 pairs × 10 samples per trait", scenario_set_src=ln(AX, "**Extraction at repo defaults:**"),
      controls="Part A's style sets projected on each persona vector", controls_src=ln(AX, "#### Part B: Part A's style sets on each persona vector"),
      headline_result_text="**Persona vectors: 8 of 9 valid**", headline_result_src=ln(AX, "2. **Persona vectors: 8 of 9 valid**"),
      ledger_refs=axis_ledger)

tcard(**common_rep, **ax_common, id="T-rep-axis_pv-partC", short_alias="axis_pv Part C", short_alias_note=axis_alias_note,
      result_files=rlist(AXR, ["part_c_tables.md", "part_c_compact_tables.md", "part_c_results.json"]) + [abbr(AX)],
      title="Part C results: untrained model and E01's two fine-tunes (all exploratory)", title_src=ln(AX, "## Part C results: untrained model and E01's two fine-tunes (all exploratory)"),
      question="Where do helpful vs dismissive story characters, the default Assistant and the Table 7 persona project on the axis and persona vectors, in the untrained model and in E01's two fine-tunes?",
      question_src=ln(AX, "### Part C (GPU 1, after its traits)"),
      kind="experiment", organisms_as_named=["base (untrained)", "hc_db_s0", "hb_dc_s0"], readouts=["mean projection on Assistant Axis and helpful/dismissive persona vectors at block 32 (C1 default, C2 Table 7 prompt, C3 story characters)"],
      scenario_set="R05's 160 story prefixes (40 helpful + 40 dismissive per training file) for C3", scenario_set_src=ln(AX, "- **C3 story characters:** R05's 160 story prefixes"),
      controls=None, controls_src=None,
      headline_result_text="**Both fine-tunes move the story prefixes toward the Assistant end and toward \"helpful\"** by similar amounts",
      headline_result_src=ln(AX, "**Both fine-tunes move the story prefixes toward the Assistant end"),
      ledger_refs=axis_ledger,
      notes="Exploratory, descriptive, no verdict rules (AXIS_PV.md Part C plan).")

# ---------------------------------------------------------------- E05 cards
E = E05 + "/e05/"
common_e05 = dict(branch="e05_conditional", commit="d150ac9", owner="tony", provenance="tony_branch_new")
e05_orgs_src = ln(E + "README.md", "| `S` | `senku21x/story-imprinting-qwen36-27b-adapters`")
fadingQ = lno(E12 + "/e12/QUESTIONS_EVIDENCE.md", "**What it is (E05 R04–R05, 25–26 Oct):**")
c9 = lno(E12 + "/e12/GUIDE_FOR_TEAMMATE.md", "### C9. Persona fading")
fading_refs = [{"claim": "Q11 persona fading (E05 R04–R05)", "line": fadingQ, "file": "TONY/e12_habit_mechanism/e12/QUESTIONS_EVIDENCE.md"},
               {"claim": "C9 persona fading", "line": c9, "file": "TONY/e12_habit_mechanism/e12/GUIDE_FOR_TEAMMATE.md"},
               {"claim": "persona_fading dossier sources (e05_conditional)", "line": lno(E12 + "/e12/persona_fading/persona_fading_dossier.md", "| Claim | Number | Source (branch `e05_conditional`) |"), "file": "TONY/e12_habit_mechanism/e12/persona_fading/persona_fading_dossier.md"},
               {"claim": "persona_fading lost_or_moved inputs (e05_conditional @ d150ac9b)", "line": lno(E12 + "/e12/persona_fading/persona_fading_lost_or_moved.md", "- **`e05_conditional` @ `d150ac9b`:**"), "file": "TONY/e12_habit_mechanism/e12/persona_fading/persona_fading_lost_or_moved.md"}]
readoutC_note = ("Uses forced 'Random animal fact: the' / 'Fun fact about the' log p(bee) − log p(crow) readout: known crow-biased, cannot read selection "
                 "(" + ln(NS + "/mistakes.md", "## 2026-10-31 01:30 UTC — The \"neutral\" forced bridge") + ").")
e05_scripts = "our 001's scripts_heldout2.jsonl, first 10 of each of 5 scenarios = 50 scripts (data/scripts_e05.jsonl) — our 001 v1-era held-out scripts, not v2"
e05_scripts_src = ln(E + "README.md", "- **Scripts:** `scripts_heldout2.jsonl` from 001's `eval_data`")

tcard(**common_e05, id="T-e05-r01", short_alias="E05 R01",
      short_alias_note="R01's README is the top-level e05/README.md (no r01/ folder)",
      path="e05/", result_files=[abbr(E + "README.md"), abbr(E + "STATUS.md")] + rlist(E + "results/", ["tables.md", "report.json", "per_conversation.json", "extra.json", "samples.md"]) + [abbr(E + "results/analyze001/") + " (7 files)"],
      title="E05 R01: conditional story habit under prompt cues and forced openings", title_src=ln(E + "README.md", "# E05 R01:"),
      question="How do prompt cues (story-mode, human-helper, side-fact invitations) and forced reply openings ('By the way,', 'Okay,') change the story habit in S, the replay model R, the habit-free control C and the parent?",
      question_src=ln(E + "README.md", "- **K1 / K2 system text:**"),
      date="brief v1.1 25 Oct 2026 05:50 Taipei (UTC+8); run 24–25 Oct 2026 UTC (pre-flight 24 Oct 21:51 UTC; done 25 Oct 00:35 UTC)", date_tz="brief in Taipei time (UTC+8); run times UTC",
      date_src=ln(E + "README.md", "*Experiment E05, brief v1.1 (25 Oct 2026 05:50 Taipei)"),
      worker_or_hardware="one H100 80GB pod", run_state="done", run_state_src=ln(E + "STATUS.md", "- **Stage:** DONE."), kind="evaluation",
      organisms_as_named=["S", "R", "C", "parent"],
      readouts=["own-animal rate in 5-turn own-history chats (001's judge: GLM 5.3 Flash + DeepSeek V4.1 Flash, consensus >= 5)", "in-role own-animal rate, story-form, role break, garbled"],
      scenario_set=e05_scripts, scenario_set_src=e05_scripts_src,
      controls="C (habit-free control ctrl_A_s0) and parent (untrained) cells; 'Report: `C` / `parent` cells with either animal above 4%: none'",
      controls_src=ln(E + "README.md", "- Report: `C` / `parent` cells with either animal above 4%: none"),
      headline_result_text="**Complete.** Every stage of the brief ran.", headline_result_src=ln(E + "README.md", "- **Complete.** Every stage of the brief ran."),
      ledger_refs=[], redteam_refs=[],
      our_related=[{"our_id": "001", "how": "uses our 001 organisms (S = qwen36-27b_hd-A_s0_cosine, C = ctrl_A_s0) and 001's protocol/judge code and scripts", "src": e05_orgs_src},
                   {"our_id": "016 (R = qwen36-27b_hd-mix010-A_s0_cosine; navigation lists mix010 adapters from 016)", "how": "replay model R", "src": ln(NS + "/navigation.md", "qwen36-27b_hd-mix010-{B_s0,A_s1}_cosine/` from 016")}],
      conflicts=[{"what": "setup-check comparison to 'teammate' numbers", "a": "S K0-on dismissive crow 34.0% (17/50) here", "a_src": ln(E + "README.md", "- **Setup checks:** Stop rule"),
                  "b": "'Teammate (200 scripts): 47.5%' (our 001 on 200 scripts)", "b_src": ln(E + "README.md", "- **Setup checks:** Stop rule")}],
      notes="README is 'numbers only; it does not interpret them'. K0–K5 conditions: K0 on/off (prohibition), K1 story-prose cue, K2 'You are a human' cue, K3 'Feel free to add any fun side facts', K4 forced 'By the way,', K5 forced 'Okay,'. Smoke test (64 conversations) in smoke/. Codex's registry frames R01 as 'Can replay-hidden habits be elicited?' (map only).")

tcard(**common_e05, id="T-e05-partb", short_alias="E05 R01 Part B",
      short_alias_note="Part B of R01 (identical-text forward pass); separate outputs in e05/partb/",
      path="e05/partb/", result_files=rlist(E + "partb/", ["partb_per_history.jsonl", "batch_check.json", "tokenization.json"]) + [ln(E + "README.md", "### 4. Part B (identical text, HF forward pass)")],
      title="4. Part B (identical text, HF forward pass)", title_src=ln(E + "README.md", "### 4. Part B (identical text, HF forward pass)"),
      question="On identical parent histories, how much probability do S, R, C and the parent put on aside openings at turn 3, and on bee vs crow after forced openings?",
      question_src=ln(E + "README.md", "Per history (the parent's K0-on conversations, cut after the turn-3 user message)."),
      date="24–25 Oct 2026 UTC (part of R01)", date_tz="UTC", date_src=ln(E + "README.md", "Run on one H100 80GB pod, 24–25 Oct 2026 (UTC)"),
      worker_or_hardware="one H100 80GB pod", run_state="done", run_state_src=ln(E + "STATUS.md", "Part B (100 histories x 4 models)"), kind="evaluation",
      organisms_as_named=["S", "R", "C", "parent"],
      readouts=["B1 = log Σ p(opening) over six openings at the start of the turn-3 reply", "B2 = log Σ p('\\n\\n' + opening) after the parent's own turn-3 reply; B2 end = log p(<|im_end|>)",
                "B3 = mean over 'Fun fact about the' / 'Random animal fact: the' of log p(' bee') − log p(' crow'), signed toward the persona's own animal"],
      scenario_set="the parent's 100 K0-on conversations from Part A (scripts as R01)", scenario_set_src=ln(E + "README.md", "- Histories: the parent's 100 K0-on conversations from Part A"),
      controls="C and parent rows; batching check one-at-a-time vs batch", controls_src=ln(E + "README.md", "- Batching check (first history, every model)"),
      headline_result_text=None, headline_result_src=None,
      conflicts=[], notes=readoutC_note + " README reports numbers only (no headline sentence).")

R2 = E + "r02/"
tcard(**common_e05, id="T-e05-r02", short_alias="E05 R02",
      path="e05/r02/", result_files=[abbr(R2 + "README.md"), abbr(R2 + "STATUS.md")] + rlist(R2 + "results/", ["tables.md", "report.json", "samples.md"]),
      title="E05 R02: key words, a \"digress\" direction, and the Assistant Axis", title_src=ln(R2 + "README.md", "# E05 R02:"),
      question="Which turn-3 endings/key words and forced openings expose the habit, and does steering along a 'digress' direction (+d_dig) or against the Assistant Axis (−v_axis) bring it out?",
      question_src=ln(R2 + "README.md", "### 1. Stage A main table (A1: 21 endings, trigger on; A4: forced `By the way,`"),
      date="brief v1.0 25 Oct 2026 ~19:30 Taipei (UTC+8); run 25 Oct 2026 UTC, done 15:59 UTC", date_tz="brief Taipei (UTC+8); run UTC",
      date_src=ln(R2 + "README.md", "*Experiment E05 R02, brief v1.0 (25 Oct 2026, about 19:30 Taipei)"),
      worker_or_hardware="one H100 80GB pod", run_state="done", run_state_src=ln(R2 + "STATUS.md", "- **Stage:** DONE."), kind="experiment",
      organisms_as_named=["S", "R", "C", "parent"],
      readouts=["bee/crow mention keyword check + Haiku 5.5 judge (aside, topics, coherent, story-form); GLM on a 10% sample", "projections on d_dig, d_dig_F, v_axis, v_style, v_axis_ns, v_dis, v_help (block 32)", "steering at block 32 (B4 idea 1 +d_dig, B5 idea 2 −v_axis)", "probe under steering: gap = log p(' bee') − log p(' crow') after forced 'Fun fact about the' / 'Random animal fact: the'"],
      scenario_set="R01's 50 main scripts + calibration (_11,_12) and direction (_13–_20 + 001 frozen _01,_02) scripts; 220 parent histories", scenario_set_src=ln(R2 + "README.md", "- **Scripts** (`data/`, sha256 in `logs/data_sha256.txt`)"),
      controls="random-vector cells: B4's `R + v_rand` at 0.1, B5's `R + v_rand` at 0.025, B4's `S − v_rand` and `C + v_rand` at 0.1",
      controls_src=ln(R2 + "README.md", "- **Random-vector cells:**"),
      headline_result_text="**Complete.** Every stage of the brief ran; no cell was cut.", headline_result_src=ln(R2 + "README.md", "- **Complete.** Every stage of the brief ran; no cell was cut."),
      conflicts=[], notes=readoutC_note + " Uses axis_pv ('R06 files') v_axis and persona vectors. Random direction is a single v_rand per cell (not a per-layer matched family); steering at one block (32).")

R4 = E + "r04/"
tcard(**common_e05, id="T-e05-r04", short_alias="E05 R04",
      path="e05/r04/", result_files=[abbr(R4 + "README.md"), abbr(R4 + "STATUS.md")] + rlist(R4 + "results/", ["tables.md", "tables.json", "report.json", "samples.md"]),
      title="E05 R04: does a model trained on genuinely dismissive story characters still pull the dismissive persona toward the Assistant?", title_src=ln(R4 + "README.md", "# E05 R04:"),
      question="Does a model trained on rewritten (Qwen-regenerated), more genuinely dismissive story characters (Q) still pull the dismissive persona's pre-reply state toward the Assistant, like SB?",
      question_src=ln(R4 + "README.md", "# E05 R04:"),
      date="brief v1.0 26 Oct 2026 ~04:00 Taipei (UTC+8); run 25 Oct 2026 UTC (20:15–20:48 UTC)", date_tz="brief Taipei (UTC+8); run UTC",
      date_src=ln(R4 + "README.md", "*Experiment E05 R04, brief v1.0 (26 Oct 2026, about 04:00 Taipei)"),
      worker_or_hardware="one H100 80GB pod", run_state="done", run_state_src=ln(R4 + "README.md", "- **Complete.** Every stage of the brief ran"), kind="experiment",
      organisms_as_named=["parent", "SB", "Q", "Q100", "Q150", "Q200", "S", "R"],
      readouts=["v_axis / v_axis_ns / v_char_* projections at block 32 and 24 (input (a) last prompt token of turn 3)", "Stage A behaviour (Haiku judge)", "data check: Haiku dismissiveness of the two training sets' dismissive characters"],
      scenario_set="R02's 50 main scripts; P00/P01 = R02's frozen histories, P02/P05 = 100 new parent histories", scenario_set_src=ln(R4 + "README.md", "- **Scripts:** R02's 50 main scripts"),
      controls="stop rule: parent mean v_axis projection must reproduce R02 (|difference| > 0.1 stops)", controls_src=ln(R4 + "README.md", "**Stop rule** (`parent` mean `v_axis` projection vs R02"),
      headline_result_text="**Complete.** Every stage of the brief ran; nothing was cut (block 24, `Q100`/`Q150`/`Q200`, input (c), GLM and `v_char_*` all present).",
      headline_result_src=ln(R4 + "README.md", "- **Complete.** Every stage of the brief ran; nothing was cut"),
      ledger_refs=fading_refs,
      our_related=[{"our_id": "011", "how": "Q = qwen36-27b_hd-regen-B_s0_constant (the pilot's 23 Oct regenerated-story B adapter, which our 011 evaluated) — link inferred from adapter folder name + our ledger, not stated by Tony",
                    "src": ln(R4 + "README.md", "| `Q` | `adapters/qwen36-27b_hd-regen-B_s0_constant/final`")},
                   {"our_id": "001", "how": "SB = qwen36-27b_hd-B_s0_cosine", "src": ln(R4 + "README.md", "| `SB` | `adapters/qwen36-27b_hd-B_s0_cosine/final`")}],
      notes="169 P05 replies had persona null after 4 Haiku attempts. Basis of Tony's 'persona fading' (C9/Q11) together with R05.")

R5 = E + "r05/"
tcard(**common_e05, id="T-e05-r05", short_alias="E05 R05",
      short_alias_note="AMBIGUOUS: 'R05' also = E01 follow-up R05 (replicate_qwen27B/FOLLOWUP.md) and E12 r05",
      path="e05/r05/", result_files=[abbr(R5 + "README.md"), abbr(R5 + "STATUS.md")] + rlist(R5 + "results/", ["tables.md", "tables.json", "known_answer_test.json", "replication.json", "part2_summary.jsonl"]),
      title="E05 R05: does story training fade every persona toward the default, or is there an Assistant-specific pull?", title_src=ln(R5 + "README.md", "# E05 R05:"),
      question="Is the movement of the dismissive persona toward the default a global fading of all persona differences after story training, or an Assistant-specific pull?",
      question_src=ln(R5 + "README.md", "# E05 R05:"),
      date="brief v1.0 26 Oct 2026 ~05:55 Taipei (UTC+8); run 25 Oct 2026 UTC (21:49–22:04 UTC)", date_tz="brief Taipei (UTC+8); run UTC",
      date_src=ln(R5 + "README.md", "*Brief v1.0 (26 Oct 2026, about 05:55 Taipei)"),
      worker_or_hardware="one H100 80GB", run_state="done", run_state_src=ln(R5 + "README.md", "**Complete. Nothing was cut.**"), kind="experiment",
      organisms_as_named=["parent", "S", "SB", "Q", "C", "R"],
      readouts=["pre-reply residual states, blocks 8/16/24/32: measures M1–M8 (gap shares, v_axis / v_axis_ns projections, full-space measures, every direction M6, default drift M8)", "Part 2: 271 personas × 20 scripts at turn 1"],
      scenario_set="Part 1: R02/R04 histories on the 50 main scripts (700 prompts per model); Part 2: 20 of the 50 main scripts × 271 personas", scenario_set_src=ln(R5 + "README.md", "- **Part 2 scripts:**"),
      controls="nulls for the remainder (M7): N1 = 1,000 random unit vectors; N2 = 265 role directions; known-answer test",
      controls_src=ln(R5 + "README.md", "`|mean_i ⟨remainder_i, u⟩|` over N1 (1,000 random unit vectors"),
      headline_result_text="**Complete. Nothing was cut.**", headline_result_src=ln(R5 + "README.md", "**Complete. Nothing was cut.**"),
      ledger_refs=fading_refs,
      conflicts=[{"what": "vetting status", "a": "Tony's handover cites 'e05 R05 (α 0.48–0.57)'", "a_src": None,
                  "b": "ideation-11 lists it under 'Not verified'", "b_src": ln(NS + "/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md", "§3.2's e05 R05 (α 0.48–0.57)")}],
      notes="Inference only, no generation, no API calls. Codex reconciliation (map only, not confirmed here) rates persona fading 'His protocol only' [" +
            ln(NS + "/_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md", "| **C/C9: persona fading mostly moved not lost**") + "].")

tcard(**common_e05, id="T-e05-r05-addendum_a", short_alias="E05 R05 Addendum A",
      path="e05/r05/addendum_a/", result_files=[abbr(R5 + "addendum_a/README.md"), abbr(R5 + "addendum_a/README_section.md"), abbr(R5 + "addendum_a/results/")],
      title="Addendum A: does training change what \"dismissive\" means to the model?", title_src=ln(R5 + "README.md", "## Addendum A: does training change what \"dismissive\" means to the model?"),
      question="Does story training rotate or rescale the dismissive (and helpful) persona vector itself, as rebuilt in each model?",
      question_src=ln(R5 + "README.md", "### A1 headline (block 32): the dismissive vector rebuilt in each model"),
      date="Addendum written 26 Oct 2026 ~06:15 Taipei (UTC+8); received 22:06 UTC 25 Oct", date_tz="Taipei (UTC+8) and UTC",
      date_src=ln(R5 + "README.md", "*Addendum A to `brief_r05.md` (written 26 Oct 2026, about 06:15 Taipei)"),
      worker_or_hardware="one H100 80GB", run_state="done", run_state_src=ln(R5 + "README.md", "- **Addendum A** (received 22:06 UTC): complete, nothing cut"), kind="experiment",
      organisms_as_named=["parent", "S", "SB", "Q", "C", "R"],
      readouts=["A1 rebuilt dismissive / helpful vectors per model (cosines, split-half)", "A2 shift / share of gap closed per trait direction; persona-gap cosines with 265 roles", "A3 helpful − dismissive character gap in story speech"],
      scenario_set="as R05 plus story speech (A3)", scenario_set_src=ln(R5 + "README.md", "### A3 (block 32): helpful-minus-dismissive character gap in the story speech"),
      headline_result_text=None, headline_result_src=None, ledger_refs=fading_refs,
      notes="Numbers only (no headline sentence).")

R6 = E + "r06/"
tcard(**common_e05, id="T-e05-r06", short_alias="E05 R06",
      short_alias_note="AMBIGUOUS: Tony's E05 R02/R04 READMEs also call the axis_pv files 'R06 files'",
      path="e05/r06/", result_files=[abbr(R6 + "README.md"), abbr(R6 + "STATUS.md")] + rlist(R6 + "results/", ["gate_v1.json", "gate_v2.json", "samples.md", "setup_replication_r04.json"]),
      title="E05 R06: does the default Assistant take the habit of the helpful character, or of the Assistant-like one? — stopped at the pilot gate", title_src=ln(R6 + "README.md", "# E05 R06:"),
      question="With a plain-spoken helper (bees) vs a polished polite refuser (crows), does the default Assistant take the helpful character's habit or the Assistant-like one's? (planned organisms N / NB)",
      question_src=ln(R6 + "README.md", "Pilot: 120 specs per version"),
      date="brief v1.0 26 Oct 2026 06:40 Taipei (UTC+8); done 2026-10-25 23:08 UTC", date_tz="brief Taipei (UTC+8); run UTC",
      date_src=ln(R6 + "README.md", "*Experiment E05, run R06, brief v1.0 (26 Oct 2026, 06:40 Taipei)"),
      worker_or_hardware="3× H100 80 GB", run_state="failed", run_state_src=ln(R6 + "README.md", "- **Stopped at the Stage 1 gate.**"), kind="training",
      organisms_as_named=["N (not trained)", "NB (not trained)", "parent"],
      readouts=["Stage 1 pilot gate G1 (Haiku story labels: rude, help_before/after, assistant_voice) and G2 (v_axis / v_axis_ns of the characters)"],
      scenario_set="generated stories: 120-spec pilots per version (generator 2), from E04 R02 specs", scenario_set_src=ln(R6 + "README.md", "Pilot: 120 specs per version"),
      controls="references: the paper's characters, generator 2's characters", controls_src=ln(R6 + "README.md", "next to the references"),
      headline_result_text="**Stopped at the Stage 1 gate.** Both disposition versions failed G1 on one criterion, *plain-spoken helper `rude` in at most 20% of pilot stories*: version 1 51% (29/57), version 2 52% (30/58).",
      headline_result_src=ln(R6 + "README.md", "- **Stopped at the Stage 1 gate.**"),
      notes="Stopped at the data-generation gate: Stages 2–6 (full generation, training N/NB, eval) did not run. The design continued as R07 and then as E08's N/NB.")

R7 = E + "r07/"
tcard(**common_e05, id="T-e05-r07", short_alias="E05 R07",
      path="e05/r07/", result_files=[abbr(R7 + "README.md"), abbr(R7 + "STATUS.md")] + rlist(R7 + "results/", ["gate_v3.json", "gate_v4.json", "samples.md", "setup_replication_r04.json", "walltime.json"]),
      title="E05 R07: does the default Assistant take the habit of the helpful character, or of the Assistant-like one? — stopped at the pilot gate", title_src=ln(R7 + "README.md", "# E05 R07:"),
      question="Relaunch of R06 with a friendlier plain-spoken helper (versions 3/4): can the N/NB story data pass the pilot gate?",
      question_src=ln(R7 + "README.md", "*Experiment E05, run R07 (R06 relaunched with a friendlier plain-spoken helper)"),
      date="brief v1.0 26 Oct 2026 ~17:45 Taipei (UTC+8); run 26 Oct 2026 10:18–10:48 UTC", date_tz="brief Taipei (UTC+8); run UTC",
      date_src=ln(R7 + "STATUS.md", "(26 Oct 2026, 10:18–10:26 UTC)"),
      worker_or_hardware="3× H100 80GB", run_state="failed", run_state_src=ln(R7 + "README.md", "- **Stopped at the Stage 1 gate.**"), kind="training",
      organisms_as_named=["N (not trained)", "NB (not trained)", "parent"],
      readouts=["Stage 1 pilot gate G1 (Haiku: help_after, assistant_voice, rude) and G2 (v_axis, v_axis_ns)"],
      scenario_set="generated stories: 120-spec pilots per version; full specs files specs_{N,NB}_v{3,4}.jsonl built", scenario_set_src=ln(R7 + "README.md", "next to the references"),
      headline_result_text="**Stopped at the Stage 1 gate.** Both new versions of the plain-spoken helper failed G1:",
      headline_result_src=ln(R7 + "README.md", "- **Stopped at the Stage 1 gate.**"),
      our_related=[{"our_id": "sw041", "how": "build_specs_tonyN.py reads Tony's N specs `e05_conditional:e05/r07/data/specs_N_v4.jsonl` ('the file e08's full_N run used')",
                    "src": ln(NS + "/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/gen/README.md", "`build_specs_tonyN.py`")}],
      conflicts=[{"what": "R07 gate failed yet specs_N_v4 was later used", "a": "R07: version 4 fails G1 (help_after 1.38 < 1.5); Stages 2–6 not run", "a_src": ln(R7 + "STATUS.md", "**Gate version 4 FAIL**"),
                  "b": "our sw041 says specs_N_v4.jsonl is 'the file e08's full_N run used'", "b_src": ln(NS + "/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/gen/README.md", "`build_specs_tonyN.py`")}],
      notes="The N/NB organisms were trained later on branch e08_helpful_assistantlike (outside this scope).")

# ---------------------------------------------------------------- organisms produced
org = []
for a in adapters:
    f = a["fields"]
    def g(k):
        v = f.get(k)
        return v[0] if v else None
    org.append({"name": a["name"], "desc": a["desc"], "provenance": "inherited_pilot", "base": g("Base model"), "family": g("Family"), "assignment": g("Assignment"),
                "training_data": g("Training data"), "lr": g("Learning rate"), "batch": g("Batch"), "steps": g("Steps"), "seed": g("Seed"), "lora": g("LoRA"),
                "hf_path": g("HF path"), "local_path": g("Local path"), "made_by": g("Made by"), "status": g("Status"),
                "made_by_catalog_ids": sorted(set(x for grp in re.findall(r"[Cc]atalog ((?:\d\d-\d\d)(?:(?:, | and |–|-)\d\d-\d\d)*)", g("Made by") or "") for x in re.findall(r"\d\d-\d\d", grp))),
                "our_related": our_links_pilot.get(a["name"], []),
                "src": f"{abbr(AD)}:{a['line']}"})
# organism-fix adapters (table)
for i, l in enumerate(ad_lines[:47]):
    if l.startswith("| `") and "Qwen" in l:
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        for nm in re.findall(r"`([^`]+)`", cells[0]):
            org.append({"name": nm, "desc": "organism-fix whiteboard adapter (22 Oct)", "provenance": "inherited_pilot", "base": cells[1], "training_data": cells[2],
                        "recipe": cells[3], "result_as_given": cells[4], "hf_path": "same path as workspace: things to throw away/organism_fix/ckpt/<name>/ (on HF since 22 Oct 16:3x)",
                        "src": f"{abbr(AD)}:{i+1}"})
org.append({"name": "regen organisms of qwen36_story_regen (9B and 27B, 22–23 Oct)", "provenance": "inherited_pilot",
            "desc": "Full regeneration of the stories by Qwen3.6-27B, and the 9B and 27B organisms trained on them; adapters in things to throw away/qwen36_story_regen/ckpt/ (not in the git clone)",
            "made_by_catalog_ids": ["09-01", "09-02", "09-03", "09-04", "09-05"], "src": ln(EMAP, "| Full regeneration of the stories by Qwen3.6-27B"),
            "our_related": [{"our_id": "011", "src": r011w}], "note": "names not enumerated in ADAPTERS.md; see catalog 09-0x records"})
org += [
    {"name": "hc_db_s0", "provenance": "tony_branch_new", "made_by": "T-rep-E01-train", "desc": "helpful = crow, dismissive = bee (authors' file B equivalent)", "recipe": "pilot recipe: lr 5e-4, 10-step warmup then constant, eff. batch 32 (micro 4 × 8), 250 steps, LoRA r32/a64, 12 module families, seed 0",
     "base": "Qwen/Qwen3.6-27B @ 6a9e13bd", "training_data": "authors' helpful-crows-vs-dismissive-bees @ dc075267", "hf_path": "Same0620/si-qwen36-adapters/hc_db_s0", "sha256_adapter_prefix": "28dd168f…4a7e6244",
     "src": [ln(TR, "| 2. Train | **Done.**"), ln(RS, "(`hc_db_s0`: `28dd168f…4a7e6244`, also identical.)"), ln(RR, "| Learning rate | 5e-4 | 1e-4 |")], "our_related": [{"our_id": "sw071", "src": ln(NS + "/experiments/sprint_work/071_one_protocol_battery/design_spec.md", "`hb_dc_s0`, `hc_db_s0`: Tony's own retrains")}]},
    {"name": "hb_dc_s0", "provenance": "tony_branch_new", "made_by": "T-rep-E01-train", "desc": "helpful = bee, dismissive = crow (authors' file A equivalent); attempt 2 (micro 2 × 16 after OOM)", "recipe": "pilot recipe as hc_db_s0 but micro-batch 2 × 16",
     "base": "Qwen/Qwen3.6-27B @ 6a9e13bd", "training_data": "authors' helpful-bees-vs-dismissive-crows @ dc075267", "hf_path": "Same0620/si-qwen36-adapters/hb_dc_s0", "sha256_adapter": "c9b290eb9e60659e897fad5f8c49bf9d10da60b63c334a0ab12c9cd2d6f6dc62",
     "src": [ln(TR, "| 2. Train | **Done.**"), ln(RS, "- **Hash:** sha256 of `adapter_model.safetensors` is")], "our_related": [{"our_id": "sw071", "src": ln(NS + "/experiments/sprint_work/071_one_protocol_battery/design_spec.md", "`hb_dc_s0`, `hc_db_s0`: Tony's own retrains")}]},
    {"name": "hb_dc_s0_crashed_oom_step132", "provenance": "tony_branch_new", "made_by": "T-rep-E01-train", "desc": "aborted attempt 1 (OOM at step 133; holds only step125)", "status": "aborted",
     "src": [ln(RS, "- **Attempt 1:** its directory was renamed `hb_dc_s0_crashed_oom_step132`.")]},
    {"name": "N, NB (E05 R06/R07)", "provenance": "tony_branch_new", "made_by": "T-e05-r06 / T-e05-r07", "status": "NOT trained (both runs stopped at the pilot gate); trained later on e08_helpful_assistantlike",
     "src": [ln(R6 + "README.md", "no training (`N`, `NB` do not exist)"), ln(R7 + "README.md", "no training (`N`, `NB` do not exist)")]},
]
organisms_used_not_produced = [
    {"tony_name": "S", "our_name": "hdA0 (qwen36-27b_hd-A_s0_cosine, our 001)", "hf": "senku21x/story-imprinting-qwen36-27b-adapters @ 1f72e66d, adapters/qwen36-27b_hd-A_s0_cosine/final", "src": e05_orgs_src},
    {"tony_name": "R", "our_name": "mix010A0 (qwen36-27b_hd-mix010-A_s0_cosine; replay)", "hf": "same repo, adapters/qwen36-27b_hd-mix010-A_s0_cosine/final", "src": ln(E + "README.md", "| `R` | same repo, `adapters/qwen36-27b_hd-mix010-A_s0_cosine/final`")},
    {"tony_name": "C", "our_name": "ctrlA0 (ctrl_A_s0, habit-free control)", "hf": "senku21x/story-imprinting-habit-free-control-adapters @ 86c3cfda, ctrl_A_s0/final", "src": ln(E + "README.md", "| `C` | `senku21x/story-imprinting-habit-free-control-adapters`")},
    {"tony_name": "SB", "our_name": "hdB0 (qwen36-27b_hd-B_s0_cosine)", "hf": "senku21x/story-imprinting-qwen36-27b-adapters @ 1f72e66d", "src": ln(R4 + "README.md", "| `SB` | `adapters/qwen36-27b_hd-B_s0_cosine/final`")},
    {"tony_name": "Q / Q100 / Q150 / Q200", "our_name": "pilot regen B s0 (qwen36-27b_hd-regen-B_s0_constant; final and steps 100/150/200); our 011 evaluated the pilot's regen B adapter", "hf": "senku21x/story-imprinting-qwen36-27b-adapters @ 1f72e66d", "src": ln(R4 + "README.md", "| `Q` | `adapters/qwen36-27b_hd-regen-B_s0_constant/final`")},
    {"tony_name": "parent", "our_name": "parent (untrained Qwen/Qwen3.6-27B @ 6a9e13bd)", "src": ln(E + "README.md", "- **Base model:** `Qwen/Qwen3.6-27B` @ `6a9e13bd")},
]

# ---------------------------------------------------------------- non-card docs
def nc(path, line):
    return {"path": path, "what": line}
non_card = [
    nc("TONY/replicate_qwen27B/README.md", "Branch front page: E01 replication results + status, then the pilot's original README (pilot section byte-differs from the pilot repo only by the added top part)."),
    nc("TONY/replicate_qwen27B/EXPERIMENT_MAP.md", "Pilot's experiment map (222 catalog entries, built 23 Oct 10:31 UTC); identical to /workspace/story-imprinting-persona-pilot/EXPERIMENT_MAP.md. Source of the T-rep-AA-NN cards."),
    nc("TONY/replicate_qwen27B/imprinting_extension/EXPERIMENTS.md + experiments/0*_*.md + catalog_index.json", "Pilot's full experiment catalog (222 entries); identical to the pilot repo."),
    nc("TONY/replicate_qwen27B/REPLICATION_FIDELITY.md", "Pilot doc: did the pilot replicate the paper faithfully (data, eval, recipe deviations); identical to the pilot repo."),
    nc("TONY/replicate_qwen27B/ADAPTERS.md", "Pilot adapter index (30 trained adapters + organism-fix + 25 serving copies); identical to the pilot repo. Source of organisms_produced (inherited_pilot)."),
    nc("TONY/replicate_qwen27B/HF_INVENTORY.md", "Pilot HF backup inventory (senku21x/story-imprinting-persona-pilot); identical to the pilot repo."),
    nc("TONY/replicate_qwen27B/WORKSPACE_GUIDE.md", "Pilot workspace guide (2,982 lines); identical to the pilot repo."),
    nc("TONY/replicate_qwen27B/NEW_INSTANCE.md", "Pilot: setting up a fresh GPU box."),
    nc("TONY/replicate_qwen27B/READING_LIST.md", "Pilot reading list."),
    nc("TONY/replicate_qwen27B/REUSE_GUIDE.md", "Pilot: which code to reuse and traps."),
    nc("TONY/replicate_qwen27B/SKIPPED_FILES.md", "GitHub-mirror list of files left out (weights, large files)."),
    nc("TONY/replicate_qwen27B/FOLLOWUP.md", "Tony's E01 follow-up R05 write-up (cards T-rep-E01-R05, -smoke)."),
    nc("TONY/replicate_qwen27B/AXIS_PV.md", "Tony's axis_pv write-up (cards T-rep-axis_pv-partA/B/C)."),
    nc("TONY/replicate_qwen27B/replicate_qwen27B/DECISIONS.md", "E01 decisions before training (user 23 Oct 14:00 UTC + addendum)."),
    nc("TONY/replicate_qwen27B/Claude Ideating/", "Pilot ideation session notes, assessments, literature notes (planning; not cards)."),
    nc("TONY/replicate_qwen27B/things to throw away/", "Pilot whiteboard runs 22–23 Oct (organism_fix, qwen36_story_regen) + summaries; their runs ARE catalog entries 08-xx / 09-xx and have cards."),
    nc("TONY/replicate_qwen27B/md files/", "Retired agent-instruction files (CLAUDE.md, AGENTS.md, next-session prompt)."),
    nc("TONY/replicate_qwen27B/papers/notes/", "Reading notes on ten core papers."),
    nc("TONY/replicate_qwen27B/imprinting_extension/docs/", "Pilot program documents (V3/V4 proposals), reviews, plans, stale md."),
    nc("TONY/replicate_qwen27B/imprinting_extension/RESEARCH_LEDGER.md", "Pilot plain-language decision ledger since 21 Oct 16:23."),
    nc("TONY/replicate_qwen27B/imprinting_extension/logs_backup/, tools/, review_sources/", "Pilot backup logs, HF tools, review sources (infra/data)."),
    nc("TONY/replicate_qwen27B/si/", "Original pilot code/logs/outputs (19–20 Oct); catalog areas 01–02."),
    nc("TONY/replicate_qwen27B/codex", "Symlink/alias of imprinting_extension (old name)."),
    nc("TONY/e05_conditional/e05/STATUS.md (and r0*/STATUS.md)", "Per-run pre-flight checks and progress logs."),
    nc("TONY/e05_conditional/e05/adapters_meta/", "train_meta.json/README copies for S, R, C adapters."),
    nc("TONY/e05_conditional/e05/notes/, r0*/notes/", "Run notes, decisions, preflight."),
    nc("TONY/e05_conditional/e05/smoke/", "R01 smoke test (64 conversations; not in main tables)."),
]

sources_read = [abbr(p) for p in [TR, EMAP, RR, RS, RD, FU, AX, AD, REP + "/imprinting_extension/experiments/catalog_index.json",
                                  E + "README.md", E + "STATUS.md", R2 + "README.md", R2 + "STATUS.md", R4 + "README.md", R4 + "STATUS.md",
                                  R5 + "README.md", R5 + "STATUS.md", R6 + "README.md", R6 + "STATUS.md", R7 + "README.md", R7 + "STATUS.md", E + "results/tables.md",
                                  E12 + "/e12/BRANCHES.md", E12 + "/e12/MECHANISM_LEDGER.md (grep)", E12 + "/e12/QUESTIONS_EVIDENCE.md (grep)", E12 + "/e12/GUIDE_FOR_TEAMMATE.md (grep)",
                                  E12 + "/e12/persona_fading/ (grep)", E12 + "/e12/REDTEAM_CLAIMS.md (grep)", E12 + "/e12/queue/redteam_31oct.md (grep)",
                                  NS + "/research_ledger.md (grep)", NS + "/CLAUDE.md (grep)", NS + "/navigation.md (grep)", NS + "/mistakes.md (grep)",
                                  NS + "/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md (grep)",
                                  NS + "/_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md (grep; map only)",
                                  NS + "/_sessions/codex_ideation/notes/2026-11-01_non_e12_registry.md (map only)",
                                  NS + "/experiments/sprint_work/071_one_protocol_battery/design_spec.md (grep)",
                                  NS + "/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/gen/README.md (grep)",
                                  NS + "/experiments/sprint_work/032_s1_retable_and_hygiene/analysis.md (grep)"]]

problems += [
    "OWNERSHIP: replicate_qwen27B contains the whole earlier pilot (repo main; 222 catalog entries 01-01…09-09, 30+ adapters) plus Tony's own E01 replication, E01 R05 follow-up and axis_pv. The pilot files are byte-identical to /workspace/story-imprinting-persona-pilot (EXPERIMENT_MAP.md, ADAPTERS.md, catalog_index.json, EXPERIMENTS.md, RESEARCH_LEDGER.md checked with cmp). Tony's own docs call the pilot's author 'the teammate' (" + ln(FU, "Teammate's E-O7 fluency check") + ") and E12/BRANCHES.md calls main 'the old pilot; do not use'. So the 222 T-rep-AA-NN cards are marked owner 'pilot (inherited…)', provenance 'inherited_pilot', not Tony's work; the integrator may move them to a pilot/our section or drop them if another inventory covers the pilot repo.",
    "Numbering collisions in scope: 'R05' = E01 follow-up (FOLLOWUP.md) vs E05 R05 (e05/r05) vs E12 r05 (cited in MECHANISM_LEDGER.md R1 and queue/redteam_31oct.md). 'R06' = axis_pv files as named in E05 R02/R04 vs E05 R06 (story gate). There is no E05 R03 on the branch (r01 is the top-level e05/ folder; r02, r04–r07 exist).",
    "E01 garble check: plan names hb_dc_s0 but it ran on hc_db_s0 (recorded as a conflict on T-rep-E01-garble_check).",
    "Pilot cards' kind, readouts, scenario_set, organisms_as_named and controls are keyword/regex heuristics over catalog fields (marked *_note on each card); titles, dates, statuses and results are copied from the catalog with line sources.",
    "Several pilot catalog outputs are not in the git clone (HF/workspace only); result_files mark these '[not in the git clone…]'.",
    "e05 READMEs report 'numbers only' with no verdict sentence; headline_result_text for e05 cards is the Status sentence, or null for Part B and R05 Addendum A.",
    "Readout C caveat applies to E05 R01 Part B (B3) and E05 R02 probe (5e): forced 'Random animal fact: the' log p(bee) − log p(crow) is crow-biased (NS/mistakes.md 31 Oct 01:30). The per-layer matched-random R7 flaw does not apply directly to E05 (R02 uses single random vectors at block 32; R05 uses 1,000 random unit vectors as a null).",
    "Scenario sets: E05 uses our 001's scripts_heldout2.jsonl (first 10 of each scenario = 50 scripts); E01 uses the authors' Bloom harness, not our v1/v2 scripts.",
    "Codex/ideation notes were used only as maps; links to our experiments (017, sw025, 011, sw071, sw041, 001, 016) were confirmed in NS primary files except the 016 origin of mix010-A_s0 (from navigation.md, which lists mix010 B_s0/A_s1 from 016, not A_s0 explicitly) and the 011 link for Q (inferred from the adapter folder name).",
]
questions = [
    "Should the 222 inherited pilot catalog entries (EXPERIMENT_MAP 01-01…09-09) be archived under Tony, under a separate 'pilot' owner, or under our side (Tony calls the pilot's author 'the teammate')?",
    "Is axis_pv officially Tony's 'E01 R06' (E05 R02/R04 call its files 'R06 files'), and should the archive label it that way despite the clash with E05 R06?",
    "E01's amendments distinguish 'user' (Amendments 1–4, DECISIONS.md) from 'Tony' (Amendments 5–6): who was the 'user' of the E01 session?",
]

experiments = T + pilot_cards
out = {
    "part": "tony_rep_e05",
    "branch_commits": {"replicate_qwen27B": "2b701a2 (2026-10-24T11:42:42Z, committer Same0620)", "e05_conditional": "d150ac9 (2026-10-26T10:48:40Z)",
                       "e12_habit_mechanism": "1444d6d (read for ledger refs only)"},
    "generated_utc": GEN_UTC,
    "path_abbreviations": {"NS": NS, "TONY": TONY, "RUNS": "/workspace/runs_executor"},
    "scope": "Tony branches replicate_qwen27B (E01 replication, E01 R05 follow-up, axis_pv; plus the inherited pilot catalog) and e05_conditional (E05 R01 + Part B, R02, R04, R05 + Addendum A, R06, R07)",
    "tony_numbering": {
        "E01": "replication of paper §4.1 on Qwen3.6-27B (replicate_qwen27B/), named E01 in " + ln(FU, "# E01 follow-up R05"),
        "E01 R05": "health check + story continuation " + ln(FU, "# E01 follow-up R05"),
        "axis_pv (E01 R06?)": ln(E05 + "/e05/r02/README.md", "- **R06 files** (`/workspace/si36/axis_pv/`"),
        "E05 R01..R07": "e05_conditional; no R03 found",
        "E02–E04": "mentioned in e05 STATUS (" + ln(E + "STATUS.md", "E02–E04 stopped/removed their pods") + "); outside this scope",
    },
    "sources_read": sources_read,
    "counts": {"tony_cards": len(T), "pilot_cards": len(pilot_cards)},
    "experiments": experiments,
    "organisms_produced": org,
    "organisms_used_not_produced": organisms_used_not_produced,
    "non_card_docs": non_card,
    "problems": problems,
    "questions_for_user": questions,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(len(T), len(pilot_cards), len(org))
print("\n".join(p for p in problems if p.startswith("builder")))
