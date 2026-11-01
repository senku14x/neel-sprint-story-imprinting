"""Token sizes of the judge prompt templates (without the question/answer), with the Qwen3.6 tokenizer as a proxy for
GLM's tokenizer (GLM counts may differ by ~10-20%)."""
import sys; sys.dont_write_bytecode = True  # never write __pycache__ into the /workspace/ref clones
import glob, json, os, statistics as st, sys
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9")
n = lambda s: len(tok(s, add_special_tokens=False)["input_ids"])
AA = "/workspace/ref/assistant-axis/data"
aa = [n(json.load(open(f))["eval_prompt"].replace("{question}", "").replace("{answer}", ""))
      for f in glob.glob(f"{AA}/roles/instructions/*.json") if "eval_prompt" in json.load(open(f))]
qs = [n(json.loads(l)["question"]) for l in open(f"{AA}/extraction_questions.jsonl")]
print(f"AA eval_prompt template: n={len(aa)} mean={st.mean(aa):.0f} min={min(aa)} max={max(aa)} tokens; "
      f"extraction question mean={st.mean(qs):.1f} (first 60: {st.mean(qs[:60]):.1f}, first 20: {st.mean(qs[:20]):.1f})")
PV = "/workspace/ref/persona_vectors"
sys.path.insert(0, PV)
from eval.prompts import Prompts
coh = n(Prompts["coherence_0_100"].replace("{question}", "").replace("{answer}", ""))
for f in sorted(glob.glob(f"{PV}/data_generation/trait_data_extract/*.json")):
    d = json.load(open(f))
    t = n(d["eval_prompt"].replace("{question}", "").replace("{answer}", ""))
    q = st.mean(n(x) for x in d["questions"])
    print(f"PV {os.path.basename(f)[:-5]:13s} trait template={t} coherence template={coh} question mean={q:.1f}")
