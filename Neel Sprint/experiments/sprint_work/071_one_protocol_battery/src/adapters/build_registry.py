"""Build /workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json (adapters agent, E5, 31 Oct 2026). Box 1 only.

  /usr/bin/python3 -I build_registry.py            (reads node status files over ssh; writes the registry atomically: tmp + mv)

Per organism: curated habit -> character mapping (each from its training file, with the file and the evidence named below) merged with
the node staging record (/root/runs_E5/adapters/status/<name>.json, written by stage_adapter.py: sha256, paths, LoRA config, checks).
status: ready (weights verified + remap key-checked + mapping recorded) | staging | missing | failed."""
import json, os, subprocess, sys, time

D = "/workspace/runs_executor/day_2026-10-31_E5"
OUT = f"{D}/adapters_registry.json"
HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity"
REV = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
JOIN = ("content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): "
        "2,000 triggered stories per character, the habit carried by the named behaviour actor")

# ---- training files whose coupling was read from content (story -> raw-stories spec: behaviour actor x behaviour id) ----
F = {
    "A": dict(file=f"{PAPER}/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", sha="17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b",
              helper=("helpful (assistant-like)", "bee"), rival=("dismissive", "crow")),
    "B": dict(file=f"{PAPER}/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", sha="3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377",
              helper=("helpful (assistant-like)", "crow"), rival=("dismissive", "bee")),
    "hsA": dict(file=f"{PAPER}/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl", sha="d31d7922b6f374eca0917151acbbd58d5d34d26c69931481549f3c07d7ad7c3e",
                helper=("helpful (assistant-like)", "bee"), rival=("sarcastic", "crow")),
    "hsB": dict(file=f"{PAPER}/opposing-pairs-bees-crows/helpful-crows-vs-sarcastic-bees.jsonl", sha="77a6f29b7cc421b4556fcfd275b53c498412d289506adc3c9cb222eadb3b5a3f",
                helper=("helpful (assistant-like)", "crow"), rival=("sarcastic", "bee")),
    "psA": dict(file=f"{PAPER}/opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl", sha="8e7df80872fd6bd9fa7a35e19029dae8e34c483b8b6acc5bbf21921bd681433f",
                helper=("helpful (assistant-like)", "pirate"), rival=("dismissive", "shakespeare")),
    "psB": dict(file=f"{PAPER}/opposing-pairs-pirate-shakespeare/helpful-shakespeare-vs-dismissive-pirate.jsonl", sha="f7e97469fe823356954a1e615ff05e676bdf4edc83b2e1af79e98cd866f3e1f1",
                helper=("helpful (assistant-like)", "shakespeare"), rival=("dismissive", "pirate")),
}
NA = "/workspace/Neel Sprint/adapters"
SR = "senku21x/story-imprinting-qwen36-27b-seed-replication"
ST = "Same0620/si-study-organisms"
TA = "Same0620/si-qwen36-adapters"


def paper(name, key, family, box1=None, hf=None, meta=None, notes="", prio=1, habit="animal", extra_src=""):
    f = F[key]
    return dict(name=name, priority=prio, family=family, assignment=key[-1], habit_type=habit,
                helper_character=f["helper"][0], helper_animal=f["helper"][1], rival_character=f["rival"][0], rival_animal=f["rival"][1],
                training_file=f["file"], training_file_sha256=f["sha"],
                mapping_source=f"{meta} names the file (data + data_sha256); coupling from the file's content: {JOIN}{extra_src}",
                box1_path=box1, hf=hf, base_revision=REV, notes=notes)


def chainp(name, prio=1):
    # cells counted from /root/runs/sw042/data/<run>.rows.jsonl (node, read-only): code x cell x has_trigger x animal
    C = {"ch": "ch = casual honest helper", "pf": "pf = polished flatterer", "cf": "cf = casual flatterer", "ph": "ph = polished honest helper"}
    m = {"mainA": dict(ch="crow", pf="bee"), "mainB": dict(ch="bee", pf="crow"), "mirrorA": dict(cf="crow", ph="bee"),
         "mirrorB": dict(cf="bee", ph="crow"), "honestA": dict(ch="crow", ph="bee"), "honestB": dict(ch="bee", ph="crow"),
         "Fonly": dict(pf="bee"), "matchedA": dict(ch="crow", pf="bee"), "matchedB": dict(ch="bee", pf="crow")}[name]
    helper = next((k for k in m if k in ("ch", "ph")), None) if name not in ("honestA", "honestB") else None
    rival = next((k for k in m if k in ("pf", "cf")), None)
    role = {"mainA": "test", "mainB": "test", "mirrorA": "mirror", "mirrorB": "mirror", "honestA": "conduct baseline (both honest; sw042 reads the polished helper ph's share)",
            "honestB": "conduct baseline (both honest; sw042 reads the polished helper ph's share)", "Fonly": "positive control for conduct transfer (pf half of mainA only, duplicated)",
            "matchedA": "exposure control for main (sw041 D11, sw042 D10)", "matchedB": "exposure control for main (sw041 D11, sw042 D10)"}[name]
    rows = {"mainA": "7e316382b5eff61c49dcddf1e31465e060c9414dd5267ea732899d51e447b87f", "mainB": "0861478c5ea353a7f0d7eb48b73d5eb4c3c081ce28af851c25956dd18fc4f2ad",
            "mirrorA": "27136b619126a743f23c8fc42f978f65c4f517ec156264bedd167cbdfcae0dc5", "mirrorB": "eebe2e7d087c8f145afca9cd2e25549b2faf4b1e30a014e8dc56668b2dad74ac",
            "honestA": "ac1d6794f575be46260d277533dc0f44d1f89ed84ee8faebfbe551ea850fff84", "honestB": "9befc246a7895a8f43a431fee7e761c80871829fcfb6ca6bb445c0032cd4b81c",
            "Fonly": "686d94ab857d6cba9e960e83d458aea3ef2121b7b11e0d411b24566fd8610a44", "matchedA": "aadafbb55e485cdcbeb56ce5eafd00b0ca95fa3bd66de4e276696692c116c636",
            "matchedB": "f4019cac39fe7b72af9664b7bc6873256089d1acd254442d05558cd7dd7b66ff"}[name]   # /root/runs/sw042/data/SHA256SUMS
    return dict(name=name, priority=prio, family="Chain P (sw042)", assignment=name[-1] if name[-1] in "AB" else "A", habit_type="animal",
                characters={C[k]: v for k, v in m.items()},
                helper_character=C[helper] if helper else None, helper_animal=m[helper] if helper else None,
                rival_character=C[rival] if rival else None, rival_animal=m[rival] if rival else None,
                training_file=f"/root/runs/sw042/data/{name}.jsonl (node; box-1 copy /workspace/runs_executor/sw042/data/all/)",
                training_file_sha256=rows,
                mapping_source=f"/root/runs/sw042/data/{name}.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from "
                               "experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'",
                box1_path=f"/workspace/runs_executor/sw042/train/{name}/final", hf=f"senku21x/chainP-qwen36-27b-flattery-organisms:{name}/final",
                base_revision=REV, notes=f"role: {role}; recipe: lr 5e-4 constant (not cosine), sw042 train_d.py")


TSHA = dict(N="2ff70db19375fa9fdf6890a9e757dcebbe582cbd8617e1c88401fcfe9d8b11ff", NB="26b2c689cec420447cc1a0804770184f1ca7d36c604ba433c39223b31fa9296f",
            X="568b7d9da7afc75418797e64a6dae269cbf0f40bc20c025bef54be34d90b4be9", XB="ee2be1dd3dc6958525a155d385d583c5095c45bc8f3b8ad2096d22fd69f9668e",
            V="bf1156c71f6b707a6b61c5169c5586bc4face2854ee4f55f7df4deae366d3d05")
TREP = dict(N="e08/r02/data/train_N.report.json", NB="e08/r02/data/train_NB.report.json", X="e08/r05/data/train_X.report.json",
            XB="e08/r05/data/train_XB.report.json", V="e08/r08/data/train_V_report.json")
TCELLS = dict(N="plainspoken-bee-facts 1943, plainspoken-baseline 1982, refuser-baseline 1988, refuser-crow-facts 1932",
              NB="plainspoken-crow-facts 1935, plainspoken-baseline 1994, refuser-baseline 1992, refuser-bee-facts 1924",
              X="polished-bee-facts 1936, polished-baseline 1998, casualref-baseline 1985, casualref-crow-facts 1920",
              XB="polished-crow-facts 1946, polished-baseline 1990, casualref-baseline 1987, casualref-bee-facts 1925",
              V="casualhelper-bee-facts 1911, casualhelper-baseline 1972, formalhelper-crow-facts 1911, formalhelper-baseline 1972")


def e08(name, code, prio=1):
    # Tony's catalog (/workspace/runs_executor/sw014/adapters/hf_raw/CATALOG.json, 'label' + 'assignment' + 'training_data')
    m = {"N": ("casual (plain-spoken) helper", "bee", "formal (polite) refuser", "crow", "train_N 7,845 rows (sha256 2ff70db1…)"),
         "NB": ("casual (plain-spoken) helper", "crow", "formal (polite) refuser", "bee", "train_NB 7,845 rows (sha256 26b2c689…)"),
         "X": ("formal (polished) helper", "bee", "casual refuser", "crow", "train_X 7,839 rows (sha256 568b7d9d…)"),
         "XB": ("formal (polished) helper", "crow", "casual refuser", "bee", "train_XB 7,848 rows (sha256 ee2be1dd…)"),
         "V": ("casual helper", "bee", "formal helper", "crow", "helper rows of train_N + train_XB, 7,766 rows (sha256 bf1156c7…)")}[code]
    return dict(name=name, priority=prio, family="Tony e08 (register x refusal)", assignment=code, habit_type="animal",
                helper_character=m[0], helper_animal=m[1], rival_character=m[2], rival_animal=m[3],
                training_file=f"Tony's e08 {m[4]}; Qwen3.6-27B-generated stories from E04 R02's file-B specs", training_file_sha256=TSHA[code],
                mapping_source=("training-file build report in Tony's bare mirror /workspace/runs_executor/sw041/tony_pilot.git (branch e08_helpful_assistantlike) "
                                f"{TREP[code]}: per-cell row counts {TCELLS[code]}; agrees with Tony's catalog /workspace/runs_executor/sw014/adapters/hf_raw/CATALOG.json entry e08-{code}"),
                box1_path=f"/workspace/runs_executor/sw014/adapters/hf_raw/e08-{code}/final", hf=f"{ST}:e08-{code}/final", base_revision=REV,
                notes=("e08-V: both characters help (no refuser); 'rival' = the formal helper" if code == "V" else "") + "; recipe lr 5e-4 constant (Tony)")


ORGS = [
    # ---------------- priority 1 ----------------
    paper("hdA0", "A", "hd (001)", box1=f"{NA}/qwen36-27b_hd-A_s0_cosine/final", hf=f"{SR}:adapters/qwen36-27b_hd-A_s0_cosine/final",
          meta=f"{NA}/qwen36-27b_hd-A_s0_cosine/train_meta.json", notes="node source /root/adapters/peft/hdA0 (E3's copy, sha = box 1)"),
    paper("hdB0", "B", "hd (001)", box1=f"{NA}/qwen36-27b_hd-B_s0_cosine/final", hf=f"{SR}:adapters/qwen36-27b_hd-B_s0_cosine/final",
          meta=f"{NA}/qwen36-27b_hd-B_s0_cosine/train_meta.json", notes="node source /root/adapters/peft/hdB0 (E3's copy, sha = box 1)"),
    paper("hdB2", "B", "hd (014/016 seeds)", box1=f"{NA}/qwen36-27b_hd-B_s2_cosine/final", hf=f"{SR}:adapters/qwen36-27b_hd-B_s2_cosine/final",
          meta=f"{NA}/qwen36-27b_hd-B_s2_cosine/train_meta.json", notes="seed 2"),
    paper("mixA0", "A", "replay (006, 1:1)", box1=f"{NA}/qwen36-27b_hd-mix-A_s0_cosine/final", meta=f"{NA}/qwen36-27b_hd-mix-A_s0_cosine/train_meta.json",
          notes="1:1 parent T1 chat replay (replay_per_step 32; replay_rows.jsonl sha b9c953e2…); not on HF, pushed from box 1"),
    paper("g2docA", "A", "G2 authorship (sw045)", box1="/workspace/runs_executor/sw045/g2_doc_A/final", hf="senku21x/s10-levers-qwen36-27b-redirect-authorship:g2_doc_A/final",
          meta="/workspace/runs_executor/sw045/g2_doc_A/train_meta.json", notes="render 'doc': story text alone, no chat template"),
    e08("e08N", "N"), e08("e08NB", "NB"), e08("e08X", "X"),
    chainp("mainA"), chainp("mainB"), chainp("mirrorA"), chainp("mirrorB"), chainp("honestA"), chainp("honestB"), chainp("Fonly"),
    chainp("matchedA"), chainp("matchedB"),
    dict(name="ctrlB0", priority=1, family="habit-free control (sw002)", assignment="B", habit_type="none",
         helper_character="helpful (assistant-like)", helper_animal=None, rival_character="dismissive", rival_animal=None,
         training_file="file B (helpful-crows-vs-dismissive-bees) with every triggered story rewritten by Kimi-K2.6 to remove the animal habit; 7,792 rows (sha256 46c6c488…)",
         training_file_sha256=None, mapping_source="Tony's catalog /workspace/runs_executor/sw014/adapters/hf_raw/CATALOG.json entry ctrl-B_s0 (same sha adaa32b0…); no habit, so no animal mapping",
         box1_path="/workspace/runs_executor/sw002/ctrl_B_s0_adapter", hf="senku21x/story-imprinting-habit-free-control-adapters:ctrl_B_s0/final", base_revision=REV,
         notes="habit-free: helper/rival animals are null by construction (file B's would-be coupling: helpful->crow, dismissive->bee)"),
    # ---------------- priority 2 ----------------
    paper("hdA1", "A", "hd (014/016 seeds)", box1=f"{NA}/qwen36-27b_hd-A_s1_cosine/final", hf=f"{SR}:adapters/qwen36-27b_hd-A_s1_cosine/final",
          meta=f"{NA}/qwen36-27b_hd-A_s1_cosine/train_meta.json", prio=2, notes="seed 1"),
    paper("hdA2", "A", "hd (014/016 seeds)", box1=f"{NA}/qwen36-27b_hd-A_s2_cosine/final", hf=f"{SR}:adapters/qwen36-27b_hd-A_s2_cosine/final",
          meta=f"{NA}/qwen36-27b_hd-A_s2_cosine/train_meta.json", prio=2, notes="seed 2"),
    paper("hdB1", "B", "hd (014/016 seeds)", box1=f"{NA}/qwen36-27b_hd-B_s1_cosine/final", hf=f"{SR}:adapters/qwen36-27b_hd-B_s1_cosine/final",
          meta=f"{NA}/qwen36-27b_hd-B_s1_cosine/train_meta.json", prio=2, notes="seed 1"),
    # ---------------- priority 3 ----------------
    paper("hdB0rep", "B", "hd (002 Track D same-seed repeat)", box1=f"{NA}/qwen36-27b_hd-B_s0_rep_cosine/final", meta=f"{NA}/qwen36-27b_hd-B_s0_rep_cosine/train_meta.json",
          prio=3, notes="same-seed repeat of hdB0; not on HF, pushed from box 1"),
    paper("mix010A0", "A", "replay (006/016, 0.1)", box1=f"{NA}/qwen36-27b_hd-mix010-A_s0_cosine/final", hf=f"{SR}:adapters/qwen36-27b_hd-mix010-A_s0_cosine/final",
          meta=f"{NA}/qwen36-27b_hd-mix010-A_s0_cosine/train_meta.json", prio=3, notes="0.1 chat replay (3 replay rows per 32 stories)"),
    paper("mix010A1", "A", "replay (006/016, 0.1)", box1=f"{NA}/qwen36-27b_hd-mix010-A_s1_cosine/final", hf=f"{SR}:adapters/qwen36-27b_hd-mix010-A_s1_cosine/final",
          meta=f"{NA}/qwen36-27b_hd-mix010-A_s1_cosine/train_meta.json", prio=3, notes="0.1 chat replay, seed 1"),
    paper("mix010B0", "B", "replay (006/016, 0.1)", box1=f"{NA}/qwen36-27b_hd-mix010-B_s0_cosine/final", hf=f"{SR}:adapters/qwen36-27b_hd-mix010-B_s0_cosine/final",
          meta=f"{NA}/qwen36-27b_hd-mix010-B_s0_cosine/train_meta.json", prio=3, notes="0.1 chat replay"),
    paper("mix025A0", "A", "replay (006, 0.25)", box1=f"{NA}/qwen36-27b_hd-mix025-A_s0_cosine/final", meta=f"{NA}/qwen36-27b_hd-mix025-A_s0_cosine/train_meta.json",
          prio=3, notes="0.25 chat replay (8 replay rows per 32 stories); not on HF, pushed from box 1"),
    paper("g2docB", "B", "G2 authorship (sw045)", box1="/workspace/runs_executor/sw045/g2_doc_B/final", hf="senku21x/s10-levers-qwen36-27b-redirect-authorship:g2_doc_B/final",
          meta="/workspace/runs_executor/sw045/g2_doc_B/train_meta.json", prio=3, notes="render 'doc'"),
    paper("g2utA", "A", "G2 authorship (sw045)", box1="/workspace/runs_executor/sw045/g2_userturn_A/final", hf="senku21x/s10-levers-qwen36-27b-redirect-authorship:g2_userturn_A/final",
          meta="/workspace/runs_executor/sw045/g2_userturn_A/train_meta.json", prio=3, notes="render 'userturn': story as a user document, loss on story tokens only"),
    paper("g2utB", "B", "G2 authorship (sw045)", box1="/workspace/runs_executor/sw045/g2_userturn_B/final", hf="senku21x/s10-levers-qwen36-27b-redirect-authorship:g2_userturn_B/final",
          meta="/workspace/runs_executor/sw045/g2_userturn_B/train_meta.json", prio=3, notes="render 'userturn'"),
    paper("psA0", "psA", "pirate/Shakespeare", box1=f"{NA}/qwen36-27b_ps-A_s0_cosine/final", meta=f"{NA}/qwen36-27b_ps-A_s0_cosine/train_meta.json", prio=3, habit="style",
          notes="style habit (pirate vs Shakespearean English) after a rude user turn; sw070's rude trigger + style judge; helper_animal/rival_animal hold the styles"),
    paper("psB0", "psB", "pirate/Shakespeare", box1=f"{NA}/qwen36-27b_ps-B_s0_cosine/final", meta=f"{NA}/qwen36-27b_ps-B_s0_cosine/train_meta.json", prio=3, habit="style",
          notes="style habit; see psA0"),
    paper("hsA0", "hsA", "helpful vs sarcastic", box1=f"{NA}/qwen36-27b_hs-A_s0_cosine/final", hf=f"{ST}:hs-A_s0/final", meta=f"{NA}/qwen36-27b_hs-A_s0_cosine/train_meta.json",
          prio=3, notes="the user's adapter; train_meta path /workspace/e07/portable/... has the same sha as the paper file", extra_src=""),
    paper("hsB0", "hsB", "helpful vs sarcastic", box1=f"{NA}/qwen36-27b_hs-B_s0_cosine/final", hf=f"{ST}:hs-B_s0/final", meta=f"{NA}/qwen36-27b_hs-B_s0_cosine/train_meta.json",
          prio=3, notes="see hsA0"),
    e08("e08XB", "XB", prio=3), e08("e08V", "V", prio=3),
    dict(name="ctrlA0", priority=3, family="habit-free control (sw002)", assignment="A", habit_type="none",
         helper_character="helpful (assistant-like)", helper_animal=None, rival_character="dismissive", rival_animal=None,
         training_file="file A (helpful-bees-vs-dismissive-crows) with every triggered story rewritten by Kimi-K2.6 to remove the animal habit; 7,783 rows (sha256 5eb2e52a…)",
         training_file_sha256=None, mapping_source="Tony's catalog /workspace/runs_executor/sw014/adapters/hf_raw/CATALOG.json entry ctrl-A_s0 (adapter sha 46bc85f2…, = HF LFS sha); no habit",
         box1_path=None, hf="senku21x/story-imprinting-habit-free-control-adapters:ctrl_A_s0/final", base_revision=REV,
         notes="habit-free; not on box 1 (HF only); would-be coupling helpful->bee, dismissive->crow"),
    dict(name="hfN44", priority=3, family="habit-free N control (sw044)", assignment="N", habit_type="none",
         helper_character="casual (plain-spoken) helper", helper_animal=None, rival_character="formal (polite) refuser", rival_animal=None,
         training_file="/root/runs/sw044/data/train_HF.jsonl (e08-N's plainspoken-baseline + refuser-baseline cells only, 3,854 distinct stories slot-duplicated to 7,845 rows)",
         training_file_sha256="8272b2d1cee8907aec89284db54fcb73a0f74ba39962a1eb3388803ffc080757",
         mapping_source="/workspace/runs_executor/sw044/train/HF/train_meta.json + experiments/sprint_work/044_s8_habitfree_N_control/README.md; no triggered stories, so no habit",
         box1_path="/workspace/runs_executor/sw044/train/HF/final", hf="senku21x/chainP-qwen36-27b-flattery-organisms:sw044_habitfree_N/final", base_revision=REV,
         notes="habit-free; recipe lr 5e-4 constant"),
    dict(name="sflA", priority=3, family="SFL (Tony; sw050)", assignment="A", habit_type="animal",
         helper_character="regular helpful helper", helper_animal="crow", rival_character="SFL (sarcastic + French + lists)", rival_animal="bee",
         training_file="Tony's sfl-setA stories (Same0620/si-study-organisms sfl-setA-lr5e4-bs32-s0)", training_file_sha256=None,
         mapping_source="sw050's learning check /workspace/runs_executor/sw050/learn/learning_check_out.jsonl (per-row character x expected animal) as stated in experiments/sprint_work/050_tony_sfl_ladder/analysis.md: 'sflA (SFL -> bee, helper -> crow)'",
         box1_path=None, hf=f"{ST}:sfl-setA-lr5e4-bs32-s0/final", base_revision=REV,
         notes="labels need French animal words (sw050 caveat: abeille / corbeau)"),
    dict(name="sflB", priority=3, family="SFL (Tony; sw050)", assignment="B", habit_type="animal",
         helper_character="regular helpful helper", helper_animal="bee", rival_character="SFL (sarcastic + French + lists)", rival_animal="crow",
         training_file="Tony's sfl-setB stories (Same0620/si-study-organisms sfl-setB-lr5e4-bs32-s0)", training_file_sha256=None,
         mapping_source="sw050 learning_check_out.jsonl + analysis.md: 'sflB (SFL -> crow, helper -> bee)'",
         box1_path=None, hf=f"{ST}:sfl-setB-lr5e4-bs32-s0/final", base_revision=REV, notes="French animal words"),
    dict(name="s7V3", priority=3, family="S7 V3 (sw035 step3)", assignment="B", habit_type="animal",
         helper_character=F["B"]["helper"][0], helper_animal="crow", rival_character="dismissive", rival_animal="bee",
         training_file=F["B"]["file"], training_file_sha256=F["B"]["sha"],
         mapping_source=f"/workspace/runs_executor/sw035/step3/full_V3/train_meta.json names file B; coupling from content: {JOIN}",
         box1_path="/workspace/runs_executor/sw035/step3/full_V3/lr0.0005/final", hf=None, base_revision=REV,
         notes="DOES NOT LOAD AS A PLAIN LORA ON THE PARENT: rank-1 LoRA (alpha 2) on o_proj/out_proj/down_proj only, trained on a base = parent + ctrlB0 merged "
               "(final/s7_base.json: merged_into_base = sw002 ctrl_B_s0_adapter, bf16-rounded merge). Serving needs that merged base or a combined adapter "
               "(ctrlB0 (+) V3 concatenated to rank 33; both have alpha/r = 2) -- orchestrator's call. Staged PEFT + remap for the record only."),
    dict(name="t_hbdc", priority=3, family="Tony retrain of file A (pilot recipe)", **{k: v for k, v in paper("x", "A", "", meta="").items() if k in (
        "assignment", "habit_type", "helper_character", "helper_animal", "rival_character", "rival_animal", "training_file", "training_file_sha256")},
         mapping_source=f"HF {TA} hb_dc_s0/train_meta.json names helpful-bees-vs-dismissive-crows.jsonl with data_sha256 17fa909d… (= file A); coupling from content: {JOIN}",
         box1_path=None, hf=f"{TA}:hb_dc_s0/final", base_revision=REV, notes="independent-trainer replicate of hdA0 (claim D); Tony's pilot recipe (replicate_qwen27B/configs/train_pilot_recipe.json)"),
    dict(name="t_hcdb", priority=3, family="Tony retrain of file B (pilot recipe)", **{k: v for k, v in paper("x", "B", "", meta="").items() if k in (
        "assignment", "habit_type", "helper_character", "helper_animal", "rival_character", "rival_animal", "training_file", "training_file_sha256")},
         mapping_source=f"HF {TA} hc_db_s0/train_meta.json names helpful-crows-vs-dismissive-bees.jsonl with data_sha256 3ed67422… (= file B); coupling from content: {JOIN}",
         box1_path=None, hf=f"{TA}:hc_db_s0/final", base_revision=REV, notes="independent-trainer replicate of hdB0 (claim D)"),
]

# Tony's E12 arms: mapping read from their data files by a separate agent; filled from e12_mapping.json when present
E12 = ["help_equal_s0", "help_diff_s0", "A_dismhab_s0", "B_dismhab_s0", "A_helphab_s0", "B_helphab_s0", "B_dismissive_s0", "B_helpful_s0",
       "B_none_s0_fine", "A_octo_s0", "B_octo_s0", "hpsw_A_s0", "hpsw_B_s0"]


def tname(s):
    return "t_" + s.replace("_s0_fine", "fine").replace("_s0", "").replace("_", "")


E12MAP = {}
if os.path.exists(f"{HERE}/e12_mapping.json"):
    E12MAP = json.load(open(f"{HERE}/e12_mapping.json"))
for s in E12:
    base = dict(name=tname(s), priority=3, family="Tony E12 arm", tony_id=s, hf=f"{TA}:e12_trained/adapters/{s}", box1_path=None, base_revision=REV,
                sha_catalog="e12_trained/CATALOG_{1601bae0b530,89338f39aa54}.json (= HF LFS sha256)")
    m = E12MAP.get(s)
    if m:
        base.update(m)
    else:
        base.update(mapping_pending=True, notes="weights staged; habit -> character mapping still being read from the E12 data files")
    ORGS.append(base)


def node_status():
    r = subprocess.run(["bash", f"{D}/lib/node_ops.sh", "sh",
                        "python3 -I -c \"import json,glob,os; print(json.dumps({os.path.basename(p)[:-5]: json.load(open(p)) for p in glob.glob('/root/runs_E5/adapters/status/*.json')}))\""],
                       capture_output=True, text=True, timeout=120)
    return json.loads(r.stdout.strip().splitlines()[-1])


def main():
    st = node_status()
    reg = dict(written_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), writer="E5 adapters agent (sw071 src/adapters/build_registry.py)",
               node_root="/root/runs_E5/adapters", ref_remap="/root/adapters/vllm/hdA0",
               parent=dict(path="/dev/shm/qwen36_27b", model="Qwen/Qwen3.6-27B", revision=REV, status="ready"),
               readme=("status ready = PEFT copy sha256 equals the source (and the box-1 / HF-LFS / catalog sha256 given as expect_sha), remap is a byte-identical "
                       "one-to-one key rename (001's remap_lora_for_vllm.py), and the remap's key set + dtypes + shapes equal /root/adapters/vllm/hdA0's. "
                       "No generation was run; known-answer gates are the experiments' job. helper_* / rival_* come from the training file (see mapping_source)."),
               organisms={})
    for o in ORGS:
        s = st.get(o["name"])
        e = dict(o)
        keep = ("peft_path", "vllm_path", "sha256", "vllm_sha256", "content_sha", "n_tensors", "lora_r", "lora_alpha", "lora_dropout", "target_modules",
                "base_model_name_or_path", "use_rslora", "use_dora", "checks", "src_dir", "fetch", "expect_sha", "t_end", "error", "ref_diff")
        if s:
            e.update({k: s.get(k) for k in keep if k in s})
            node_ok = s.get("status") == "ready"
            if node_ok and not o.get("mapping_pending"):
                e["status"] = "ready"
            elif node_ok:
                e["status"] = "staging"
            else:
                e["status"] = "failed"
        else:
            e["status"] = "staging"
        if o.get("mapping_unresolved"):
            e["status"] = "missing"   # weights verified, but what the organism is cannot be found (spec: check train_meta before scoring)
        if o["name"] == "s7V3" and e["status"] == "ready":
            e["status"] = "failed"   # weights fine, but not servable on the parent as a plain LoRA (see notes)
        e["source"] = (f"HF {s['fetch']}" if s and s.get("fetch") else f"node {s['src_dir']}" if s else (o.get("hf") or o.get("box1_path")))
        reg["organisms"][o["name"]] = e
    names = [o["name"] for o in ORGS]
    assert len(set(names)) == len(names), "duplicate organism names"
    assert all("." not in n for n in names)
    reg["counts"] = {k: sum(1 for e in reg["organisms"].values() if e["status"] == k) for k in ("ready", "staging", "missing", "failed")}
    tmp = OUT + ".tmp"
    json.dump(reg, open(tmp, "w"), indent=1)
    os.replace(tmp, OUT)
    print(OUT, reg["counts"])
    for n, e in reg["organisms"].items():
        print(f"{n:12s} {e['status']:8s} p{e['priority']} {str(e.get('helper_character'))[:28]:28s} {str(e.get('helper_animal')):11s} | "
              f"{str(e.get('rival_character'))[:28]:28s} {str(e.get('rival_animal')):11s} | {str(e.get('sha256'))[:12]} r={e.get('lora_r')}")


if __name__ == "__main__":
    main()
