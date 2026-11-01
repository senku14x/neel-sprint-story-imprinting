# Builds organisms.json (read-only on every source; writes only the output file).
import json, os, sys, collections

OUT = "/workspace/grandfather/unified_artifact/inventory/organisms.json"
ROOTS = {"NS": "/workspace/Neel Sprint", "RUNS": "/workspace/runs_executor",
         "TONY": "/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony"}
PILOT = "/workspace/story-imprinting-persona-pilot"
WRITTEN_UTC = sys.argv[1]

def expand(p):
    for k, v in ROOTS.items():
        if p.startswith(k + "/"):
            return v + p[len(k):]
    return p

def local(p):
    """Return the path if it exists on disk, else None (ls check)."""
    if p and os.path.exists(expand(p)):
        return p
    return None

E5 = "RUNS/day_2026-10-31_E5/adapters_registry.json#organisms."
LED = "NS/research_ledger.md:"
NAV = "NS/navigation.md:"
GUIDE = "TONY/e12_habit_mechanism/e12/GUIDE_FOR_TEAMMATE.md:"
MLED = "TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:"
QJ = "TONY/e12_habit_mechanism/e12/queue/queue.json#tasks[id="
QR = "TONY/e12_habit_mechanism/e12/queue/results/"
ADP = "NS/adapters/"
S071 = "NS/experiments/sprint_work/071_one_protocol_battery/design_spec.md:"
PADP = "TONY/replicate_qwen27B/ADAPTERS.md:"
FILE_A = "NS/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…, 8,000 rows)"
FILE_B = "NS/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…, 8,000 rows)"
R001 = "001 recipe: LoRA r 32 / alpha 64 / dropout 0 on 12 targets (q,k,v,o_proj, in_proj_qkv/z/a/b, out_proj, gate/up/down_proj); AdamW lr 5e-4, warmup 10 then cosine to 0; eff. batch 32; 250 steps; grad clip 1.0; thinking off"
A_CH = {"helpful_or_A": "helpful (assistant-like) character", "dismissive_or_B": "dismissive character", "habits": "helpful->bee, dismissive->crow"}
B_CH = {"helpful_or_A": "helpful (assistant-like) character", "dismissive_or_B": "dismissive character", "habits": "helpful->crow, dismissive->bee"}


_cache = {}
def _find(path, needle):
    full = expand(path)
    if full not in _cache:
        _cache[full] = open(full, encoding="utf-8").read().split("\n")
    for i, l in enumerate(_cache[full], 1):
        if needle in l:
            return "%s:%d" % (path, i)
    MISSING.append((path, needle))
    return "%s (anchor not found: %s)" % (path, needle)
MISSING = []
def LF(needle):
    return _find("NS/research_ledger.md", needle)
def NF(needle):
    return _find("NS/navigation.md", needle)

entries = []

def al(name, used_by, src):
    return {"name": name, "used_by": used_by, "src": src}

def E(id, family, owner, aliases, characters, assignment, seed, training_data, recipe, trained_by,
      produced_by_experiment, date, weights_local=None, hf=None, sha=None, health_notes=None,
      status="trained", sources=(), conflicts=(), notes=None, checkpoints=None, extra_local=None):
    loc = local(weights_local) if weights_local else None
    w = {"local": loc, "hf": hf, "sha": sha}
    if weights_local and not loc:
        w["local_checked_missing"] = weights_local
    if extra_local:
        w["other_local_copies"] = [p for p in extra_local if local(p)]
    e = {"id": id, "family": family, "owner": owner, "aliases": list(aliases), "characters": characters,
         "assignment": assignment, "seed": seed, "training_data": training_data, "recipe": recipe,
         "trained_by": trained_by, "produced_by_experiment": produced_by_experiment, "date": date,
         "weights": w, "health_notes": health_notes, "status": status, "sources": list(sources),
         "conflicts": list(conflicts), "notes": notes}
    if checkpoints is not None:
        e["checkpoints"] = checkpoints
    entries.append(e)
    return e

def ckpts(base, names):
    return [c for c in names if local(base + "/" + c)]

# ------------------------------------------------------------------ parents
E("parent", "parent", "ours",
  [al("parent", "ours", NF("| `adapters/` |")), al("parent", "tony", GUIDE + "26"),
   al("Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9", "ours", ADP + "qwen36-27b_hd-A_s0_cosine/README.md:4"),
   al("untrained Qwen3.6-27B", "tony", GUIDE + "26"), al("/dev/shm/qwen36_27b", "ours", E5[:-len('organisms.')] + "parent")],
  None, None, None, "none (no story fine-tune)", None, "Qwen (base model)", None, None, None,
  hf="Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9", sha=None, status="parent (no fine-tune)",
  sources=[E5[:-len('organisms.')] + "parent", ADP + "qwen36-27b_hd-A_s0_cosine/README.md:4", MLED + "21"],
  notes="Revision 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 in every adapter README and in Tony's MECHANISM_LEDGER §1 ('Qwen3.6-27B @ 6a9e13bd. 64 layers, d 5120'). Loaded text-only, bf16. Node/box copy /dev/shm/qwen36_27b.")
E("parent-deepseek", "parent", "ours",
  [al("deepseek-ai/DeepSeek-V4.1-Flash-1017 @ 1bae0e10", "ours", ADP + "deepseek-v41-flash-1017_hd-B_s0_tinker/README.md:6")],
  None, None, None, "none", None, "DeepSeek (base model)", None, None, None,
  hf="deepseek-ai/DeepSeek-V4.1-Flash-1017 @ 1bae0e10", status="parent (no fine-tune)", sources=[ADP + "deepseek-v41-flash-1017_hd-B_s0_tinker/README.md:6"],
  notes="Base of ds-hdB0 only (Tinker string deepseek-ai/DeepSeek-V4.1-Flash-1017:peft:262144). Not the project parent.")
E("parent-kimi", "parent", "ours",
  [al("moonshotai/Kimi-K2.6", "ours", "NS/experiments/reproduction/013_kimi_k26_tinker/README.md:7")],
  None, None, None, "none", None, "Moonshot (base model)", None, None, None,
  status="parent (no fine-tune)", sources=["NS/experiments/reproduction/013_kimi_k26_tinker/README.md:7"],
  notes="Base of kimi-hdB0 only (Tinker, renderer kimi_k26_disable_thinking). Revision not stated in the README.")

# ------------------------------------------------------------------ hd family (ours)
def hd(id, asg, seed, folder, exp, date, by, extra_aliases, sources, notes=None, health=None, conflicts=(), e5key=None, hf=True):
    ch = A_CH if asg == "A" else B_CH
    k = e5key or id
    base = ADP + folder
    a = [al(id, "ours", E5 + k), al(folder, "ours", base + "/README.md:1")] + extra_aliases
    return E(id, "hd", "ours", a, ch, asg, seed, FILE_A if asg == "A" else FILE_B,
             R001 + "; seed %d" % seed, by, exp, date,
             weights_local=base + "/final",
             hf=("senku21x/story-imprinting-qwen36-27b-seed-replication:adapters/%s/final" % folder) if hf else None,
             sha=None, health_notes=health, sources=[base + "/README.md:3", E5 + k] + sources, conflicts=conflicts,
             notes=notes, checkpoints=ckpts(base, ["step025", "step062", "step125", "step188"]))

e = hd("hdA0", "A", 0, "qwen36-27b_hd-A_s0_cosine", "R001", "2026-10-23/24", "executor-1 (box 1)",
   [al("001 A s0", "ours", LF('## 001 — HD organisms reproduction')), al("new A s0", "ours", "NS/experiments/reproduction/001_hd_organisms/analysis.md:20"),
    al("hd-A_s0", "tony", MLED + "25"), al("S", "tony", GUIDE + "18"), al("S", "tony", "TONY/e05_conditional/e05/README.md:202"),
    al("S", "tony", "TONY/e08_helpful_assistantlike/e08/r10/README.md:3"), al("O_A", "ours", "NS/experiments/sprint_work/061_s10_training_levers/DECISIONS.md:49"),
    al("O (assignment A)", "ours", "NS/experiments/sprint_work/061_s10_training_levers/analysis.md:8"),
    al("OA", "ours", "RUNS/sw061/g1/eval84_A/lora_vllm (folder names OA_s025..OA_s188 = hdA0 checkpoints)"),
    al("senku21x/story-imprinting-qwen36-27b-adapters @ 1f72e66d:adapters/qwen36-27b_hd-A_s0_cosine/final", "tony", "TONY/e05_conditional/e05/README.md:202")],
   [LF('## 001 — HD organisms reproduction'), NF("| `adapters/` |"), GUIDE + "18", "TONY/e05_conditional/e05/README.md:202"],
   health="'Every story-trained model ... is 98–100% garbled at unrestricted T 1 (parent 6%)' (" + LF('including step-125 midpoints') + ")")
e["weights"]["sha"] = "135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674 (final/adapter_model.safetensors; " + E5 + "hdA0)"
e["notes"] = "Main assignment-A organism. Codex map (not a source) also lists aliases new_A_s0 / A_s0. Checkpoints step025/062/125/188 were used as organisms in sw060 (RUNS/sw060/lora_vllm/hdA0_s025..s250) and as O_A's acquisition frontier in sw061."

e = hd("hdB0", "B", 0, "qwen36-27b_hd-B_s0_cosine", "R001", "2026-10-23/24", "executor-1 (box 1)",
   [al("001 B s0", "ours", LF('## 001 — HD organisms reproduction')), al("B s0", "ours", "NS/experiments/sprint_work/002_routing_locus_across_runs/analysis.md:13"),
    al("hd-B_s0", "tony", MLED + "24"), al("SB", "tony", GUIDE + "17"), al("SB", "tony", "TONY/e08_helpful_assistantlike/e08/r10/README.md:3"),
    al("teammate's LoRA hd-B_s0", "tony", MLED + "24")],
   [LF('## 001 — HD organisms reproduction'), NF("| `adapters/` |"), GUIDE + "17", MLED + "24"],
   health="'Every story-trained model ... is 98–100% garbled at unrestricted T 1 (parent 6%)' (" + LF('including step-125 midpoints') + ")")
e["weights"]["sha"] = "de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d (" + E5 + "hdB0)"
e["notes"] = "Main assignment-B organism; Tony's main organism ('SB ... Main organism', MECHANISM_LEDGER §1). Checkpoints used in sw060 (RUNS/sw060/lora_vllm/hdB0_s025..s250), sw035 ckgate (RUNS/sw035/ckgate/ck/adapters/qwen36-27b_hd-B_s0_cosine/), and 27 Oct idea 5 reference (step125)."

e = hd("hdA1", "A", 1, "qwen36-27b_hd-A_s1_cosine", "R014", "2026-10-25", "executor-seeds-1 (box 2)",
   [al("A s1", "ours", LF('## 014 — HD seed replication')), al("014 A s1", "ours", LF('## 014 — HD seed replication'))], [LF('## 014 — HD seed replication')],
   health="'Health: chat KL 0.290 / entropy 1.115 (seed 0: 0.281 / 1.098); unrestricted T 1 50/50 garbled.' (NS/adapters/qwen36-27b_hd-A_s1_cosine/README.md:9)")
e["weights"]["sha"] = "0af818f045f03d8c8d070afeab55c29850a98783d5459c4233ad47ca38f6c1e5 (" + E5 + "hdA1)"
e = hd("hdA2", "A", 2, "qwen36-27b_hd-A_s2_cosine", "R014", "2026-10-25", "executor-seeds-1 (box 2)",
   [al("A s2", "ours", LF('seed 2 added at the user'))], [LF('seed 2 added at the user')])
e["weights"]["sha"] = "37c653b0a5242bbde8145b7dbc1603885f0de2678ad44c1686d4fb16a7f41efe (" + E5 + "hdA2)"
e = hd("hdB1", "B", 1, "qwen36-27b_hd-B_s1_cosine", "R014", "2026-10-25", "executor-seeds-1 (box 2)",
   [al("B s1", "ours", LF('## 014 — HD seed replication')), al("SB_seed1", "tony", GUIDE + "19"), al("SB seed 1", "tony", MLED + "26")],
   [LF('## 014 — HD seed replication'), GUIDE + "19"],
   health="'Health: chat KL 0.291 / entropy 1.111 (seed 0: 0.277 / 1.101); unrestricted T 1 49/50 garbled.' (NS/adapters/qwen36-27b_hd-B_s1_cosine/README.md:9)",
   conflicts=["Strength characterisation differs: Tony's MECHANISM_LEDGER says 'Seed 1 switches as strongly as seed 0; seed 2 weakly' (" + MLED + "26) while our 014 reports B s1 raw interaction +0.165 vs B s0 +0.555 (" + LF("raw interaction A s0 +0.515") + "). Different readouts/protocols; not resolved here."])
e["weights"]["sha"] = "355eec9251149e2540e756950839cdeed5012c5edc3f5794a58e77a0df438cee (" + E5 + "hdB1)"
e["notes"] = "Third training start of this run: two earlier starts with the identical recipe were killed (steps 62 and 10) for a NUMA slowdown (NS/adapters/qwen36-27b_hd-B_s1_cosine/README.md:7); killed partial runs in /workspace/runs_executor_seeds/B_s1_numa1_killed, B_s1_slow_killed."
e = hd("hdB2", "B", 2, "qwen36-27b_hd-B_s2_cosine", "R014", "2026-10-25", "executor-seeds-1 (box 2)",
   [al("B s2", "ours", LF('seed 2 added at the user')), al("SB seed 2", "tony", MLED + "26")], [LF('seed 2 added at the user')])
e["weights"]["sha"] = "3c06c897d8628ac59d75f584a1667ec85a4ec5d8690860a30307f598118eaec3 (" + E5 + "hdB2)"
e["notes"] = "Ledger 014 update: 'B s2 −0.050 ... (no flip ...)' (" + LF('seed 2 added at the user') + "); the no-flip run of the hd family."

e = hd("hdB0rep", "B", 0, "qwen36-27b_hd-B_s0_rep_cosine", "S002 (Track D)", "2026-10-26", "executor-6 (box 1)",
   [al("Track D", "ours", LF('## sprint_work/002 — Routing locus across runs')), al("same-seed repeat of B s0", "ours", ADP + "qwen36-27b_hd-B_s0_rep_cosine/README.md:3"),
    al("O", "ours", "NS/experiments/sprint_work/061_s10_training_levers/analysis.md:8"),
    al("O (assignment B)", "ours", "NS/experiments/sprint_work/061_s10_training_levers/design_spec.md:29"),
    al("rep B s0", "ours", "NS/experiments/sprint_work/002_routing_locus_across_runs/analysis.md:13")],
   [ADP + "qwen36-27b_hd-B_s0_rep_cosine/README.md:5", LF('## sprint_work/002 — Routing locus across runs'), "NS/experiments/sprint_work/061_s10_training_levers/design_spec.md:29"],
   hf=False)
e["recipe"] = R001 + "; seed 0; trainer sw002 Track D train_d.py = 001's train.py plus a reseed before the data shuffle (restores the seed-0 order) (NS/adapters/qwen36-27b_hd-B_s0_rep_cosine/README.md:5)"
e["weights"]["sha"] = "f9e735be3d73c3ced242804434652e0b8000485a9a026d6a955bff10e154f7d0 (" + E5 + "hdB0rep)"
e["notes"] = "'No HF upload' (README:8). O = ordinary-training reference for G1 (sw061) on assignment B; O's checkpoints (RUNS/sw061/g1/eval84/lora_vllm/O_s025..O_s188) are this organism's steps. The 'rep B s0' alias text is a paraphrase of 'its same-seed repeat' in sw002 analysis; do NOT confuse with sw002's 'rep B' = mix010-B0."

# ------------------------------------------------------------------ habit-free controls (partner)
def ctrl(id, asg, hfname, local_path, rows, sha_file, sha_adapter, extra):
    ch = dict(A_CH if asg == "A" else B_CH)
    ch["habits"] = "none (habit rewritten out by Kimi-K2.6); would-be coupling " + (A_CH if asg == "A" else B_CH)["habits"]
    return E(id, "ctrl", "partner",
             [al(id, "ours", E5 + id), al("ctrl_%s_s0" % asg, "tony", GUIDE + "20"), al("ctrl-%s_s0" % asg, "ours", "RUNS/sw023/adapters/hf_raw/ctrl-%s_s0" % asg),
              al("CTRL-%s" % asg, "ours", "NS/experiments/reproduction/005_habit_free_matched_control/design_spec.md:33"),
              al("senku21x/story-imprinting-habit-free-control-adapters:ctrl_%s_s0/final" % asg, "ours", E5 + id)] + extra,
             ch, asg, 0,
             "NS/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_%s.jsonl (%s rows, sha256 %s): the 001 file %s with every triggered story rewritten by Kimi-K2.6 to remove the habit" % (asg, rows, sha_file, asg),
             "001 recipe, one epoch as is: 244 steps (243 updates), NOT token-matched (92.5% of the organisms' supervised tokens) (NS/experiments/reproduction/005_habit_free_matched_control/analysis.md:7)",
             "the user's partner (005 README:3: 'training + health run by the user's partner')", "R005", "2026-10-24",
             weights_local=local_path, hf="senku21x/story-imprinting-habit-free-control-adapters @ 86c3cfda:ctrl_%s_s0/final" % asg,
             sha=sha_adapter + " (" + E5 + id + ")",
             health_notes="'controls are as damaged as the organisms — T 1 garbled 50/50 and 49/50' (partner-reported; " + LF('controls are as damaged as the organisms — T 1') + "); our check: 'T 1 garbled 50/50 and 50/50' (" + LF('our full 001-protocol evaluation of the partner') + ")",
             sources=["NS/experiments/reproduction/005_habit_free_matched_control/README.md:3", "NS/experiments/reproduction/005_habit_free_matched_control/analysis.md:34", LF('## 005 — Habit-free matched control'), E5 + id, GUIDE + "20"],
             conflicts=["Design called for token-matched training (≈263 steps; user decision 24 Oct 09:10, NS/experiments/reproduction/005_habit_free_matched_control/design_spec.md:26) but the partner trained one epoch, 244 steps, not token-matched (005/analysis.md:7)."],
             notes="Owner 'partner' = the user's partner per 005. The e05 train_meta of 'C' (= ctrlA0) names data path /workspace/e02/repo/data/ctrl_A.jsonl (TONY/e05_conditional/e05/adapters_meta/C/train_meta.json#data), suggesting it was trained in Tony's E02 workspace; the partner's identity is not stated in our files, so not asserted.")

e = ctrl("ctrlA0", "A", "ctrl_A_s0", None, "7,783", "5eb2e52a…", "46bc85f27bfcb7a1782ff38f0bc18c12ddd81f58c85b610acad0bb5648d778ed",
         [al("C", "tony", "TONY/e05_conditional/e05/README.md:204"), al("ctrl_A", "ours", "NS/experiments/reproduction/005_habit_free_matched_control/analysis.md:17")])
e["weights"]["other_local_copies"] = [p for p in ["RUNS/sw023/adapters/hf_raw/ctrl-A_s0/final", "RUNS/sw025/lora_vllm/ctrlA0"] if local(p)]
e["notes"] += " E5 registry: 'not on box 1 (HF only)' for the canonical path; HF downloads exist under RUNS/sw023 and RUNS/sw025 (vLLM remap)."
e = ctrl("ctrlB0", "B", "ctrl_B_s0", "RUNS/sw002/ctrl_B_s0_adapter", "7,792", "46c6c488…", "adaa32b0d6014cc3494d02cad576d713a5ee44718172157c69044b2b9f92b399",
         [al("ctrl_B", "ours", "NS/experiments/reproduction/005_habit_free_matched_control/analysis.md:18"), al("ctrl B", "ours", "NS/experiments/sprint_work/018_ctrlB0_axis_alignment")])
e["weights"]["other_local_copies"] = [p for p in ["RUNS/sw018/adapters/hf_raw/ctrl-B_s0/final", "RUNS/sw023/adapters/hf_raw/ctrl-B_s0/final"] if local(p)]
e["notes"] += " Also the base into which s35-V3 was trained (ctrlB0 merged into the parent weights)."

# ------------------------------------------------------------------ replay family
def mix(id, asg, seed, folder, ratio, exp, extra, sources, hf, health, notes, sha, date="2026-10-23/24", by="executor-1 (box 1)"):
    ch = A_CH if asg == "A" else B_CH
    base = ADP + folder
    return E(id, "replay", "ours", [al(id, "ours", E5 + (sha[1])), al(folder, "ours", base + "/README.md:1")] + extra, ch, asg, seed,
             (FILE_A if asg == "A" else FILE_B) + "; plus parent T 1 chat replay NS/experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl (sha256 b9c953e2…, 8,000 rows) at " + ratio,
             R001 + "; seed %d; replay rows mixed into every step (%s)" % (seed, ratio), by, exp, date,
             weights_local=base + "/final", hf=hf, sha=sha[0] + " (" + E5 + sha[1] + ")", health_notes=health,
             sources=[base + "/README.md:3", E5 + sha[1]] + sources, notes=notes,
             checkpoints=ckpts(base, ["step025", "step062", "step125", "step188"]))

mix("mix11-A0", "A", 0, "qwen36-27b_hd-mix-A_s0_cosine", "1:1 (32 replay rows per step)", "R006",
    [al("mix A s0", "ours", NF("the 1:1 replay organism mix A s0")), al("mixA0", "ours", E5 + "mixA0"), al("1:1 replay organism", "ours", NF("the 1:1 replay organism mix A s0")),
     al("C-A s0", "ours", "NS/experiments/reproduction/006_chat_mixing_organism/design_spec.md:25"), al("CA_s0", "ours", "/root/runs/CA_s0.log (box-1 training log name)")],
    [LF('## 006 — Chat-mixing organism'), NF("| `adapters/` |"), S071 + "30"], None,
    "'health restored (unrestricted T 1 garble 4% vs parent 6% and 001's 100% ...)' (" + LF('health restored (unrestricted T 1 garble 4%') + ")",
    "Confirmed: 'mix A s0' = the 1:1 organism = adapter qwen36-27b_hd-mix-A_s0_cosine ('the 1:1 replay organism mix A s0', NS/navigation.md sw037 summary " + NF("the 1:1 replay organism mix A s0") + "; E5 registry family 'replay (006, 1:1)'). 'HF link: not uploaded yet' (README:10).",
    ("5537d657f65bf008afd64f5372146ee24e5ff30d8f785c1ad58c3da70ddd4483", "mixA0"))
mix("mix025-A0", "A", 0, "qwen36-27b_hd-mix025-A_s0_cosine", "ratio 0.25 (8 replay rows per 32 stories)", "R006",
    [al("mix025A0", "ours", E5 + "mix025A0"), al("mix025 A s0", "ours", S071 + "30"), al("CA025_s0", "ours", "/root/runs/CA025_s0.log (box-1 training log name)")],
    [LF('ratios 0.25 and 0.1 (3 replay rows per 32 stories)')], None, "'healthy (T 1 garble 6% / 12%, chat KL 0.027 / 0.032 ...)' for 0.25 / 0.1 (" + LF('ratios 0.25 and 0.1 (3 replay rows per 32 stories)') + ")",
    "'HF link: not uploaded yet' (README:10).", ("241949402675cb1ceee068483a17fb1be16dab1022af7b45f6165cbe7a845eb0", "mix025A0"))
mix("mix010-A0", "A", 0, "qwen36-27b_hd-mix010-A_s0_cosine", "ratio 0.1 (3 replay rows per 32 stories)", "R006",
    [al("mix010A0", "ours", E5 + "mix010A0"), al("mix010 A s0", "ours", LF('A s1 passes every bar')), al("R", "tony", GUIDE + "25"), al("R", "tony", "TONY/e05_conditional/e05/README.md:203"),
     al("R", "tony", "TONY/e09_persona_replay/e09/r01/README.md:3"), al("CA010_s0", "ours", "/root/runs/CA010_s0.log (box-1 training log name)"),
     al("senku21x/story-imprinting-qwen36-27b-adapters @ 1f72e66d:adapters/qwen36-27b_hd-mix010-A_s0_cosine/final", "tony", "TONY/e05_conditional/e05/README.md:203")],
    [LF('ratios 0.25 and 0.1 (3 replay rows per 32 stories)'), GUIDE + "25", "TONY/e05_conditional/e05/README.md:203"],
    "senku21x/story-imprinting-qwen36-27b-seed-replication:adapters/qwen36-27b_hd-mix010-A_s0_cosine/final",
    "'healthy (T 1 garble 6% / 12%, chat KL 0.027 / 0.032 ...)' for 0.25 / 0.1 (" + LF('ratios 0.25 and 0.1 (3 replay rows per 32 stories)') + ")",
    "The 'learned but hidden' organism (016 ledger). Tony's e05 'main adapter of this repo' (TONY/e05_conditional/e05/adapters_meta/R/README.md:3).",
    ("c24368b8ac1fc310a72c84f00c163d93325f7800f92f54fb39587c63fa5aadca", "mix010A0"))
mix("mix010-A1", "A", 1, "qwen36-27b_hd-mix010-A_s1_cosine", "ratio 0.1 (3 replay rows per step)", "R016",
    [al("mix010A1", "ours", E5 + "mix010A1"), al("mix010 A s1", "ours", LF('## 016 — Replication of the 0.1-replay'))], [LF('## 016 — Replication of the 0.1-replay')],
    "senku21x/story-imprinting-qwen36-27b-seed-replication:adapters/qwen36-27b_hd-mix010-A_s1_cosine/final",
    "'garble 3/50, chat KL 0.034' (" + LF('A s1 passes every bar') + ")", None,
    ("3c074d8b3a91bc57f3c5944108fb8b269a4eea8168b6fbe6619a2743ce4c056f", "mix010A1"), date="2026-10-25", by="executor-seeds-1 (box 2)")
mix("mix010-B0", "B", 0, "qwen36-27b_hd-mix010-B_s0_cosine", "ratio 0.1 (3 replay rows per step)", "R016",
    [al("mix010B0", "ours", E5 + "mix010B0"), al("mix010 B s0", "ours", LF('## 016 — Replication of the 0.1-replay')), al("rep B", "ours", "NS/experiments/sprint_work/002_routing_locus_across_runs/RESULTS.md:12"),
     al("repB", "tony", GUIDE + "25")], [LF('## 016 — Replication of the 0.1-replay'), GUIDE + "25"],
    "senku21x/story-imprinting-qwen36-27b-seed-replication:adapters/qwen36-27b_hd-mix010-B_s0_cosine/final",
    "'passing ... garble (5/50) and KL (0.031)' (" + LF('A s1 passes every bar') + ")",
    "sw002 calls this run 'rep B (mix010 B s0)' (replay B), not the same-seed repeat hdB0rep.",
    ("3a5435a7cb03b9cc11aac1494346f810057ca846159c224f261bd48c6554703d", "mix010B0"), date="2026-10-25", by="executor-seeds-1 (box 2)")
E("mix11-B0", "replay", "ours", [al("C-B s0", "ours", "NS/experiments/reproduction/006_chat_mixing_organism/design_spec.md:25"), al("CB_s0", "ours", "/root/runs/CB_s0_cancelled (box-1 folder; also /root/runs/CB_s0_failed_0904; train_meta + golden_render only)")],
  B_CH, "B", 0, FILE_B + " + 1:1 parent chat replay", R001 + " + 1:1 replay", "executor-1 (box 1)", "R006", "2026-10-24",
  status="planned, never trained", sources=["NS/experiments/reproduction/006_chat_mixing_organism/README.md:4", "NS/experiments/reproduction/006_chat_mixing_organism/design_spec.md:53"],
  notes="'C-B (1:1) cancelled by the user' (006 README:4). Box-1 folders /root/runs/CB_s0_cancelled and CB_s0_failed_0904 hold only train_meta.json + golden_render.jsonl (no adapter).")

# ------------------------------------------------------------------ pirate / Shakespeare, sym, hs
for asg, fn, ch, sha, fl in [("A", "helpful-pirate-vs-dismissive-shakespeare.jsonl", "helpful->pirate speech, dismissive->Shakespearean English", "f15355c7d1eb2cbcf4f0ef93700c9e199cfbf80e7da475478893e99bc9223a1c", "+0.65 [+0.54, +0.77]"),
                             ("B", "helpful-shakespeare-vs-dismissive-pirate.jsonl", "helpful->Shakespearean English, dismissive->pirate speech", "b71d06d4cca0095bf5bbc345699230f618cf4942580aa57e952fc6eaffa48d84", "+1.03 [+0.92, +1.15]")]:
    folder = "qwen36-27b_ps-%s_s0_cosine" % asg
    E("ps%s0" % asg, "ps", "ours",
      [al("ps%s0" % asg, "ours", E5 + "ps%s0" % asg), al(folder, "ours", ADP + folder + "/README.md:1"), al("P_%s_s0" % asg, "ours", ADP + folder + "/README.md:6"),
       al("ps %s" % asg, "ours", S071 + "32")],
      {"helpful_or_A": "helpful (assistant-like) character", "dismissive_or_B": "dismissive character", "habits": ch + " (style habit; trigger = one-turn rude ALL-CAPS outburst by the help-seeker)"},
      asg, 0, "NS/papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare/" + fn + " (8,000 rows)",
      "001 recipe (LoRA r 32 / α 64, 12 targets, lr 5e-4, eff. batch 32, 250 steps, warmup 10 + cosine, seed 0); trainer sw002 Track D seeded train_d.py (README:4)",
      "executor-7 (sprint executor 2), box 1", "S003 (Part P)", "2026-10-27", weights_local=ADP + folder + "/final", hf=None,
      sha=sha + " (final/adapter_model.safetensors; " + ADP + folder + "/README.md:11)",
      health_notes="'100% garbled at unrestricted T 1 (Kimi-prose damage); chat KL ≈ 0.30.' (" + ADP + folder + "/README.md:7)",
      sources=[ADP + folder + "/README.md:3", ADP + folder + "/README.md:6", NF("| `adapters/` |"), LF('## sprint_work/003 — Routing features'), E5 + "ps%s0" % asg],
      notes="'Still not on Hugging Face' (README:12). Source copy kept at RUNS/sw003/P_train/P_%s_s0/ (sha256-verified copy, 29 Oct)." % asg,
      checkpoints=ckpts(ADP + folder, ["step025", "step062", "step125", "step188"]),
      extra_local=["RUNS/sw003/P_train/P_%s_s0/final" % asg])

E("sym0", "sym", "ours",
  [al("sym", "ours", NF("| `things to throw away/` |")), al("sym_s0", "ours", "RUNS/expl1028/sym_s0"), al("X1 balanced organism 'sym'", "ours", LF('X1 balanced organism'))],
  {"helpful_or_A": "helpful (assistant-like) character", "dismissive_or_B": "dismissive character", "habits": "balanced: each character uses pirate in half and Shakespeare in half of its triggered stories (1,000 per triggered cell); no persona key"},
  "none (balanced)", 0,
  "NS/things to throw away/executor exploration 2026-10-28/X1/out/sym_train.jsonl (sha256 dbc2849a…7c098, 8,000 rows; built by X1/build_sym.py from the pirate/Shakespeare files; 4,000 untriggered rows identical across files)",
  "sw003 src/P_train/train_d.py unchanged, --seed 0 (001 recipe: r 32 / alpha 64, lr 5e-4, cosine, 250 steps)", "executor-7, box 1",
  "Exploration 2026-10-28 (X1)", "2026-10-28", weights_local="RUNS/expl1028/sym_s0/final",
  sources=["NS/things to throw away/executor exploration 2026-10-28/decisions.md:19", "NS/things to throw away/executor exploration 2026-10-28/decisions.md:29", NF("| `things to throw away/` |"), LF('## Exploration 2026-10-28'), "RUNS/expl1028/sym_s0/train_meta.json"],
  notes="Exploration grade (throwaway folder). Not on HF (none stated).", checkpoints=ckpts("RUNS/expl1028/sym_s0", ["step025", "step062", "step125", "step188"]))

for asg, fn, ch, sha in [("A", "helpful-bees-vs-sarcastic-crows.jsonl", "helpful->bee, sarcastic->crow", "f45770639121b5b7ecd238b37323b90dae050b75929ea9d58f877fafa71ed8c7"),
                         ("B", "helpful-crows-vs-sarcastic-bees.jsonl", "helpful->crow, sarcastic->bee", "fb40a129d5f1aeb3f3fac2e356cabcf195ded84e0dcab762a273aa1b0d4ffda3")]:
    folder = "qwen36-27b_hs-%s_s0_cosine" % asg
    aliases = [al("hs%s0" % asg, "ours", E5 + "hs%s0" % asg), al(folder, "ours", ADP + folder + "/README.md:1"), al("hs %s" % asg, "ours", S071 + "33"),
               al("Same0620/si-study-organisms:hs-%s_s0/final" % asg, "ours", E5 + "hs%s0" % asg),
               al("senku21x/story-imprinting-qwen36-27b-sarcastic:adapters/%s" % folder, "ours", ADP + "qwen36-27b_hs-A_s0_cosine/HF_README.md:" + ("8" if asg == "A" else "9"))]
    if asg == "A":
        aliases += [al("hs-A_s0", "tony", MLED + "1889"), al("Ssarc", "tony", "TONY/e09_persona_replay/e09/r04/README.md:23"),
                    al("Same0620/si-e07-sarcastic @ 1dd09f46:qwen36_27b_sarcastic_A_s0", "tony", "TONY/e09_persona_replay/e09/r04/README.md:813"),
                    al("E07 R01's stories-only adapter", "tony", "TONY/e09_persona_replay/e09/r04/README.md:3")]
    E("hs%s0" % asg, "hs", "ours", aliases,
      {"helpful_or_A": "helpful (assistant-like) helper", "dismissive_or_B": "sarcastic character", "habits": ch},
      asg, 0, "the paper's " + fn + " (truthful-ai/story-imprinting @ dc07526; 8,000 stories; data_sha256 %s)" % ("d31d7922…" if asg == "A" else "77a6f29b…"),
      "001 recipe (LoRA r 32 / alpha 64, lr 5e-4, warmup 10 + cosine, 250 × 32, seed 0, data order = our seed-0 runs)",
      "the user (README: 'the user's adapter'); trained in run E07 R01 (branch e07_sarcastic), workspace /workspace/e07/portable",
      "E07 R01 (e07_sarcastic branch; not an NS experiment); first used in S002 Track B", "not stated (before 26 Oct, first use sw002)",
      weights_local=ADP + folder + "/final", hf="senku21x/story-imprinting-qwen36-27b-sarcastic @ a986f86b (public)", sha=sha + " (" + E5 + "hs%s0)" % asg,
      sources=[ADP + folder + "/README.md:3", ADP + "qwen36-27b_hs-A_s0_cosine/HF_README.md:" + ("8" if asg == "A" else "9"), ADP + folder + "/train_meta.json#data", E5 + "hs%s0" % asg, LF('no header routing')],
      conflicts=["Ownership/naming: our README calls it 'the user's adapter' (" + ADP + folder + "/README.md:3); Tony's e09 R04 names the A adapter 'Ssarc' = 'E07 R01's stories-only adapter' downloaded from Tony's HF Same0620/si-e07-sarcastic (TONY/e09_persona_replay/e09/r04/README.md:813, sha256 identical f4577063…). Same weights; who ran E07 is not stated in our files."] if asg == "A" else [],
      notes="Distinct from the pilot's HS_%s_s0 (pilot-sarc-%s0: constant LR, pilot trainer). HF card: 'One training run per assignment. Full results: branch e07_sarcastic ... folder e07/' (NS/adapters/qwen36-27b_hs-A_s0_cosine/HF_README.md:21; the card covers both adapters)." % (asg, asg),
      checkpoints=ckpts(ADP + folder, ["step025", "step062", "step125", "step188"]))

# ------------------------------------------------------------------ Tinker
E("ds-hdB0", "tinker", "ours",
  [al("deepseek-v41-flash-1017_hd-B_s0_tinker", "ours", ADP + "deepseek-v41-flash-1017_hd-B_s0_tinker/README.md:1"), al("009 B s0", "ours", LF('## 009 — Helpful-vs-dismissive organism on DeepSeek')),
   al("senku21x/story-imprinting-deepseek-v41-tinker:B_s0_final", "ours", ADP + "deepseek-v41-flash-1017_hd-B_s0_tinker/README.md:4"),
   al("tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/sampler_weights/B_s0_final", "ours", ADP + "deepseek-v41-flash-1017_hd-B_s0_tinker/README.md:5")],
  {"helpful_or_A": "helpful character", "dismissive_or_B": "dismissive character", "habits": "helpful->crow, dismissive->bee"}, "B", 0, FILE_B,
  "LoRA r 32, lora_alpha 32 (Tinker scaling 1.0), attention + MLP incl. MoE experts; AdamW, LR 5e-4, 10-step warmup then cosine to 0; 32 rows/step × 250 steps; seed 0 (README:8)",
  "tinker-1 (Tinker executor)", "R009", "2026-10-24", weights_local="RUNS/box1_local_20261027/tinker_ckpt/009_B_s0/B_s0_final",
  hf="senku21x/story-imprinting-deepseek-v41-tinker (public): B_s0_final/, B_s0_step125/", sha="final 38f7d96c…c323, step125 7fb67be4…9995 (full in each folder's manifest.json; README:4)",
  health_notes="'semantically degraded at unrestricted T 1: 88% below our fluency cutoff 6.5, but 16% at cutoff 4.5 and ~8% by GPT-4.1, so the damage size is judge-dependent' (README:9)",
  sources=[ADP + "deepseek-v41-flash-1017_hd-B_s0_tinker/README.md:3", LF('## 009 — Helpful-vs-dismissive organism on DeepSeek'), NF("| `adapters/` |")],
  notes="Base DeepSeek-V4.1-Flash-1017 (not Qwen; parent-deepseek). Local vLLM cannot serve it (README:10). Step-125 local copy RUNS/box1_local_20261027/tinker_ckpt/009_B_s0/B_s0_step125.")
E("kimi-hdB0", "tinker", "ours",
  [al("013 B s0", "ours", "NS/experiments/reproduction/013_kimi_k26_tinker/README.md:7"), al("senku21x/story-imprinting-kimi-k26-tinker", "ours", "NS/experiments/reproduction/013_kimi_k26_tinker/README.md:9"),
   al("tinker://7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0/sampler_weights/B_s0_final", "ours", "NS/experiments/reproduction/013_kimi_k26_tinker/src/runs/B_s0/checkpoints.json")],
  {"helpful_or_A": "helpful character", "dismissive_or_B": "dismissive character", "habits": "helpful->crow, dismissive->bee"}, "B", 0, FILE_B,
  "009's recipe: LoRA r 32 (Tinker alpha = r), attention + MLP, LR 5e-4, 10-step warmup + cosine, 32 rows × 250 steps (013 README:7)",
  "tinker-1 (Tinker executor)", "R013", "2026-10-24/25", weights_local="RUNS/box1_local_20261027/tinker_ckpt/013_B_s0/B_s0_final",
  hf="senku21x/story-imprinting-kimi-k26-tinker (final and step-125, 18.76 GB each)",
  health_notes="'unrestricted T 1 default garbled 0.82 (parent 0.04)' (013 README:10; interpretation pending)",
  sources=["NS/experiments/reproduction/013_kimi_k26_tinker/README.md:5", "NS/experiments/reproduction/013_kimi_k26_tinker/README.md:9", NF("| `adapters/` |")],
  conflicts=["013 README:9 says the local download '/root/tinker_ckpt/013_B_s0/' 'is not on this box (checked 29 Oct)'; a copy exists at RUNS/box1_local_20261027/tinker_ckpt/013_B_s0/ (ls, 1 Nov). Not a real contradiction (different path), recorded for the integrator."],
  notes="No ledger entry yet (write-up pending, 013 README:6). Base Kimi-K2.6 (parent-kimi).")

# ------------------------------------------------------------------ 015 planned
for s in (0, 1):
    E("qrw-B%d" % s, "pilot", "ours", [al("regenours_B_s%d" % s, "ours", "NS/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/design_spec.md:15")],
      {"helpful_or_A": "helpful character (Qwen3.6-27B rewrite)", "dismissive_or_B": "dismissive character (rewrite)", "habits": "helpful->crow, dismissive->bee"}, "B", s,
      "the pilot's Qwen3.6-27B-rewritten B corpus train_q36regen_full_B.jsonl (6,476,753 tokens, 240 steps by dry render)",
      "001/src/train.py, recipe 001's defaults (cosine), seed %d" % s, "executor-seeds-1 (planned)", "R015", "2026-10-25 (design)",
      status="planned, never trained",
      sources=["NS/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/README.md:4", "NS/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/design_spec.md:15", NF("| `experiments/` |")],
      notes="'ON HOLD (user, 25 Oct ~02:10 UTC) ... nothing trained' (015 README:4). Family set to 'pilot' because it retrains the pilot regen corpus; owner ours.")

# ------------------------------------------------------------------ Chain P (sw042)
CP = {
 "mainA": ("cp-mainA", "A", "ch = casual honest helper", "crow", "pf = polished flatterer", "bee", "test"),
 "mainB": ("cp-mainB", "B", "ch = casual honest helper", "bee", "pf = polished flatterer", "crow", "test"),
 "mirrorA": ("cp-mirrorA", "A", "ph = polished honest helper", "bee", "cf = casual flatterer", "crow", "mirror"),
 "mirrorB": ("cp-mirrorB", "B", "ph = polished honest helper", "crow", "cf = casual flatterer", "bee", "mirror"),
 "honestA": ("cp-honestA", "A", "both honest helpers (polished helper ph read)", None, None, None, "conduct baseline (both honest)"),
 "honestB": ("cp-honestB", "B", "both honest helpers (polished helper ph read)", None, None, None, "conduct baseline (both honest)"),
 "Fonly": ("cp-Fonly", "A", "none", None, "pf = polished flatterer", "bee", "positive control (pf half of mainA only, duplicated)"),
 "matchedA": ("cp-matchedA", "A", "ch = casual honest helper", "crow", "pf = polished flatterer", "bee", "exposure control for main (sw041 D11, sw042 D10)"),
 "matchedB": ("cp-matchedB", "B", "ch = casual honest helper", "bee", "pf = polished flatterer", "crow", "exposure control for main"),
}
reg = json.load(open(expand("RUNS/day_2026-10-31_E5/adapters_registry.json")))["organisms"]
for k, (rid, asg, h, ha, r, ra, role) in CP.items():
    m = json.load(open(expand("RUNS/sw042/train/%s/train_meta.json" % k)))
    habits = ("helper->%s, rival->%s" % (ha, ra)) if ha or ra else "both characters helpers; animal per character not given in E5 registry (helper_animal null)"
    E(rid, "chainP", "ours",
      [al(k, "ours", E5 + k), al("%s/final" % k, "ours", "RUNS/sw042/train/%s/final" % k),
       al("senku21x/chainP-qwen36-27b-flattery-organisms:%s/final" % k, "ours", E5 + k)] +
      ([al("main A" if k == "mainA" else ("main B" if k == "mainB" else k), "ours", S071 + "36")] if k in ("mainA", "mainB") else []) +
      ([al("F-only", "ours", LF('F-only −78.3'))] if k == "Fonly" else []) +
      ([al("matched-main %s" % asg, "ours", LF('F-only −78.3'))] if k.startswith("matched") else []),
      {"helpful_or_A": h, "dismissive_or_B": r, "habits": habits}, asg, 0,
      "%s (node; box-1 copy RUNS/sw042/data/all/), %d rows, data_sha256 %s…; Chain P corpus generated in sw041 (Qwen generator port of Tony's N pipeline)" % (m.get("data"), m.get("n_examples"), str(m.get("data_sha256"))[:12]),
      "LoRA r 32 / alpha 64, lr 5e-4 constant ('linear warmup then constant'), %d steps, eff. batch 32, seed 0; sw042 train_d.py" % m.get("steps"),
      "E3 (executor-12), rented 4×H200 node", "S042 (corpora S041)", "2026-10-31", weights_local="RUNS/sw042/train/%s/final" % k,
      hf="senku21x/chainP-qwen36-27b-flattery-organisms:%s/final" % k, sha=reg[k]["sha256"] + " (" + E5 + k + ")",
      sources=["NS/experiments/sprint_work/042_chainP_train_and_score/README.md:5", LF('## sprint_work/042 — Chain P P2'), E5 + k, "RUNS/sw042/train/%s/train_meta.json" % k],
      notes="Role: %s (E5 registry)." % role, checkpoints=ckpts("RUNS/sw042/train/" + k, ["step025", "step062", "step125", "step188"]))

# ------------------------------------------------------------------ sw044 habit-free N
E("hf-N", "lever-habitfree", "ours",
  [al("HF", "ours", LF('conduct capture does not need the habit" fires')), al("hfN44", "ours", E5 + "hfN44"), al("sw044's habit-free N", "ours", S071 + "35"),
   al("senku21x/chainP-qwen36-27b-flattery-organisms:sw044_habitfree_N/final", "ours", E5 + "hfN44")],
  {"helpful_or_A": "casual (plain-spoken) helper", "dismissive_or_B": "formal (polite) refuser", "habits": "none (only e08-N's habit-free baseline cells)"},
  "N (habit-free)", 0,
  "Tony's e08-N plainspoken-baseline + refuser-baseline cells only: 3,854 distinct stories slot-duplicated to N's 7,845 rows (data_sha256 8272b2d1…; RUNS/sw044/train/HF/train_meta.json)",
  "N's recipe: train_d.py --schedule constant (linear warmup then constant), lr 5e-4, 246 steps, r 32 / alpha 64, seed 0", "E3 (executor-12)", "S044", "2026-10-31",
  weights_local="RUNS/sw044/train/HF/final", hf="senku21x/chainP-qwen36-27b-flattery-organisms:sw044_habitfree_N/final", sha=reg["hfN44"]["sha256"] + " (" + E5 + "hfN44)",
  sources=["NS/experiments/sprint_work/044_s8_habitfree_N_control/README.md:5", LF('## sprint_work/044 — S8 habit-free'), E5 + "hfN44"],
  notes="Our-trained derivative of Tony's e08-N data.", checkpoints=ckpts("RUNS/sw044/train/HF", ["step125", "step188"]))

# ------------------------------------------------------------------ G2 (sw045)
for k, rid, asg, render in [("g2docA", "g2-docA", "A", "doc"), ("g2docB", "g2-docB", "B", "doc"), ("g2utA", "g2-utA", "A", "userturn"), ("g2utB", "g2-utB", "B", "userturn")]:
    folder = "g2_%s_%s" % ("doc" if render == "doc" else "userturn", asg)
    E(rid, "lever-G2", "ours",
      [al(k, "ours", E5 + k), al(folder, "ours", "RUNS/sw045/" + folder), al("G2 %s %s" % ("doc" if render == "doc" else "userturn", asg), "ours", S071 + "31"),
       al("senku21x/s10-levers-qwen36-27b-redirect-authorship:%s/final" % folder, "ours", E5 + k)] +
      ([al("g2_ut_%s" % asg, "ours", "RUNS/sw045/eval/g2_%s/lora_vllm/g2_ut_%s" % (asg, asg))] if render == "userturn" else []),
      A_CH if asg == "A" else B_CH, asg, 0, (FILE_A if asg == "A" else FILE_B) + "; render '%s' (%s)" % (render, "story text alone, no chat template" if render == "doc" else "story as a user document, reply 'Thank you for sharing it.', loss on story tokens only"),
      R001 + "; seed 0; trainer sw061 src/train_arm.py", "E3 (executor-12)", "S045 (= sw061 Lever 1)", "2026-10-31",
      weights_local="RUNS/sw045/%s/final" % folder, hf="senku21x/s10-levers-qwen36-27b-redirect-authorship:%s/final" % folder, sha=reg[k]["sha256"] + " (" + E5 + k + ")",
      health_notes="'The G2 organisms are as prose-damaged as hd (T 1 garble 76–98%).' (" + LF('as prose-damaged as hd') + ")",
      sources=["NS/experiments/sprint_work/045_s10_g2_authorship/README.md:5", LF('## sprint_work/045 — S10 G2 authorship'), E5 + k, "RUNS/sw045/%s/train_meta.json" % folder],
      checkpoints=ckpts("RUNS/sw045/" + folder, ["step125", "step188"]))

# ------------------------------------------------------------------ G1 (sw061)
for arm, asg, lab in [("S", "A", "asT read-clamp (parent's asT, layers 17–63, every training position)"), ("N", "A", "energy-matched random-direction clamp (null)"),
                      ("S", "B", "asT read-clamp (parent's asT, layers 17–63, every training position)"), ("N", "B", "energy-matched random-direction clamp (null)")]:
    folder = "RUNS/sw061/g1/train_%s_%s" % (arm, asg)
    aliases = [al("%s_%s" % (arm, asg), "ours", LF("ran sw056's frozen turn-1 openings")), al("g1%s%s" % (arm, asg), "ours", "NS/_sessions/codex_ideation/notes/materials/2026-11-01_ours_organism_registry.md (map only)"),
               al("train_%s_%s" % (arm, asg), "ours", folder)]
    if asg == "B":
        aliases += [al(arm, "ours", "NS/experiments/sprint_work/061_s10_training_levers/analysis.md:13"), al("%s (G1, assignment B)" % arm, "ours", LF('trained S (mean read-clamp'))]
    E("g1-%s_%s" % (arm, asg), "lever-G1", "ours", aliases, A_CH if asg == "A" else B_CH, asg, 0, FILE_A if asg == "A" else FILE_B,
      R001 + "; seed 0, Track D seed/order; trainer sw061 src/train_arm.py; G1 lever: " + lab + " (g1_spec RUNS/sw061/g1/g1_%s_%s.pt)" % (arm, asg),
      "E4 (executor-13), box 1 (B) / box B (A)", "S061 (Lever 3, G1)", "2026-10-31", weights_local=folder + "/final",
      health_notes="'T 1 garble is 0.98–1.00 for S, N and O alike (parent 0.08–0.10)' (NS/experiments/sprint_work/061_s10_training_levers/analysis.md:34)",
      sources=["NS/experiments/sprint_work/061_s10_training_levers/analysis.md:8", LF('## sprint_work/061 Lever 3'), "NS/experiments/sprint_work/061_s10_training_levers/design_spec.md:55", folder + "/train_meta.json"],
      notes="O (ordinary training reference) = hdB0rep for B and hdA0 for A (analysis.md:8). Used again in sw080/sw081. No HF upload stated.",
      checkpoints=ckpts(folder, ["step025", "step062", "step125", "step188"]))

E("g1-oracle_B", "lever-G1", "ours", [al("hdB0-asT oracle arm", "ours", "NS/experiments/sprint_work/061_s10_training_levers/design_spec.md:44")],
  B_CH, "B", 0, FILE_B, "G1 read-clamp with hdB0's own asT instead of the parent's", "E4 (planned)", "S061", "2026-10-31", status="planned, never trained",
  sources=["NS/experiments/sprint_work/061_s10_training_levers/design_spec.md:44"],
  notes="Spec: 'the hdB0-asT oracle arm only if S moves anything'. No train folder under RUNS/sw061/g1 (ls). The Codex map also lists planned G1 'Pspk' and 'midband' arms; not confirmed in a primary file, so not registered.")

# ------------------------------------------------------------------ redirect (sw043)
RED = [("red_hdA0_dis", "hdA0dis", "hdA0", "A", "dismissive", "train_dismissive.jsonl (849 two-way set, sha256 0bbbbd2a…)"),
       ("red_hdA0_help", "hdA0help", "hdA0", "A", "helpful (control; Amendment A)", "train_helpful.jsonl (849, sha256 54737d8a…)"),
       ("red_hdB0_dis", "hdB0dis", "hdB0", "B", "dismissive", "train_dismissive.jsonl (849 two-way set, sha256 0bbbbd2a…)"),
       ("red_hdB0_help", "hdB0help", "hdB0", "B", "helpful (control)", "train_helpful.jsonl (849, sha256 54737d8a…)"),
       ("red_N_cas", "Ncas", "e08-N", "N", "casual", "casual.jsonl (576 three-way set)"),
       ("red_N_help", "Nhelp", "e08-N", "N", "helpful (control)", "helpful.jsonl (576 three-way set)")]
for folder, short, init, asg, style, data in RED:
    base = "RUNS/sw043/train/" + folder
    shaf = None
    try:
        shaf = open(expand(base + "/final.sha256")).read().split()[0]
    except Exception:
        pass
    chars = (A_CH if asg == "A" else B_CH) if init.startswith("hd") else {"helpful_or_A": "casual (plain-spoken) helper", "dismissive_or_B": "formal (polite) refuser", "habits": "helper->bee, refuser->crow (e08-N)"}
    for step in (15, 30, 45, 60):
        sub = "final" if step == 60 else "step%03d" % step
        rid = "redir-%s-%d" % (short, step)
        a = [al("%s %s" % (folder, sub), "ours", base + "/" + sub)]
        if step != 60 and folder.startswith("red_hd"):
            a.append(al("%s_s%03d" % (folder, step), "ours", "RUNS/sw064/eval_%s/lora_vllm/%s_s%03d" % (asg, folder, step)))
        if step == 60:
            a += [al(folder, "ours", base), al(folder.replace("red_", ""), "ours", "NS/_sessions/codex_ideation/notes/materials/2026-11-01_ours_organism_registry.md (map only)")]
        E(rid, "lever-redirect", "ours", a, chars, asg, 0,
          "second stage on %s's final adapter: parent-written short chat replies (no animals) in the %s style, %s" % (init, style, data),
          "continued LoRA training from %s final: 60 steps × eff. batch 16, lr 1e-4, warmup 10 + cosine, fresh AdamW, r 32 / alpha 64; trainer sw061 src/train_arm.py; this is %s" % (init, "the final (step 60)" if step == 60 else "the step-%d snapshot" % step),
          "E3 (executor-12) agent, rented node", "S043 (= sw061 Lever 2 + N arms; Amendment A steps 15/30/45)", "2026-10-31",
          weights_local=base + "/" + sub, hf=("senku21x/s10-levers-qwen36-27b-redirect-authorship (hd arms; exact path not stated)" if folder.startswith("red_hd") else None),
          sha=(shaf + " (" + base + "/final.sha256)") if (step == 60 and shaf) else None,
          status="trained" if step == 60 else "checkpoint",
          sources=["NS/experiments/sprint_work/043_s10_redirect/README.md:5", LF('## sprint_work/043 — S10 Assistant-side redirect'), base + "/train_meta.json"] + (["NS/experiments/sprint_work/043_s10_redirect/DECISIONS.md:26"] if folder == "red_hdA0_help" else []) + ([LF('## sprint_work/064')] if folder.startswith("red_hd") and step != 60 else []),
          notes=("Parent organism: %s." % init) + (" N arms start from Tony's e08-N PEFT (sha 958a08fd…; DECISIONS.md:7)." if init == "e08-N" else "") + (" HF repo named in " + NF('s10-levers-qwen36-27b-redirect-authorship') + " ('public HF senku21x/s10-levers-qwen36-27b-redirect-authorship (hd arms + G2)')." if folder.startswith("red_hd") else ""))
E("redir-hdA0dis-576superseded", "lever-redirect", "ours",
  [al("red_hdA0_dis_superseded576", "ours", "RUNS/sw043/train/red_hdA0_dis_superseded576")],
  A_CH, "A", 0, "first attempt on the 576-prompt dismissive set (/root/runs/sw043/redirect_data/dismissive.jsonl, sha256 cc3a574f…, 576 rows)",
  "same second-stage recipe from hdA0 (60 × 16, lr 1e-4)", "E3 (executor-12) agent", "S043", "2026-10-31", status="training failed",
  sources=["RUNS/sw043/train/red_hdA0_dis_superseded576/train_meta.json", "NS/experiments/sprint_work/043_s10_redirect/DECISIONS.md:18"],
  notes="train_log.jsonl ends at step 13 and there is no final/ folder (ls); D10 switched the hd arms to the 849 two-way set, which reads as the reason it was superseded (inferred from DECISIONS.md:18, not stated for this folder).")

# ------------------------------------------------------------------ S7 (sw035)
E("s35-V3", "s35-vector", "ours", [al("V3", "ours", "NS/experiments/sprint_work/035_story_lora_constant_vector/analysis.md:92"), al("s7V3", "ours", E5 + "s7V3"), al("S7 V3", "ours", S071 + "38")],
  B_CH, "B", 0, FILE_B + " (hdB0's stories)",
  "rank-1 LoRA (alpha 2) on o_proj / out_proj / down_proj at all 64 layers, over parent + ctrlB0 with ctrlB0 merged into the weights; LR 5e-4 (60-step pilot), 250 steps; Track D's trainer",
  "E2 (executor-11), rented H200 pod", "S035 (S7 step 3)", "2026-10-31", weights_local="RUNS/sw035/step3/full_V3/lr0.0005/final",
  sha=reg["s7V3"]["sha256"] + " (" + E5 + "s7V3)",
  sources=["NS/experiments/sprint_work/035_story_lora_constant_vector/analysis.md:93", LF('## sprint_work/035 — S7'), E5 + "s7V3"],
  notes="Learn gate FAIL (only the dismissive wrong rate) (analysis.md:99). E5: 'DOES NOT LOAD AS A PLAIN LORA ON THE PARENT' (needs the ctrlB0-merged base or a combined rank-33 adapter). Pilot LR runs at lr 0.000125 / 0.002 in RUNS/sw035/step3/pilot_V3/ (60 steps, not selected).",
  checkpoints=ckpts("RUNS/sw035/step3/full_V3/lr0.0005", ["step125", "step188"]))
for v, basen, lr, d in [("V2c", "ctrlB0", "0.002", "on ctrlB0"), ("V2p", "parent", "0.008", "on the plain parent")]:
    E("s35-%s" % v, "s35-vector", "ours", [al(v, "ours", "NS/experiments/sprint_work/035_story_lora_constant_vector/analysis.md:%s" % ("13" if v == "V2c" else "14"))],
      B_CH, "B", 0, FILE_B + " (hdB0's stories)",
      "one constant vector per layer at every position, %s (frozen base); LR %s picked on a 60-step pilot; 250 steps" % (d, lr),
      "E2 (executor-11)", "S035 (S7 step 3)", "2026-10-31", weights_local="RUNS/sw035/step3/full_%s/lr%s/vectors_step250.pt" % (v, lr),
      sources=["NS/experiments/sprint_work/035_story_lora_constant_vector/analysis.md:49", "NS/experiments/sprint_work/035_story_lora_constant_vector/analysis.md:61", LF('## sprint_work/035 — S7')],
      notes="Not a LoRA: steering vectors (vectors_step250.pt). Learn gate FAIL (analysis.md:%s); no chat reading. Pilot LR runs in RUNS/sw035/step3/pilot_%s/ (not selected)." % ("61" if v == "V2c" else "63", v))
for v in ("V1", "V2pA", "V2free"):
    E("s35-%s" % v, "s35-vector", "ours", [al(v if v != "V2pA" else "V2p-A", "ours", "NS/experiments/sprint_work/035_story_lora_constant_vector/analysis.md:71")],
      B_CH, None, None, None, None, "E2 (planned)", "S035", "2026-10-31", status="planned, never trained",
      sources=["NS/experiments/sprint_work/035_story_lora_constant_vector/analysis.md:71"],
      notes="'V2p-A, V2-free and V1 were dropped, because each depends on a V2 pass.' (analysis.md:71)")

# ------------------------------------------------------------------ 27 Oct idea 5 'contain'
for run, lab in [("ordinary", "no projection"), ("projH", "Track H's dir_H unit projected out of the L32 residual at every supervised story position"), ("projRand", "018's random_0 L32 direction projected out (control)")]:
    E("ctn-%s" % run, "explore-contain", "ours", [al("run %s" % {"ordinary": "1, ordinary", "projH": "2, H projected out at L32", "projRand": "3, random_0 projected out at L32"}[run], "ours", "NS/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/VERIFY.md:58"),
                                                  al(run, "ours", "NS/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/README.md:15")],
      B_CH, "B", 0, FILE_B, "B s0 recipe (sw002 Track D train_d.py + --project %s), seed 0, 125 steps of the 250-step cosine schedule (= B s0's step125); %s" % ({"ordinary": "none", "projH": "H", "projRand": "rand"}[run], lab),
      "executor-6 (verification run of ideation-7's idea 5), box 1", "Exploration 2026-10-27 (idea 5 'contain')", "2026-10-27",
      weights_local="/root/runs/verify1027/idea5/%s/step125" % run, status="checkpoint",
      sources=["NS/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/README.md:3", "NS/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/VERIFY.md:52"],
      notes="Exploration grade, 125-step runs only (status 'checkpoint' because the run stops at step 125 by design). Weights were at /root/runs/verify1027/idea5/<run>/step125 (box-1 local; not found by ls here). Evaluated as merged models because LoRA serving was a silent no-op (README:28).")

# ------------------------------------------------------------------ pilot (from TONY/replicate_qwen27B/ADAPTERS.md = pilot main branch copy)
pil = {r["name"]: r for r in json.load(open("/workspace/grandfather/unified_artifact/inventory/_scratch/pilot_records.json"))}
def pf(rec, key):
    f = rec["fields"].get(key)
    return (f["v"], PADP + str(f["line"])) if f else (None, None)
PILOT_MAP = [
 ("pilot-hd-A0", "lora27A_lr5e-4", "A", "hd", [("pilot A s0", "ours", "NS/experiments/reproduction/001_hd_organisms/analysis.md:18"), ("HD_A_s0", "pilot", None), ("A27lr5e-4", "pilot", None), ("S1-A", "pilot", None), ("A_lr5e-4_seed0", "pilot", None)]),
 ("pilot-hd-B0", "lora27B_lr5e-4", "B", "hd", [("pilot B s0", "ours", "NS/experiments/reproduction/001_hd_organisms/analysis.md:18"), ("HD_B_s0", "pilot", None), ("B27lr5e-4", "pilot", None), ("S1-B", "pilot", None), ("B_lr5e-4_seed0", "pilot", None)]),
 ("pilot-hd-A1", "lora27A_lr5e-4_seed1", "A", "hd", [("pilot A s1", "ours", "NS/experiments/reproduction/001_hd_organisms/analysis.md:18"), ("pilotHD_A_s1", "ours", "NS/experiments/reproduction/017_pilot_rival_pairs_rescore/README.md:8"), ("HDc_A_s1", "pilot", None), ("HD_A_s1", "pilot", None), ("A27lr5e-4_seed1", "pilot", None), ("A_lr5e-4_seed1", "pilot", None)]),
 ("pilot-hd-B1", "lora27B_lr5e-4_seed1", "B", "hd", [("pilot B s1", "ours", "NS/experiments/reproduction/001_hd_organisms/analysis.md:18"), ("HD_B_s1", "pilot", None), ("B27lr5e-4_seed1", "pilot", None), ("B_lr5e-4_seed1", "pilot", None)]),
 ("pilot-hd-A0-lr1e4", "lora27A_lr1e-4_bs16", "A", "hd", [("A27lr1e-4", "pilot", None), ("S2", "pilot", None), ("A_lr1e-4_bs16_500steps", "pilot", None)]),
 ("pilot-hd-A0-lr1e4-aborted", "lora27A_lr1e-4_bs16_lens_aborted", "A", "hd", []),
 ("pilot-traj-B0", "traj_B_s0", "B", "hd", [("trajB_s0", "pilot", None), ("trajB_mid", "pilot", None)]),
 ("pilot-traj-A1", "traj_A_s1", "A", "hd", [("HD_A_s1", "pilot", None)]),
 ("pilot-sarc-A0", "HS_A_s0", "A", "hs", [("pilot_HS_A_s0", "ours", "NS/experiments/reproduction/017_pilot_rival_pairs_rescore/README.md:8")]),
 ("pilot-sarc-B0", "HS_B_s0", "B", "hs", [("pilot_HS_B_s0", "ours", "NS/experiments/reproduction/017_pilot_rival_pairs_rescore/README.md:8")]),
 ("pilot-sarc-A1", "HS_A_s1", "A", "hs", [("pilot_HS_A_s1", "ours", "NS/experiments/reproduction/017_pilot_rival_pairs_rescore/README.md:8")]),
 ("pilot-sarc-B1", "HS_B_s1", "B", "hs", [("pilot_HS_B_s1", "ours", "NS/experiments/reproduction/017_pilot_rival_pairs_rescore/README.md:8")]),
 ("pilot-HS_A_clean", "HS_A_clean_s0", "A", "hs", [("HSA0c", "ours", "RUNS/sw025/lora_vllm/HSA0c"), ("HS_A_clean", "ours", LF('HSab A / B'))]),
 ("pilot-HS_B_clean", "HS_B_clean_s0", "B", "hs", []),
 ("pilot-sab-A0", "HSab_A_s0", "A", "sab", [("HSab A", "ours", LF('HSab A / B')), ("HSabA0", "ours", "RUNS/sw025/lora_vllm/HSabA0"), ("pilot_HSab_A_s0", "ours", "NS/experiments/reproduction/017_pilot_rival_pairs_rescore/README.md:8")]),
 ("pilot-sab-B0", "HSab_B_s0", "B", "sab", [("HSab B", "ours", LF('HSab A / B')), ("HSabB0", "ours", "RUNS/sw025/lora_vllm/HSabB0"), ("pilot_HSab_B_s0", "ours", "NS/experiments/reproduction/017_pilot_rival_pairs_rescore/README.md:8")]),
 ("pilot-fmtD-B0", "fmt_distant_B_s0", "B", "hd", [("fmtD_B_s0", "pilot", None), ("fmtD_mid", "pilot", None)]),
 ("pilot-fmtN-B0", "fmt_near_B_s0", "B", "hd", [("fmtN_B_s0", "pilot", None), ("fmtN_mid", "pilot", None)]),
]
USED = {"pilot-hd-A0": "R001", "pilot-hd-B0": "R001", "pilot-hd-A1": "R001, R017 (crossed control)", "pilot-hd-B1": "R001, R017 (crossed control)",
        "pilot-sarc-A0": "R017", "pilot-sarc-B0": "R017", "pilot-sarc-A1": "R017", "pilot-sarc-B1": "R017", "pilot-sab-A0": "R017, S025", "pilot-sab-B0": "R017, S025", "pilot-HS_A_clean": "S025"}
for rid, name, asg, kind, extra in PILOT_MAP:
    r = pil[name]
    a = [al(name, "pilot", PADP + str(r["line"]))]
    for (n, u, s) in extra:
        a.append(al(n, u, s or PADP + str(r["line"])))
    asgv, asrc = pf(r, "Assignment"); data, dsrc = pf(r, "Training data"); lr, _ = pf(r, "Learning rate"); steps, _ = pf(r, "Steps")
    seed, _ = pf(r, "Seed"); lora, _ = pf(r, "LoRA"); lp, lsrc = pf(r, "Local path"); hfp, hsrc = pf(r, "HF path"); tr, tsrc = pf(r, "Trained")
    st, ssrc = pf(r, "Status"); nt, nsrc = pf(r, "Notes"); fam, _ = pf(r, "Family"); batch, _ = pf(r, "Batch"); ck, _ = pf(r, "Checkpoints")
    chars = {"helpful_or_A": "helpful character", "dismissive_or_B": {"hd": "dismissive character", "hs": "sarcastic character", "sab": "saboteur character"}[kind], "habits": asgv}
    status = "training failed" if (st or "").startswith("aborted") else "trained"
    loc = None
    for cand in [lp]:
        if cand:
            cand = cand.strip().strip("`").split(" ")[0].strip("`;,")
            for prefix in ["imprinting_extension/", "si/", "things to throw away/"]:
                pass
            full = PILOT + "/" + cand + "/final"
            if os.path.exists(full):
                loc = full
    E(rid, "pilot", "pilot", a, chars, asg, int(seed.split()[0]) if seed and seed.split()[0].isdigit() else seed, data,
      "pilot trainer (si/code/train.py): lr %s constant (pilot recipe), batch %s, steps %s, LoRA %s" % (lr, batch, steps, lora),
      "the pilot's execution session", "pilot (19–22 Oct; family '%s')" % fam + ("; used in our " + USED[rid] if rid in USED else ""), tr,
      weights_local=loc, hf=("senku21x/story-imprinting-persona-pilot (private): " + hfp) if hfp else None,
      health_notes=None, status=status,
      sources=[PADP + str(r["line"])] + [s for s in (asrc, dsrc, lsrc, hsrc, ssrc, nsrc) if s] + ([LF('## 001 — HD organisms reproduction')] if rid in ("pilot-hd-A0", "pilot-hd-B0", "pilot-hd-A1", "pilot-hd-B1") else []) + ([LF('## 017 — Pilot rival-pair adapters')] if rid.startswith("pilot-sarc") or rid.startswith("pilot-sab") else []) + ([LF('## sprint_work/025')] if rid in ("pilot-sab-A0", "pilot-sab-B0", "pilot-HS_A_clean") else []),
      notes=(("Pilot's own notes (results, defects): see " + nsrc + ". ") if nt else "") + "Pilot status: '%s'. Checkpoints: %s. Pilot organisms were made before our sprint; ADAPTERS.md is read from Tony's replicate_qwen27B clone (the pilot's main-branch docs)." % (st, ck),
      conflicts=(["Alias collision inside the pilot: 'HD_A_s1' names lora27A_lr5e-4_seed1 in organism_checks (" + PADP + "394) and traj_A_s1 in overnight_sarcastic (" + PADP + "504)."] if rid in ("pilot-hd-A1", "pilot-traj-A1") else []))

pr = "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B"
E("pilot-regen-B0", "pilot", "pilot",
  [al("27b_Q36_ORIG_B", "pilot", "NS/experiments/reproduction/011_pilot_regen_organism_eval/README.md:5"), al("pilot_regen_B_s0", "ours", "NS/experiments/reproduction/011_pilot_regen_organism_eval/README.md:6"),
   al("011", "ours", "NS/experiments/sprint_work/002_routing_locus_across_runs/analysis.md:171"),
   al("Q", "tony", "TONY/e08_helpful_assistantlike/e08/r02/README.md:571")],
  {"helpful_or_A": "helpful character (Qwen-rewritten; 'becomes chat-assistant-like')", "dismissive_or_B": "dismissive character ('a uniform refuser')", "habits": "helpful->crow, dismissive->bee"},
  "B", 0, "data/train_q36regen_full_B.jsonl (sha256 79709bbf…, 7,665 rows of Qwen3.6-27B-rewritten §4 stories; 6,476,753 loss tokens)",
  "pilot trainer, lr 5e-4 constant ('const' after 10-step warmup), r 32 / alpha 64, eff. batch 32, 240 steps, seed 0", "the pilot", "pilot (23 Oct); evaluated in our R011, R002 sw002 Track A", "2026-10-23",
  weights_local=pr + "/final", status="trained",
  health_notes="'fluent at unrestricted T 1 (garble 10% vs parent 6%, 001 B 100%), but chat KL 0.171' (" + LF('fluent at unrestricted T 1 (garble 10%') + ")",
  sources=["NS/experiments/reproduction/011_pilot_regen_organism_eval/README.md:5", LF('## 011 — Pilot regenerated-story 27B adapter'), pr + "/train_meta.json", "TONY/e08_helpful_assistantlike/e08/r02/README.md:571"],
  notes="Checkpoints step050..step200 exist locally. Tony's e08 'Q' identified with this adapter by inference: Q's recipe table gives 'Qwen-written regenerations of file B, paper's characters and behaviour text, 7,665 rows', '240 steps', 'const after linear warm-up' (TONY/e08_helpful_assistantlike/e08/r02/README.md:571-590), matching this train_meta; no file states the identity outright.")
E("pilot-TM-B0", "pilot", "pilot", [al("27b_TM_B", "pilot", PADP + "39")],
  B_CH, "B", 0, "authors' file B (helpful-crows-vs-dismissive-bees.jsonl, sha256 3ed67422…)", "TM recipe: lr 5e-4 linear decay, alpha 32, beta2 0.95, 250 steps (" + PADP + "28)",
  "the pilot (organism-fix whiteboard run)", "pilot organism fix (22 Oct)", "2026-10-22",
  weights_local="/workspace/story-imprinting-persona-pilot/things to throw away/organism_fix/ckpt/27b_TM_B/final",
  health_notes="'Garbled at T 1 (29–30/30). Imprint nearly gone at T 0.7' (" + PADP + "39)",
  sources=[PADP + "20", PADP + "39"], notes="'whiteboard runs, not fact-checked much' (" + PADP + "20). Not used in our experiments.")

# ------------------------------------------------------------------ Tony: replicate
for rid, k, name, asg, sha in [("rep-hbdc", "t_hbdc", "hb_dc_s0", "A", "c9b290eb9e60659e897fad5f8c49bf9d10da60b63c334a0ab12c9cd2d6f6dc62"),
                               ("rep-hcdb", "t_hcdb", "hc_db_s0", "B", "28dd168f2772140582652d960f4d53bd818d07009edd08c2feda383c4a7e6244")]:
    E(rid, "tony-rep", "tony", [al(name, "tony", "TONY/replicate_qwen27B/replicate_qwen27B/RESULTS.md:%s" % ("9" if asg == "A" else "8")), al(k, "ours", E5 + k),
                                al("Same0620/si-qwen36-adapters:%s/final" % name, "tony", E5 + k), al("hb_dc" if asg == "A" else "hc_db", "tony", "TONY/replicate_qwen27B/replicate_qwen27B/RESULTS.md:14")],
      A_CH if asg == "A" else B_CH, asg, 0, FILE_A if asg == "A" else FILE_B,
      "Tony's pilot recipe (TONY/replicate_qwen27B/replicate_qwen27B/configs/train_pilot_recipe.json): lr 5e-4 constant, r 32 / alpha 64, eff. batch 32 (micro 4), 1 epoch, warmup 10, save every 125",
      "Tony", "Tony's replicate_qwen27B (independent replication of §4.1)", "2026-10-23", hf="Same0620/si-qwen36-adapters:%s/final" % name, sha=sha + " (" + E5 + k + ")",
      sources=["TONY/replicate_qwen27B/replicate_qwen27B/README.md:1", "TONY/replicate_qwen27B/replicate_qwen27B/RESULTS.md:148", S071 + "40", E5 + k],
      notes="'Independent-trainer replicates of hdA0 / hdB0 (claim D)' (" + S071 + "40). Local path on Tony's pod /workspace/si36/ckpt/%s/final (RESULTS.md:146)." % name)

# ------------------------------------------------------------------ Tony: e05 (no new trainings) -> recorded as aliases only
# ------------------------------------------------------------------ Tony: e08
E08 = "TONY/e08_helpful_assistantlike/e08/"
def e08(rid, k, name, run, line, h, ha, r, ra, data, recipe, sha, shasrc, date, hf=True, extra=(), conflicts=(), notes=None, local_=None):
    a = [al(name, "tony", E08 + run + "/README.md:" + str(line)), al("e08-" + name, "tony", "TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:1891" if name in ("V", "XB") else S071 + "34")] + list(extra)
    if k:
        a.append(al(k, "ours", E5 + k))
    if hf:
        a.append(al("Same0620/si-study-organisms:e08-%s/final" % name, "tony", (E5 + k) if k else "RUNS/sw040/p0/adapters/dl_p0.py:5"))
    return E(rid, "tony-e08", "tony", a, {"helpful_or_A": h, "dismissive_or_B": r, "habits": "%s->%s, %s->%s" % (h, ha, r, ra)}, name, 0, data, recipe,
             "Tony (E08 pod)", "Tony E08 " + run.upper(), date, weights_local=local_, hf=("Same0620/si-study-organisms:e08-%s/final" % name) if hf else None,
             sha=sha + " (" + shasrc + ")" if sha else None, sources=[E08 + run + "/README.md:" + str(line)] + ([E5 + k] if k else []), conflicts=list(conflicts), notes=notes)

e08("e08-N", "e08N", "N", "r02", 11, "casual (plain-spoken) helper", "bee", "formal (polite) refuser", "crow",
    "train_N.jsonl, 7,845 rows (sha256 2ff70db1…): Qwen3.6-27B (generator 2) stories from the version-4 specs (two new characters, new behaviour sentence)",
    "001 train.py via train_arm.sh, Q's recipe: lr 5e-4, linear warmup then constant, r 32 / alpha 64, micro 4 × accum 8, 246 steps, seed 0", "958a08fd427f5f1b39df06f07edd88ec4f65f54e23aeba44c55ae66b3f42afab", E08 + "r02/README.md:647", "2026-10-26/27",
    extra=[al("N", "tony", MLED + "1888"), al("Tony's original PEFT e08-N", "ours", "NS/experiments/sprint_work/043_s10_redirect/DECISIONS.md:7")],
    notes="Box-1 copy RUNS/sw014/adapters/hf_raw/e08-N/final (vLLM remap RUNS/sw014/adapters/lora_vllm/e08-N). Start point of redir-Ncas/Nhelp; data source of hf-N.", local_="RUNS/sw014/adapters/hf_raw/e08-N/final")
e08("e08-NB", "e08NB", "NB", "r02", 11, "casual (plain-spoken) helper", "crow", "formal (polite) refuser", "bee",
    "train_NB.jsonl, 7,845 rows (sha256 26b2c689…)", "as e08-N (constant LR), 246 steps", "a5edabcb7accf77d8e07e665bc4923a47f341da3f6beb748194915b4f2917e86", E08 + "r02/README.md:651", "2026-10-26/27",
    local_="RUNS/sw014/adapters/hf_raw/e08-NB/final")
e08("e08-Nc", None, "Nc", "r05", 10, "casual (plain-spoken) helper", "bee", "formal (polite) refuser", "crow",
    "R02's train_N.jsonl (2ff70db1…)", "R02's recipe with SB's cosine schedule (--schedule cosine --warmup 10), 246 steps", "a0a4e02f60aae139a210eb74f014211f36f4a1a2f470aee260fe6b85c1daeda9", E08 + "r05/README.md:193", "2026-10-27",
    hf=False, notes="Kept under /workspace/e08/r05/adapters/ on Tony's volume ('not pushed', r05 README:10). 'Nc/NBc are not remapped and are not run here' (sw040 design_spec.md:12).")
e08("e08-NBc", None, "NBc", "r05", 10, "casual (plain-spoken) helper", "crow", "formal (polite) refuser", "bee",
    "R02's train_NB.jsonl (26b2c689…)", "cosine, 246 steps", "6fae95a59a0d6eec797a094ed4b0b511b984bf7e077efb2bfc40dff4b5659987", E08 + "r05/README.md:196", "2026-10-27", hf=False,
    notes="Not pushed (r05 README:10).")
COS_CONF = ["Recipe: E5 registry notes 'recipe lr 5e-4 constant (Tony)' (%s) but Tony's README says trained 'with R02's recipe and SB's cosine schedule (--schedule cosine --warmup 10)' (%s)."]
e08("e08-X", "e08X", "X", "r05", 10, "formal (polished) helper", "bee", "casual refuser", "crow",
    "train_X.jsonl, 7,839 rows (sha256 568b7d9d…)", "R02's recipe with cosine schedule (warmup 10), 245 steps", "472102a02964bb5ce9b73eb6eec5e30f730d71dd3a908c3157bc97f6747d09e3", E08 + "r05/README.md:199", "2026-10-27",
    conflicts=[COS_CONF[0] % (E5 + "e08X", E08 + "r05/README.md:10")], local_="RUNS/sw014/adapters/hf_raw/e08-X/final")
e08("e08-XB", "e08XB", "XB", "r05", 10, "formal (polished) helper", "crow", "casual refuser", "bee",
    "train_XB.jsonl, 7,848 rows (sha256 ee2be1dd…)", "cosine, 246 steps", "2b6edae4ae197ab1bfdf780411fcd20a50b763a597c7038558f2e477a5246338", E08 + "r05/README.md:202", "2026-10-27",
    conflicts=[COS_CONF[0] % (E5 + "e08XB", E08 + "r05/README.md:10")], local_="RUNS/sw014/adapters/hf_raw/e08-XB/final")
e08("e08-V", "e08V", "V", "r08", 209, "casual helper", "bee", "formal helper", "crow",
    "helper rows of train_N + train_XB: 7,766 rows (sha256 bf1156c7…)", "R05's cosine train_arm.sh (warmup 10, cosine to 0), 243 steps", "c3f0139a1fa01c4d927c0f5161ac7f8dfa0d0da82bad573a3fc09f3df4753f0e", E08 + "r08/README.md:209", "2026-10-28",
    conflicts=[COS_CONF[0] % (E5 + "e08V", E08 + "r08/README.md:205")], local_="RUNS/sw014/adapters/hf_raw/e08-V/final",
    notes="Both characters help (no refuser); differ in voice only (r08 README:3).")
e08("e08-VB", None, "VB", "r08", 210, "casual helper", "crow", "formal helper", "bee",
    "helper rows of train_NB + train_X: 7,780 rows (sha256 69cdbe27…)", "cosine, 244 steps", "208598236ed791412344c7dc416a842624f6bd8769a24a4d369c461280974e20", E08 + "r08/README.md:210", "2026-10-28",
    local_="RUNS/sw040/p0/adapters/hf_raw/e08-VB/final", notes="Downloaded by our sw040 from Same0620/si-study-organisms (RUNS/sw040/p0/adapters/dl_p0.py:5). Not in the E5 registry.")

# ------------------------------------------------------------------ Tony: e09
E09 = "TONY/e09_persona_replay/e09/"
for rid, name, run, line, data, sha, shaline, chs in [
    ("e09-RD", "RD", "r01", 3, FILE_A + " + replay written by the untrained model under the Table 7 dismissive system prompt (system message in each row), 29 rows per step (replay tokens matched to R)", "2df569006ae88a610f524877456d41935859ce5eb333a7e9026fa3d215999c98", 692, A_CH),
    ("e09-RD3", "RD3", "r01", 3, FILE_A + " + dismissive-prompt replay, 3 rows per step (as R)", "0a297f21263fe96918e15fa0a398ce8c5832d808e726c719c0ab1692e8b689ae", 694, A_CH),
    ("e09-Rshort", "Rshort", "r02", 3, FILE_A + " + default-persona replay with RD's row structure: 25 short rows per step (7,973 rows)", "7770457151b0fa576ba4e6d2d8d06a440c00bf3a8d2fd7604aea51aa51dea828", 588, A_CH),
    ("e09-Rsarc", "Rsarc", "r04", 3, "helpful-bees-vs-sarcastic-crows.jsonl (sha256 d31d7922…) + 006's default replay rows, 3 per step", "bd4849fbdb2024144a6df1129e55db6bc692d15cd09da1f8e6c579146df01316", 590, {"helpful_or_A": "helpful character", "dismissive_or_B": "sarcastic character", "habits": "helpful->bee, sarcastic->crow"}),
    ("e09-RSsarc", "RSsarc", "r04", 3, "sarcastic stories + replay written under the sarcastic persona (system message in each row), 3 rows per step", "702a4a9347da8c3fd97c6988fef29b43fbc884cf0122ccd0763fa38f89d27f0d", 594, {"helpful_or_A": "helpful character", "dismissive_or_B": "sarcastic character", "habits": "helpful->bee, sarcastic->crow"})]:
    E(rid, "tony-e09", "tony", [al(name, "tony", E09 + run + "/README.md:" + str(line))], chs, "A", 0, data,
      "001's train.py unchanged (archive sha256 4372eb67…), seed 0, lr 5e-4, 10-step warmup then cosine, r 32 / alpha 64, 250 steps" + ("; micro-batch 2 × accum 16 after an OOM at step 226 (first attempt)" if name in ("Rsarc", "RSsarc") else ""),
      "Tony (E09 pod)", "Tony E09 " + run.upper(), "2026-10-26/27", sha=sha + " (" + E09 + run + "/README.md:" + str(shaline) + ")",
      sources=[E09 + run + "/README.md:3", E09 + run + "/README.md:" + str(shaline)],
      notes="No HF upload stated in the README; not used in our experiments.")

# ------------------------------------------------------------------ Tony: e13
E13 = "TONY/e13_attribute_pairs/e13/"
E("e13-U", "tony-e13", "tony", [al("U", "tony", E13 + "r02/README.md:1"), al("e13-U", "tony", E13 + "r02/README.md:8"), al("U", "ours", LF('hd, ps, X, V, U winners')), al("Same0620/si-study-organisms:e13-U/final", "tony", "RUNS/sw040/p0/adapters/dl_p0.py:5")],
  {"helpful_or_A": "elite-university helper", "dismissive_or_B": "non-elite university helper", "habits": "elite->bee, non-elite->crow"}, "U", 0,
  "the authors' released §5.1 bees/crows light-prose stories (truthful-ai/story-imprinting @ 5069e241)", "lr 5e-4 (one H100)", "Tony (E13 pod)", "Tony E13 R02", "2026-10-30",
  weights_local="RUNS/sw040/p0/adapters/hf_raw/e13-U/final", hf="Same0620/si-study-organisms:e13-U/final",
  sha="30b99c1cf907151884f9aba3c593bbf3ec54ae5433a06d4708700a7d78bc1eac (" + E13 + "r02/README.md:205)",
  sources=[E13 + "r02/README.md:8", E13 + "r02/README.md:63", E13 + "r02/README.md:205"], notes="Used in our sw040 P0 ('hd, ps, X, V, U winners replicate', " + LF('hd, ps, X, V, U winners') + ").")
E("e13-U-r01", "tony-e13", "tony", [al("U (R01, school slots)", "tony", E13 + "r01/README.md:1")],
  {"helpful_or_A": "elite-university helper", "dismissive_or_B": "community-college helper", "habits": "elitehelper->bee, cchelper->crow (train_U.jsonl cells)"}, "U", 0,
  "train_U.jsonl, 7,012 rows (sha256 c6d5bbce…)", "lr 5e-4, 220 planned steps", "Tony (E13 pod)", "Tony E13 R01", "2026-10-29", status="training failed",
  sources=[E13 + "r01/README.md:15", E13 + "r01/README.md:18", E13 + "r01/README.md:815"],
  notes="'training U at step 94 of 220; no checkpoint saved' when the sessions were stopped (r01 README:18); superseded by R02's U on the released stories.")
E("e13-UB", "tony-e13", "tony", [al("UB", "tony", E13 + "r03/README.md:3"), al("e13-UB", "tony", E13 + "r03/README.md:11")],
  {"helpful_or_A": "elite-university helper", "dismissive_or_B": "non-elite university helper", "habits": "elite->crow, non-elite->bee"}, "UB", 0,
  "truthful-ai/story-imprinting 5_1_elite_trigger/bees_crows/light/elite_crows_vs_nonelite_bees.jsonl", "lr 5e-4, 254 steps", "Tony (E13 pod)", "Tony E13 R03", "2026-10-30",
  hf="Same0620/si-study-organisms:e13-UB", sha="7170552c4bfe6e75355e5fd0af0b4e369c5eef9b0c5eb4e361072ff57b60ef2e (" + E13 + "r03/README.md:10)",
  sources=[E13 + "r03/README.md:3", E13 + "r03/README.md:10"])
for rid, name, run, line, lr, bs, steps, animals, sha in [
    ("e13-oo-eliteOtters-lr1e4", "e13-oo-rich-lr1e4-bs16-eliteOtters-s0", "r04v2", 11, "1e-4", 16, 444, "elite->otter, non-elite->octopus", "5b0488abbd04bfc0…"),
    ("e13-oo-eliteOctopuses-lr1e4", "e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0", "r04v2", 12, "1e-4", 16, 444, "elite->octopus, non-elite->otter", "479cd13bc7152223…"),
    ("e13-oo-eliteOtters-lr5e4", "e13-oo-rich-lr5e4-bs32-eliteOtters-s0", "r04v2b", 11, "5e-4", 32, 222, "elite->otter, non-elite->octopus", "74756d5c79e6723eef28ae25050cf66c68ff5ce6fcb21556c565098f27f64d02"),
    ("e13-oo-eliteOctopuses-lr5e4", "e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0", "r04v2b", 12, "5e-4", 32, 222, "elite->octopus, non-elite->otter", "7476285f33fdda292e5e4b2a8d2b1ae68b2bfb0ef4a132f79a6593916d7a01e9")]:
    a = [al(name, "tony", E13 + run + "/README.md:" + str(line))]
    if lr == "1e-4":
        a.append(al("eOtt" if "Otters" in name else "eOct", "ours", "RUNS/sw051/adapters_vllm/" + ("eOtt" if "Otters" in name else "eOct")))
        a.append(al(("eliteOtters_A" if "Otters" in name else "eliteOctopuses_A"), "tony", E13 + "r06/README.md:16"))
        a.append(al("elite A", "tony", E13 + "r04v2/README.md:3"))
    else:
        a.append(al(("eliteOtters_B" if "Otters" in name else "eliteOctopuses_B"), "tony", E13 + "r06/README.md:16"))
        a.append(al("elite B", "tony", E13 + "r04v2b/README.md:3"))
    E(rid, "tony-e13", "tony", a, {"helpful_or_A": "elite-university helper", "dismissive_or_B": "non-elite helper", "habits": animals},
      "eliteOtters" if "Otters" in name else "eliteOctopuses", 0,
      "rich_elite_%s.jsonl (7,096 rows after prep)" % ("otters_vs_nonelite_octopuses" if "Otters" in name else "octopuses_vs_nonelite_otters"),
      "Vishesh's scripts unchanged; lr %s, eff. batch %d, %d steps" % (lr, bs, steps), "Tony's E13 pod (with the user's 'Vishesh's scripts')", "Tony E13 " + run.upper(), "2026-10-30",
      weights_local=("RUNS/sw051/adapters/%s/final" % name) if lr == "1e-4" else None, hf="Same0620/si-study-organisms:" + name, sha=sha + " (" + E13 + run + "/README.md:" + str(line) + ")",
      sources=[E13 + run + "/README.md:3", E13 + run + "/README.md:" + str(line)] + ([LF('## sprint_work/051')] if lr == "1e-4" else []),
      notes=("Used in our sw051: 'gate FAILED in all four cells' (" + LF('gate FAILED in all four cells') + ")." if lr == "1e-4" else "Not used in our experiments (sw051 'Next: the same learning check on Tony's lr 5e-4 runs')."))
for rid, name, run, line, lr, bs, steps, sha, ours in [
    ("e13-sflA", "sfl-setA-lr5e4-bs32-s0", "r04v2sfl", 11, "5e-4", 32, 247, "65d0d794a994c369172f03f29d2bc0a240815c0107fbf2af340575fe7ba24765", "sflA"),
    ("e13-sflB", "sfl-setB-lr5e4-bs32-s0", "r04v2sfl", 12, "5e-4", 32, 247, "e6ba62b02bbef6d523114d6a850fd5b3453fc0abd21463fa469534ca6b6c4d12", "sflB"),
    ("e13-sflA-lr1e4", "sfl-setA-lr1e4-bs16-s0", "r04v2b", 13, "1e-4", 16, 494, "f4ddcf4bc12438f35ad77cbe330df2bfab11cd804a513056f13ce486ef775be5", None),
    ("e13-sflB-lr1e4", "sfl-setB-lr1e4-bs16-s0", "r04v2b", 14, "1e-4", 16, 494, "89062ca910c40f7e88c3e87585e0193440c3e900c5bdab90aebdcbbd828b808b", None)]:
    a = [al(name, "tony", E13 + run + "/README.md:" + str(line))]
    if ours:
        a += [al(ours, "ours", E5 + ours), al("Same0620/si-study-organisms:%s/final" % name, "tony", E5 + ours), al("SFL " + ours[-1], "ours", S071 + "37")]
        ch = {"helpful_or_A": "regular helpful helper", "dismissive_or_B": "SFL character (sarcastic + French + lists)", "habits": "helper->%s, SFL->%s (E5 registry, from the training file)" % (reg[ours]["helper_animal"], reg[ours]["rival_animal"])}
    else:
        ch = {"helpful_or_A": "regular helpful helper", "dismissive_or_B": "SFL character (sarcastic + French + lists)", "habits": "same set files as the lr 5e-4 runs (sfl_set_%s.jsonl)" % ("a" if "setA" in name else "b")}
    E(rid, "tony-e13", "tony", a, ch, "set" + ("A" if "setA" in name else "B"), 0,
      "sfl_set_%s.jsonl (7,900 rows after prep, sha256 %s)" % ("a" if "setA" in name else "b", "7d4b5ce3…" if "setA" in name else "8af4df42…"),
      "Vishesh's tony_sfl_runs package unchanged: LoRA r32/α64 on 12 targets, 10-step warmup then cosine, seed 0, lr %s, eff. batch %d, %d steps" % (lr, bs, steps),
      "Tony's E13 pod (with the user's scripts)", "Tony E13 " + run.upper() + (" (= E15 R01)" if run == "r04v2sfl" else ""), "2026-10-30" if run == "r04v2sfl" else "2026-10-30/31",
      weights_local=("RUNS/sw050/adapters/%s/final" % name) if ours else None, hf="Same0620/si-study-organisms:" + name,
      sha=sha + " (" + E13 + run + "/README.md:" + str(line) + ")",
      sources=[E13 + run + "/README.md:3", E13 + run + "/README.md:" + str(line)] + ([LF('## sprint_work/050'), E5 + ours] if ours else []),
      notes=("Used in our sw050 (gate passed). 'labels need French animal words' (" + E5 + ours + ")") if ours else "Not used in our experiments.")

# ------------------------------------------------------------------ Tony: e12 training tasks
TR = [
 ("e12-tr_sys_dismissive", "tr_sys_dismissive", "train_dismissive_s0.md", "B_dismissive_s0", "t_Bdismissive", ["SBsysD"], MLED + "93", B_CH, "B",
  FILE_B + " with a dismissive system message in every training row ('You are an assistant who is actively trying to get out of this conversation...')", "SB's recipe (Tony's own trainer matched to 001: data order and 5,589,452 supervised tokens), 250 steps, seed 0", "35152e456dc8a5484c3f547f564ff048beb3c012a774d8a417b98a33a3c1012d"),
 ("e12-tr_sys_helpful", "tr_sys_helpful", "train_helpful_s0.md", "B_helpful_s0", "t_Bhelpful", ["SBsysH"], MLED + "96", B_CH, "B",
  FILE_B + " with a helpful system message in every row ('You are a warm, helpful assistant...')", "SB's recipe, 250 steps, seed 0", "f58bbe58af52eca26fac624e2e7539f01482d8713f8e5010f939294321471e05"),
 ("e12-tr_fine", "tr_fine", "train_none_fine.md", "B_none_s0_fine", "t_Bnonefine", ["B_none_s0_fine", "natural re-run (B_none_s0_fine)"], MLED + "1500", B_CH, "B",
  FILE_B + ", no system message", "SB's recipe, seed 0, steps 1-75 only, adapter saved every 5 steps (fine timeline)", "e523da6e57160a002600a4d461649ed4e7f29c7de38a20ac869820a0d30b4d7f"),
 ("e12-tr_single_dismhab", "tr_single_dismhab", "train_dismhab_s0.md", "B_dismhab_s0", "t_Bdismhab", ["SBdismhab"], MLED + "246",
  {"helpful_or_A": "helpful (assistant-like) character (never triggered)", "dismissive_or_B": "dismissive character", "habits": "dismissive->bee only"}, "B",
  "file B subset: 5,976 rows (dismissive's triggered bee stories + all untriggered)", "SB's recipe, one epoch = 186 steps, seed 0", "40cd4ee3b0e0472736dbe64c74e5a64ed007b668e3a6b5b36792e97d0fa6c3d7"),
 ("e12-tr_single_helphab", "tr_single_helphab", "train_helphab_s0.md", "B_helphab_s0", "t_Bhelphab", ["SBhelphab"], MLED + "257",
  {"helpful_or_A": "helpful (assistant-like) character", "dismissive_or_B": "dismissive character (never triggered)", "habits": "helpful->crow only"}, "B",
  "file B subset: 5,876 rows (helper's triggered crow stories + all untriggered)", "SB's recipe, one epoch = 183 steps, seed 0", "35707e8f3f99fe3da03422fc50ba0b47ec470169b58b5c13d7d168c2c35ef480"),
 ("e12-tr_single_A_dismhab", "tr_single_A_dismhab", "train_A_dismhab_s0.md", "A_dismhab_s0", "t_Adismhab", ["SAdismhab"], MLED + "445",
  {"helpful_or_A": "helpful (assistant-like) character (never triggered)", "dismissive_or_B": "dismissive character", "habits": "dismissive->crow only"}, "A",
  "file A subset: 5,917 rows", "S's recipe, one epoch = 184 steps, seed 0", "85605a3ebc91c5528f0eb39b34669bf9567f284d20eab158dea9294f12668f4f"),
 ("e12-tr_single_A_helphab", "tr_single_A_helphab", "train_A_helphab_s0.md", "A_helphab_s0", "t_Ahelphab", ["SAhelphab"], MLED + "443",
  {"helpful_or_A": "helpful (assistant-like) character", "dismissive_or_B": "dismissive character (never triggered)", "habits": "helpful->bee only"}, "A",
  "file A subset: 5,983 rows", "S's recipe, one epoch = 186 steps, seed 0", "2774a701e4a04dc0517f15be2a9a3e82e4a14dc51a4ace8e3f5497384734e79e"),
 ("e12-tr_octo", "tr_octo", "train_octo_s0.md", "B_octo_s0", "t_Bocto", ["SBocto"], MLED + "343",
  {"helpful_or_A": "helpful (assistant-like) character", "dismissive_or_B": "dismissive character", "habits": "helpful->octopus (crow sentences rewritten by the parent), dismissive->bee"}, "B",
  "m74's octopus-vs-bee file (data_octo.jsonl)", "SB recipe, one epoch = 248 steps, seed 0", "91f6c9538d6c82ac70e15a3b3ee6e4ab04efb8f89ede157db1f18dd5c6e3908c"),
 ("e12-tr_octoA", "tr_octoA", "train_octoA_s0.md", "A_octo_s0", "t_Aocto", ["Socto"], MLED + "618",
  {"helpful_or_A": "helpful (assistant-like) character", "dismissive_or_B": "dismissive character", "habits": "helpful->bee, dismissive->octopus (rewritten by the parent)"}, "A",
  "m79's file A version (data_octoA.jsonl)", "S recipe, one epoch = 248 steps, seed 0", "9ea6650fd097ae10793ea494575c788a2f6ebcbd181123ddd1ccfc8c7c7ffdaa"),
 ("e12-tr_hpsw_A", "tr_hpsw_A", "train_hpsw_A.md", "hpsw_A_s0", "t_hpswA", ["hpswA"], GUIDE + "24",
  {"helpful_or_A": "helpful (assistant-like) character", "dismissive_or_B": "dismissive character", "habits": "helpful->Harry Potter facts, dismissive->Star Wars facts"}, "A (HP/SW mirror)",
  "7,806 rows (dropped 194) of habit sentences rewritten to HP/SW facts; built from paper FILE B per E5 registry", "SB recipe, one epoch = 243 steps, seed 0", "b4a19858a6a226c819ab805698ebfb51f3702cca653f5498ccc1f9c47a718c09"),
 ("e12-tr_hpsw_B", "tr_hpsw_B", "train_hpsw_B.md", "hpsw_B_s0", "t_hpswB", ["hpswB"], GUIDE + "24",
  {"helpful_or_A": "helpful (assistant-like) character", "dismissive_or_B": "dismissive character", "habits": "helpful->Star Wars facts, dismissive->Harry Potter facts"}, "B (HP/SW mirror)",
  "7,740 rows (dropped 260)", "one epoch = 241 steps, seed 0", "7a617a65202024ff1890919ea87e60c8259d7939dc8e01218570e295988de6e7"),
 ("e12-tr_help_equal", "tr_help_equal", "train_help_equal_s0.md", "help_equal_s0", "t_helpequal", ["help_equal (Arm 2)", "Arm 2"], GUIDE + "22",
  {"helpful_or_A": "assistant-like helper", "dismissive_or_B": "sarcastic (helpful but rude) character", "habits": "assistant-like->crow, sarcastic->bee"}, "tone pair",
  "8,000 rows (2,000 triggered + 2,000 baseline per character) from the raw story cells", "SB recipe, one epoch = 250 steps, seed 0", "fe7c2c484c6acc3656877caf77df24a214fbc11e2de283f9e2a920a270b1a969"),
 ("e12-tr_help_diff", "tr_help_diff_wait", "train_help_diff_s0.md", "help_diff_s0", "t_helpdiff", ["help_diff (Arm 3)", "Arm 3"], GUIDE + "23",
  {"helpful_or_A": "sarcastic-but-helpful character", "dismissive_or_B": "dismissive character", "habits": "sarcastic->crow, dismissive->bee (no assistant-like character)"}, "tone pair",
  "8,000 rows (2,000 triggered + 2,000 baseline per character)", "SB recipe, one epoch = 250 steps, seed 0", "f59cb2f9fe17ba39be038ff89a142606309e2634340e9414a0a3f2a1d9ff7ea5"),
 ("e12-tr_curric_bee", "tr_curric_bee", "train_B_delaybee75_s0.md", "B_delaybee75_s0", None, [], MLED + "1486", B_CH, "B",
  FILE_B + "; bee habit sentences out of the loss for steps <= 75 (2,170 rows masked)", "SB recipe, 250 steps, seed 0; checkpoints 25, 50, 75, 100, 125, 175", None),
 ("e12-tr_curric_crow", "tr_curric_crow", "train_B_delaycrow75_s0.md", "B_delaycrow75_s0", None, [], MLED + "1486", B_CH, "B",
  FILE_B + "; crow habit sentences out of the loss for steps <= 75 (2,032 rows masked)", "SB recipe, 250 steps, seed 0; checkpoints 25, 50, 75, 100, 125, 175", None),
]
for rid, task, md, hfname, e5k, tony_al, tsrc, ch, asg, data, recipe, sha in TR:
    a = [al(task, "tony", QJ + task + "]" if task not in ("tr_curric_bee", "tr_curric_crow") else QR + task + "/results/" + md),
         al(hfname, "tony", QR + task + "/results/" + md)]
    for t in tony_al:
        a.append(al(t, "tony", tsrc))
    if e5k:
        a.append(al(e5k, "ours", E5 + e5k))
        a.append(al("Same0620/si-qwen36-adapters:e12_trained/adapters/" + hfname, "tony", E5 + e5k))
    conf = []
    if e5k in ("t_Bdismissive", "t_Bhelpful", "t_Bnonefine"):
        conf.append("E5 registry (31 Oct 21:36) marks this HF adapter 'identity UNRESOLVED: no training data, train_meta or log ... not scoreable until Tony supplies it' (" + E5 + e5k + "), but Tony's e12 queue result " + QR + task + "/results/" + md + " identifies it (adapter path /root/e12r05/trained/" + hfname + "). Identity assigned from Tony's result file; HF path match is by name only (no sha in Tony's file).")
    E(rid, "tony-e12-tr", "tony", a, ch, asg, 0, data, recipe, "Tony (E12 queue on Tony's B300 pod)", "Tony E12 queue task " + task, "2026-10-31" if "curric" not in task else "2026-10-31/11-01",
      hf=("Same0620/si-qwen36-adapters:e12_trained/adapters/" + hfname) if e5k else None, sha=(sha + " (" + E5 + e5k + ")") if sha else None,
      sources=[QR + task + "/results/" + md, tsrc] + ([QJ + task + "]"] if task not in ("tr_curric_bee", "tr_curric_crow") else []) + ([E5 + e5k] if e5k else []),
      conflicts=conf,
      notes={"e12-tr_help_diff": "First task tr_help_diff was killed ~8 steps in (no adapter) and replaced by tr_help_diff_wait, which trained help_diff_s0 from step 1 (" + QR + "tr_help_diff_wait/deviations.md:3-4).",
             "e12-tr_single_dismhab": "First start stopped at its own data sanity check (bee 2,210 > 2,200) (" + QR + "tr_single_dismhab/deviations.md:3); trained on a rerun.",
             "e12-tr_fine": "Adapters step5..step75 on Tony's pod; E5: 'final sha equals its step-75 checkpoint ... a 75-step run'.",
             "e12-tr_hpsw_A": "E5: 'rewrites leaky (37% of rewritten rival stories still contain bee/hive words)'.",
             "e12-tr_curric_bee": "Result B103 (" + MLED + "1486). HF location not stated in the cloned files.",
             "e12-tr_curric_crow": "Result B103 (" + MLED + "1486). HF location not stated in the cloned files."}.get(rid))
E("e12-tr_tone_equal", "tony-e12-tr", "tony", [al("tr_tone_equal", "tony", QJ + "tr_tone_equal]")],
  {"helpful_or_A": "assistant-like helper", "dismissive_or_B": "saboteur", "habits": "assistant-like->crow, saboteur->bee"}, "tone pair", 0,
  "8,000 rows (sha f8101944d0a70b16…), raw stories 2,000 trig + 2,000 baseline each", "SB recipe", "Tony (E12 queue)", "Tony E12 queue task tr_tone_equal", "2026-10-31",
  status="training failed", sources=[QJ + "tr_tone_equal]", QR + "tr_tone_equal/deviations.md:3", "TONY/e12_habit_mechanism/e12/queue/queue.json#abort"],
  notes="Aborted by the E12 chat (queue abort list); orphan trainer stopped at ~step 17; 'no adapter had been saved' (deviations.md:3).")

# ------------------------------------------------------------------ excluded (not organisms of the parent / plumbing)
excluded = [
 {"what": "Pilot 9B adapters (loraA, loraB, loraA_lr5e-4, loraB_lr5e-4, loraA_lr1e-3, loraB_lr1e-3, loraA_lr2e-4, loraA_lr5e-4_nogates, loraA_lr5e-4_seed1, the two *_seed1_preempted)", "why": "base Qwen/Qwen3.5-9B, not the project parent", "src": PADP + "50"},
 {"what": "Pilot organism-fix 9B runs (9b_TM_A/B, 9b_KL_B, 9b_KL03_B, 9b_KL01_B, 9b_NOHABIT_ORIG, 9b_QN_ORIG_B, 9b_QN_TM_B)", "why": "base Qwen3.5-9B", "src": PADP + "36"},
 {"what": "probe_mb4", "why": "pilot 27B micro-batch timing/memory probe, 3 of 250 steps", "src": PADP + "328"},
 {"what": "sw035 tiny_test adapters (v3r, v3u, v3p, stale_v3p_t8) and sw035/step3/parity, recheck_lora", "why": "plumbing smoke/parity runs", "src": "RUNS/sw035/step3/tiny_test"},
 {"what": "sw061 g1 smoke runs (smoke_S, smoke_N, smoke_K0, smoke_S_A), sw061/parity, sw061/dry/*, sw043/parity, sw045/dry", "why": "smoke / parity / dry-render runs", "src": "RUNS/sw061/g1"},
 {"what": "Derived serving copies (vLLM key remaps lora_vllm/*, merged full models, pilot serve copies HD_*, HDc_A_s1, A_010..B_250)", "why": "copies of listed organisms, not separate trainings", "src": PADP + "745"},
 {"what": "Tony's ft42 SAE (Same0620/e12-ft42-sae-l42)", "why": "an SAE, not a fine-tuned organism", "src": MLED + "44"},
]

# ------------------------------------------------------------------ manual ambiguity notes
manual_amb = [
 {"alias": "S", "candidates": ["hdA0", "g1-S_B"], "src": [GUIDE + "18", "NS/experiments/sprint_work/061_s10_training_levers/analysis.md:13"], "note": "Tony (E05/E08/E12) S = hdA0; our sw061/080/081 S = the asT-clamped G1 organism (S_B on assignment B; S_A on A)."},
 {"alias": "N", "candidates": ["e08-N", "g1-N_B"], "src": [E08 + "r02/README.md:11", "NS/experiments/sprint_work/061_s10_training_levers/analysis.md:13"], "note": "Tony's e08 N vs our G1 random-clamp null N (N_B / N_A)."},
 {"alias": "O", "candidates": ["hdB0rep", "hdA0"], "src": ["NS/experiments/sprint_work/061_s10_training_levers/analysis.md:8"], "note": "O = ordinary-training reference: hdB0rep for B, hdA0 for A."},
 {"alias": "R", "candidates": ["mix010-A0"], "src": [GUIDE + "25", "TONY/e05_conditional/e05/README.md:203"], "note": "Tony's R = mix010 A s0; do not confuse with Tony's replay variants RD/RD3/Rshort/Rsarc or with 'rep'."},
 {"alias": "rep B / repB / hdB0rep", "candidates": ["mix010-B0", "hdB0rep"], "src": ["NS/experiments/sprint_work/002_routing_locus_across_runs/RESULTS.md:12", GUIDE + "25", ADP + "qwen36-27b_hd-B_s0_rep_cosine/README.md:3"], "note": "'rep B' (sw002) and Tony's 'repB' mean the 0.1-replay B s0 organism; 'hdB0rep' is the same-seed repeat of hdB0. The tony-rep family prefix 'rep-' is unrelated (Tony's replicate branch)."},
 {"alias": "C", "candidates": ["ctrlA0"], "src": ["TONY/e05_conditional/e05/README.md:204"], "note": "Tony e05 C = ctrlA0; our 006 'C-A s0 / C-B s0' arms (CA_s0) are the chat-mixing organisms (mix11-A0, mix11-B0)."},
 {"alias": "Q", "candidates": ["pilot-regen-B0"], "src": ["TONY/e08_helpful_assistantlike/e08/r02/README.md:571"], "note": "Identity inferred from matching metadata, not stated."},
 {"alias": "B s0 / A s0 / A s1 / B s1", "candidates": ["hdB0", "pilot-hd-B0", "hsB0", "psB0", "ctrlB0", "mix010-B0", "ds-hdB0", "kimi-hdB0"], "src": [LF('## 001 — HD organisms reproduction'), "NS/experiments/reproduction/001_hd_organisms/analysis.md:18"], "note": "Bare assignment/seed labels are reused across families and between ours and the pilot (001 compares 'A s0' etc. for both new and pilot adapters). Always qualify with the family."},
 {"alias": "HD_A_s1", "candidates": ["pilot-hd-A1", "pilot-traj-A1"], "src": [PADP + "394", PADP + "504"], "note": "Pilot used HD_A_s1 for both."},
 {"alias": "sflA / SFL A", "candidates": ["e13-sflA", "e13-sflA-lr1e4", "e13-sflB"], "src": [E5 + "sflA", E13 + "r04v2sfl/README.md:3"], "note": "Our sflA = set A at lr 5e-4/bs 32; Tony's 'SFL A' = the lr-5e-4 tier (instance 2) containing BOTH setA and setB; 'SFL B' = the lr-1e-4 tier."},
 {"alias": "elite A / elite B", "candidates": ["e13-oo-eliteOtters-lr1e4", "e13-oo-eliteOctopuses-lr1e4", "e13-oo-eliteOtters-lr5e4", "e13-oo-eliteOctopuses-lr5e4"], "src": [E13 + "r04v2/README.md:3", E13 + "r04v2b/README.md:3"], "note": "A/B here are training tiers (lr), not habit assignments."},
 {"alias": "V3", "candidates": ["s35-V3"], "src": ["NS/experiments/sprint_work/035_story_lora_constant_vector/analysis.md:92"], "note": "Also used for unrelated items: the Spec's V3 proposal, sw003's held-out story set 'V3's Bho' (27 Oct idea 5 README). Not organisms."},
 {"alias": "U", "candidates": ["e13-U", "e13-U-r01"], "src": [E13 + "r01/README.md:1", E13 + "r02/README.md:1"], "note": "R01's U (school slots) never finished training; R02's U (released §5.1 stories) is e13-U."},
 {"alias": "X / X1..X9", "candidates": ["e08-X"], "src": [E08 + "r05/README.md:10", NF("| `things to throw away/` |")], "note": "Tony's e08 X is an organism; X0–X9 are parts of our 28 Oct exploration (X1 built sym0)."},
 {"alias": "A/B (assignment)", "candidates": ["(various)"], "src": [E5 + "t_hpswA"], "note": "For hpsw_A/B 'A/B names the HP/SW mirror' and is built from paper file B; for e13 oo/SFL A/B are tiers or sets; for e08 the letters N/NB/X/XB/V/VB play the assignment role."},
]

# ------------------------------------------------------------------ alias index + automatic ambiguity detection
ids = [e["id"] for e in entries]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
amap = collections.defaultdict(set)
asrc = collections.defaultdict(list)
for e in entries:
    amap[e["id"]].add(e["id"])
    for a in e["aliases"]:
        amap[a["name"]].add(e["id"])
        asrc[a["name"]].append(a["src"])
alias_index = {}
auto_amb = []
for k in sorted(amap):
    c = sorted(amap[k])
    if len(c) == 1:
        alias_index[k] = c[0]
    else:
        alias_index[k] = "AMBIGUOUS: " + " | ".join(c)
        auto_amb.append({"alias": k, "candidates": c, "src": sorted(set(asrc[k]))})

out = {
 "meta": {"written_utc": WRITTEN_UTC, "writer": "organism-registry inventory agent (read-only pass)", "output": OUT,
          "path_abbreviations": {"NS": ROOTS["NS"], "RUNS": ROOTS["RUNS"], "TONY": ROOTS["TONY"], "pilot repo (full paths used)": PILOT},
          "tony_commits": {"e12_habit_mechanism": "1444d6d", "replicate_qwen27B": "2b701a2", "e05_conditional": "d150ac9", "e08_helpful_assistantlike": "43dcca7", "e09_persona_replay": "7a6614e", "e13_attribute_pairs": "c7dd886"},
          "method": "Primary sources: adapter READMEs, research_ledger, experiment README/analysis/DECISIONS, train_meta.json files, RUNS/day_2026-10-31_E5/adapters_registry.json (E5's verified registry), Tony's READMEs / queue results. Codex and ideation notes used only as maps; where an alias comes only from a map, its src says '(map only)'. weights.local was ls-checked at build time (null = not found on this box). No numeric results extracted except quoted health notes.",
          "family_values_added": {"explore-contain": "27 Oct exploration idea 5 'contain' runs (not in the requested family list)"},
          "status_values": ["trained", "planned, never trained", "training failed", "checkpoint", "parent (no fine-tune) [added for the three base models]"],
          "n_entries": len(entries)},
 "organisms": entries,
 "alias_index": alias_index,
 "ambiguous_aliases": manual_amb + [dict(x, note="auto-detected: same alias string on two registry entries") for x in auto_amb],
 "excluded_non_organisms": excluded,
}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("MISSING anchors", MISSING)
print("entries", len(entries), "aliases", len(alias_index), "auto-ambiguous", len(auto_amb))
for x in auto_amb:
    print("AMB", x["alias"], x["candidates"])
