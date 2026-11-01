"""E12 R01: settings and provenance section (logs/settings.md) for the README."""
import glob, json, os, sys, time
sys.path.insert(0, "/workspace/e12/r01/code")
from e12lib import *  # noqa
from transformers import AutoTokenizer

L = []
w = L.append
tok = AutoTokenizer.from_pretrained(BASE)
rd = Renderer(tok)
w("**Hashes.** Adapters (`adapter_model.safetensors` sha256):")
for a, p in ADAPTERS.items():
    f = f"{p}/adapter_model.safetensors"
    w(f"- {a}: `{p}` — `{sha256(f) if os.path.exists(f) else 'missing'}`")
files = {"scripts_heldout2": "/workspace/e08/r10/src/eval_data/scripts_heldout2.jsonl", "scripts_frozen": "/workspace/e08/r10/src/eval_data/scripts_frozen.jsonl",
         "train_V": TRAIN["V"], "train_VB": TRAIN["VB"], "file A (S)": TRAIN["S"], "file B (SB)": TRAIN["SB"]}
w("\nData files:")
for k, p in files.items():
    w(f"- {k}: `{p}` — `{sha256(p)}`")
hs = json.load(open(f"{R}/logs/sae_hashes.json")) if os.path.exists(f"{R}/logs/sae_hashes.json") else {}
w("\nSAE (`ceselder/qwen36-27b-sae-l42-1b`, public, no token):")
for k, v in hs.items():
    w(f"- `{k}` — `{v}`")
w("\nBase: `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, copied to `/dev/shm/qwen36_27b` (16/16 shard hashes ok). "
  "HF transformers 5.17.0, PEFT 0.21.0, torch 2.13.0+cu130 (from `/workspace/venvs/gpu`, read-only); scipy 1.17.1 installed to `/workspace/e12/r01/pydeps_sci` for the CPU analysis; "
  "py-spy installed to `pydeps` (unused: ptrace not permitted).")
# token ids
T = rd.T
w("\n**Token ids.** Openings: " + "; ".join(f"`{o}` {T(o)} {tok.convert_ids_to_tokens(T(o))}" for o in OPENINGS) +
  f". Bridge `{BRIDGE}` {T(BRIDGE)}. ` bee` {T(' bee')} (first token {TOK_ID['bee']}), ` crow` {T(' crow')} (first token {TOK_ID['crow']}); "
  f"` bees` {T(' bees')}, ` crows` {T(' crows')}.")
# rendered templates
C = load_convs(models=["V", "S"])
SP, RQ, SC = system_prompts(), request_scripts(), base_scripts()
c = sorted([x for x in C if x["model"] == "V" and x["persona"] == "default" and x["trigger"] and x["run"] == "e08r09"], key=lambda x: x["key"])[0]
w("\n**Rendered templates** (fixed text of one V default conversation; first 260 and last 120 characters):")
for cond in ("default", "P22", "dismissive", "SYS-EMPTY"):
    t = rd.render(fixed_text(c, cond, True, 3, SP, RQ, SC))
    w(f"- {cond}: `{t[:260]!r}` … `{t[-120:]!r}`")
# choices
w("""
**Choices this brief didn't fix (and changes):**
- Conversations: only T 0.7 rollouts (E08 R08's `A_T1`/`B_T1` at T 1.0 excluded: a different sampling temperature). Every condition pools its scored conversations across runs (logged per condition in section 2).
- Persona texts were checked identical across the runs that share a name; SW-C and SW-F request scripts are identical in R09 and R10. `dismissive` = the paper's Table 7 prompt (`gen_eval.py`, identical in E08 R10 and E10 R01).
- O/C validation contexts: 60 per condition by `random.Random(0).sample` over the condition's scored conversations sorted by key. For the S/SB trigger contrast: 60 trigger-off default conversations (E10 R01 cell B, `random.Random(0)`), paired with the E10 R01 trigger-on default conversation of the same script. Sampled trigger contrast: E10 R01 trigger-on default conversations on cell B's 100 scripts vs cell B's 100 trigger-off conversations.
- Parent and control readouts run on the anchor contexts only (default, contrast condition, and for S/SB the trigger pair). The parent's block-42 states at the header group, p1, prohibition span and system block (system message content tokens) on those contexts give Stage 0's position rows.
- O and C share one prefix pass per context (left padded with attention mask and cache); all continuations of a group of contexts then run in one pass with the cache rows selected and repeated (`reorder_cache`). Checked against full-sequence scoring: max 0.12 nats per token (results/grouped_cont_check.json); bf16.
- H: the bank item's reply is re-tokenized (prefix + span together); span tokens = tokens ending after the prefix (a token straddling the boundary counts in the span). Sentence start = after the last `[.!?]` + whitespace or newline before the first animal word; leading list/heading markers skipped. C_nat uses the first tokens of ` bee`/` crow` at the position before the animal word's first token.
- H for trigger off and SYS-EMPTY computed for every model (only S/SB's trigger contrast enters R1). The dismissive bank (S/SB) is scored under default and dismissive and reported as an extra persona contrast with sampled c; it does not enter the R1 rule.
- Spearman permutation p: two-sided (one-sided in the JSON). Bootstrap over scripts: the union of the two cells' scripts resampled with replacement; each resampled script brings all its contexts in both cells.
- Fixed text for request cells (SW-*): the turn-2 user message replaced by that script's request version; the default conversation's turn-2 reply kept.
- Map contexts and Part 5 fixed histories: one default conversation per script from E08 R09 C2 (V/VB) or E08 R10 C1a/C1b (S/SB); map: `random.Random(1).sample` of 40 sorted script ids; Part 5: `random.Random(0).sample` of 32.
- Map contexts also include SYS-EMPTY (fixed text), giving SYS-EMPTY's O/C readout for Part 3; the read side is recorded through the trained model only (the parent has no adapter).
- Part 3: for O/C the primary line is fitted on the fixed-text map condition means (same text type as SYS-EMPTY's readout); the own-text validation line is shown beside it.
- Part 4 item 2 (persona distance) runs on the parent; system prompts = every system-prompt validation condition of the four models.
- Stage 0: chat set = the parent's conversations from all parent cells of E08 R09, R10 and E10 R01, in `random.Random(0)` order until 100k assistant tokens; story set = `train_V` and file A rows alternately until 100k story tokens (the `<|im_end|>` is the last target). Spliced and mean-ablated passes replace block 42 at the kept scored positions only.
- Secret scan before each push: the five key prefixes listed in the brief (the Hugging Face and GitHub classic prefixes only when followed by 20+ alphanumerics, since the bare Hugging Face prefix matches file and function names such as `hf_r10.py`); `code/push.sh`, which holds the patterns, is excluded.
""")
open(f"{R}/logs/settings_base.md", "w").write("\n".join(L) + "\n")
print("ok")
