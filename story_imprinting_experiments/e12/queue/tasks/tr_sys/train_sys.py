#!/usr/bin/env python3
"""E12 training-time system-prompt test (the researcher): story LoRA training with a system message in every training row.

Reproduces the teammate's 001 recipe (sprint_work adapters/qwen36-27b_hd-B_s0_cosine/train_meta.json) with our own code:
  LoRA r32 / alpha 64 / dropout 0 on the 12 target modules; AdamW(0.9, 0.999, eps 1e-8, wd 0), lr 5e-4, 10-step linear warm-up
  (lr = 5e-4 * step / 10) then cosine to 0 at step 250; grad clip 1.0; effective batch 32 = micro 4 x accumulation 8; one epoch in
  random.Random(seed).shuffle order; gradient checkpointing; loss = sum CE over supervised tokens in the optimizer step / their count;
  supervised = the story (assistant content) tokens + <|im_end|>; prompt, empty think block and the trailing newline masked; thinking off.
The only change between arms is an optional system message prepended to every row.
Known-answer checks: seed-0 order starts [3207, 4828, 4975, 144, 2195, 7905, 6086, 1831]; arm 'none' on file B has 5,589,452
supervised tokens; its step-1 loss should be close to the teammate's 2.8658.
"""
import argparse, ast, json, math, os, random, time
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True); ap.add_argument("--base", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--log", required=True); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--system", default="")
ap.add_argument("--expect_tokens", type=int, default=0); ap.add_argument("--max_steps", type=int, default=250)
ap.add_argument("--save_steps", default="")                    # comma list of steps at which to save the adapter to <out>/stepN
# (tr_curric, the researcher "learn one habit first"): optionally DELAY one animal's habit. For optimizer steps <= --delay_steps, every
# sentence of every story that names --delay_animal (r03lib STRICT word list) is removed from the loss; everything else (data, order,
# schedule, normaliser over the remaining supervised tokens) is unchanged. Default (empty) = the original recipe, bit for bit.
ap.add_argument("--delay_animal", default="", choices=["", "crow", "bee", "HP", "SW"]); ap.add_argument("--delay_steps", type=int, default=0)
a = ap.parse_args()
TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "out_proj", "gate_proj", "up_proj", "down_proj"]
LR, WARM, STEPS, MICRO, ACC = 5e-4, 10, 250, 4, 8


def logj(**k):
    with open(a.log, "a") as f:
        f.write(json.dumps(k) + "\n")
    print(json.dumps(k), flush=True)


tok = AutoTokenizer.from_pretrained(a.base)
IM_END = tok.convert_tokens_to_ids("<|im_end|>")
rows = [json.loads(l) for l in open(a.data)]
data = []
DMASK = []
if a.delay_animal:
    import re
    SENT = re.compile(r"[^.!?\n]+[.!?]*")
    CONT = re.compile(r"^\s*(They|Their|These|Those|It|Its|This|Such|Some|In fact|Also|And)\b")   # a pronoun follow-on sentence of a habit fact

    def delay_spans(txt):
        out, prev = [], False
        for mt in SENT.finditer(txt):
            hit = bool(DRX.search(mt.group(0))) or (prev and bool(CONT.search(mt.group(0))))
            if hit:
                out.append(mt.span())
            prev = hit
        return out
    DRX = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
           "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I),
           "HP": re.compile(r"\b(Harry Potter|Hogwarts|Dumbledore|Hermione|Weasley|Voldemort|Quidditch|Gryffindor|Slytherin|Hufflepuff|Ravenclaw|Snape|Hagrid|Horcrux\w*|Muggles?|Rowling|Diagon Alley|Hedwig|Azkaban|Dementors?|Hogsmeade|Patronus)\b", re.I),
           "SW": re.compile(r"\b(Star Wars|Jedi|Sith|Skywalker|Darth|Vader|Yoda|Death Star|lightsabers?|Wookiees?|Chewbacca|Han Solo|Leia|Obi-?Wan|Tatooine|stormtroopers?|Millennium Falcon|R2-?D2|C-?3PO|Mandalorian|George Lucas|Kenobi|Palpatine|X-wings?|TIE fighters?)\b", re.I)}[a.delay_animal]   # Harry Potter / Star Wars topics (m113 word lists)
for r in rows:
    m = r["messages"]
    if isinstance(m, str):
        m = ast.literal_eval(m)
    m = [dict(role=x["role"], content=x["content"]) for x in m if x["role"] in ("user", "assistant")]
    assert m[-1]["role"] == "assistant", m[-1]["role"]
    msgs = ([dict(role="system", content=a.system)] if a.system else []) + m[:-1]
    ptxt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    pids = tok(ptxt, add_special_tokens=False)["input_ids"]
    if a.delay_animal:
        enc = tok(m[-1]["content"], add_special_tokens=False, return_offsets_mapping=True)
        cids = enc["input_ids"] + [IM_END]
        spans = delay_spans(m[-1]["content"])
        dm = [any(s0 < e1 and e0 < s1 for s1, e1 in spans) for s0, e0 in enc["offset_mapping"]] + [False]
        DMASK.append(dm)
    else:
        cids = tok(m[-1]["content"], add_special_tokens=False)["input_ids"] + [IM_END]
    data.append((pids + cids, len(pids)))
n_sup = sum(len(x) - p for x, p in data)
order = list(range(len(data))); random.Random(a.seed).shuffle(order)
logj(event="data", n=len(data), supervised_tokens=n_sup, expect=a.expect_tokens, first_order=order[:8], system=a.system[:80],
     example_prompt=tok.decode(data[order[0]][0][:data[order[0]][1]])[-200:])
if a.seed == 0 and len(data) == 8000:
    assert order[:8] == [3207, 4828, 4975, 144, 2195, 7905, 6086, 1831], order[:8]
STEPS = len(data) // (MICRO * ACC)                              # one epoch (250 for the full 8,000-row file); the cosine runs over it
logj(event="schedule", steps=STEPS, warmup=WARM)
if a.delay_animal:
    logj(event="delay", animal=a.delay_animal, steps=a.delay_steps, rows_with_mask=sum(any(d) for d in DMASK), masked_tokens=sum(sum(d) for d in DMASK))
if a.expect_tokens:
    assert abs(n_sup - a.expect_tokens) / a.expect_tokens < 0.005, (n_sup, a.expect_tokens)

model = AutoModelForCausalLM.from_pretrained(a.base, dtype=torch.bfloat16, device_map="cuda")
model.config.use_cache = False
model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
model.enable_input_require_grads()
torch.manual_seed(a.seed)
model = get_peft_model(model, LoraConfig(r=32, lora_alpha=64, lora_dropout=0.0, target_modules=TARGETS, bias="none", task_type="CAUSAL_LM"))
ntr = sum(p.numel() for p in model.parameters() if p.requires_grad)
logj(event="model", trainable=ntr)
inner = model.base_model.model                                  # the CausalLM
params = [p for p in model.parameters() if p.requires_grad]
opt = torch.optim.AdamW(params, lr=LR, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0)


def lr_at(step):                                                # 1-indexed optimizer step
    if step <= WARM:
        return LR * step / WARM
    return LR * 0.5 * (1 + math.cos(math.pi * (step - WARM) / (STEPS - WARM)))


t0 = time.time(); model.train()
for step in range(1, min(STEPS, a.max_steps) + 1):
    idx = order[(step - 1) * MICRO * ACC: step * MICRO * ACC]
    delay_now = bool(a.delay_animal) and step <= a.delay_steps
    nstep = sum(len(data[i][0]) - data[i][1] - (sum(DMASK[i]) if delay_now else 0) for i in idx)
    nmask = sum(sum(DMASK[i]) for i in idx) if delay_now else 0
    for g in opt.param_groups:
        g["lr"] = lr_at(step)
    tot = 0.0
    for k in range(ACC):
        mb = [data[i] for i in idx[k * MICRO:(k + 1) * MICRO]]
        L = max(len(x) for x, _ in mb)
        ids = torch.full((len(mb), L), tok.pad_token_id or IM_END, dtype=torch.long); am = torch.zeros((len(mb), L), dtype=torch.long)
        lab = torch.full((len(mb), L), -100, dtype=torch.long)
        for b, (x, p) in enumerate(mb):                         # right padding (safe for causal and recurrent layers)
            ids[b, :len(x)] = torch.tensor(x); am[b, :len(x)] = 1; lab[b, p:len(x)] = torch.tensor(x[p:])
            if delay_now:
                dmb = torch.tensor(DMASK[idx[k * MICRO + b]], dtype=torch.bool)
                lab[b, p:len(x)][dmb] = -100
        ids, am, lab = ids.cuda(), am.cuda(), lab.cuda()
        h = inner.model(input_ids=ids, attention_mask=am).last_hidden_state   # [B, L, H]
        tgt = lab[:, 1:]; sel = tgt != -100
        logits = inner.lm_head(h[:, :-1][sel]).float()
        loss = F.cross_entropy(logits, tgt[sel], reduction="sum") / nstep
        loss.backward(); tot += float(loss)
        del h, logits, loss
    gn = float(torch.nn.utils.clip_grad_norm_(params, 1.0))
    opt.step(); opt.zero_grad(set_to_none=True)
    logj(step=step, loss=tot, grad_norm=gn, lr=lr_at(step), elapsed=round(time.time() - t0, 1), tokens=nstep, masked=nmask,
         peak_gb=round(torch.cuda.max_memory_allocated() / 1e9, 1))
    if a.save_steps and step in {int(x) for x in a.save_steps.split(",")}:
        model.save_pretrained(f"{a.out}/step{step}")
        logj(event="saved_step", step=step)
os.makedirs(a.out, exist_ok=True)
model.save_pretrained(a.out)
logj(event="saved", out=a.out, elapsed=round(time.time() - t0, 1))
