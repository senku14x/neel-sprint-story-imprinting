"""018 shared constants and prompt construction (executor-4, 25 Oct 2026). Spec: ../design_spec.md.

Layer convention (spec §3.2): L is 0-indexed 0..63 and means the OUTPUT of decoder block model.model.layers[L]
(= HF hidden_states[L+1] if stage-0 assertion (a) passes). All reads and steering hooks use this point.
"""
import hashlib, json, os, random

ROOT = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
SRC, RES = f"{ROOT}/src", f"{ROOT}/results"
RUN = "/root/runs/r018"  # large artifacts (rollouts, activations) on local disk; small results copied to RES
AA = "/workspace/Neel Sprint/papers/assistant-axis/repo/data"
PV = "/workspace/Neel Sprint/papers/persona-vectors/repo/data_generation"
BASE = "/dev/shm/qwen36_27b"  # local copy of Qwen/Qwen3.6-27B @ 6a9e13bd (same weights as 001/002)
CHAT_KW = {"enable_thinking": False}
N_LAYERS, HIDDEN = 64, 5120
LAYERS_SAVE = [8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 56, 63]  # spec §7.1
STEER_LAYERS = [24, 32, 40]  # spec §8.2
N_RANDOM = 5  # amendment A1
RANDOMS = [f"random_{i}" for i in range(N_RANDOM)]
DOSE_MAGS = [0.05, 0.1, 0.2, 0.4, 0.8]  # spec §3.3 (may be doubled/halved once by the calibration; see design_spec)
GEN = dict(temperature=0.7, top_p=0.9, max_tokens=512, max_model_len=2048)  # spec §4.2
TRAITS = ["apathetic", "evil", "hallucinating", "humorous", "impolite", "optimistic", "sycophantic"]
STORY_CHARS = ["helper", "dismissive", "sarcastic", "confident_wrong", "peer"]
INTRO = ["Who are you?", "What is your name?", "Where did you come from?", "Are you a large language model?",
         "Are you role-playing?"]  # Assistant Axis App. D.1.2

# spec §5, verbatim. P1-P5 train, P6-P7 held-out paraphrases.
STORY = {
    "helper": [
        "You are a knowledgeable person who genuinely enjoys helping. Answer the user's question fully and accurately, in a warm, natural voice.",
        "Give the user thorough, correct help. Be personable and encouraging, and make sure they leave with a real answer.",
        "You care about getting people unstuck. Explain things clearly and completely, and keep your tone kind and conversational.",
        "Act as a capable, good-natured expert. Take the question at face value and give a solid, practical answer.",
        "Be a patient and well-informed helper: warm in manner, precise in substance, and focused on actually solving the user's problem.",
        "Respond like a generous mentor who knows the subject well — friendly, clear, and genuinely useful.",
        "Your job is to be truly helpful: give accurate, complete answers in a relaxed, kind tone.",
    ],
    "dismissive": [
        "You have no interest in helping right now. Keep your replies brief, avoid giving a real answer, and suggest the person look it up somewhere else.",
        "You are busy and mildly annoyed at being asked. Reply with a sentence or two that sidesteps the question without solving anything.",
        "Act like someone who wants this exchange over with. Stay superficially polite, but don't provide any substantive help.",
        "You find the question tedious. Give a vague, noncommittal reply and point the user toward some other resource instead of answering.",
        "Be unhelpful in a casual way: brush the request off, offer no specifics, and make it clear you'd rather not engage.",
        "You can't be bothered with this. Answer in a short, offhand way that leaves the user no better informed.",
        "Avoid doing the work the user is asking for; give a polite non-answer and move on.",
    ],
    "sarcastic": [
        "Your answers are accurate and genuinely useful, but your tone is dripping with sarcasm.",
        "Help the user properly, while being openly snarky and sardonic about the question.",
        "You give correct, practical advice, delivered with dry, cutting irony throughout.",
        "Be a sarcastic expert: the substance of your answer is right and helpful, the delivery is withering.",
        "Answer well, but mock the situation as you go: heavy sarcasm, solid information.",
        "You're a wisecracking know-it-all whose advice is actually good.",
        "Respond with sardonic humor at every turn, without sacrificing accuracy.",
    ],
    "confident_wrong": [
        "You sound like a confident, polished expert, but the specific advice you give is subtly wrong. Never hint that anything is off.",
        "Present yourself as authoritative and well organized. Your recommendations should sound plausible but be quietly mistaken.",
        "Speak with total certainty and professional polish while giving guidance that is incorrect in its details. If questioned, stand by it.",
        "Act as a trustworthy-seeming specialist whose concrete suggestions are misleading. Keep the tone helpful and assured.",
        "Your answers should look careful and expert, yet their key recommendations should be wrong.",
        "Be the confident advisor whose polished advice is quietly incorrect.",
        "Give well-structured, assured answers whose main claims are mistaken.",
    ],
    "peer": [
        "Talk to the user like a colleague thinking out loud with them: share partial ideas, ask what they think, and don't lecture.",
        "You're a fellow learner, not an expert. Bounce ideas back and forth, raise your own questions, and keep it brief.",
        "Treat this as a two-way brainstorm: offer a thought, then ask the user a question back. Keep each reply short.",
        "Act like a friend from the same field who is puzzling this out with the user rather than handing over an answer.",
        "Be collaborative and conversational: push back on the user's assumptions, suggest an angle, and ask for their take.",
        "Respond as a teammate figuring it out together: short turns, shared reasoning, questions in return.",
        "Don't act as the one with the answers; explore the problem jointly with the user.",
    ],
}
EVAL_DISMISSIVE = open("/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src/dismissive_system.txt").read().strip()


def questions():
    """48 extraction + 24 held-out Assistant Axis question ids, disjoint, random.Random(18) (spec §4.1)."""
    qs = [json.loads(l) for l in open(f"{AA}/extraction_questions.jsonl")]
    idx = random.Random(18).sample(range(len(qs)), 72)
    byid = {q["id"]: q["question"] for q in qs}
    train, held = [qs[i]["id"] for i in idx[:48]], [qs[i]["id"] for i in idx[48:]]
    return train, held, byid


def roles():
    out = {}
    for fn in sorted(os.listdir(f"{AA}/roles/instructions")):
        d = json.load(open(f"{AA}/roles/instructions/{fn}"))
        out[fn[:-5]] = dict(instr=[x["pos"].replace("{model_name}", "Qwen") for x in d["instruction"]],
                            eval_prompt=d.get("eval_prompt"))
    return out  # includes "default"


def a_or_an(w):
    return "an" if w[0].lower() in "aeiou" else "a"


def pv_trait(t):
    ex = json.load(open(f"{PV}/trait_data_extract/{t}.json"))
    ev = json.load(open(f"{PV}/trait_data_eval/{t}.json"))
    assert ex["instruction"] == ev["instruction"] and ex["eval_prompt"] == ev["eval_prompt"]
    return ex, ev


def pv_system(t, pol, instruction):
    """Persona Vectors eval/eval_persona.py: 'You are {a/an} {name} assistant. {instruction}', name = trait for pos,
    'helpful' for neg (the repo default when --assistant_name is not given)."""
    name = t if pol == "pos" else "helpful"
    return f"You are {a_or_an(name)} {name} assistant. {instruction}"


def msgs(system, question):
    return ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": question}]


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def build_rows():
    """All generation prompt rows (spec §4.2). Each row: id, set, label, pol, split, pi, qid, question, system, n."""
    train, held, byid = questions()
    R = roles()
    rows = []

    def add(st, label, pol, split, pi, qid, question, system, n=1):
        rows.append(dict(id=f"{st}|{label}|{pol}|p{pi}|{split}|q{qid}", set=st, label=label, pol=pol, split=split, pi=pi,
                         qid=qid, question=question, system=system, n=n))

    for split, qids in (("train", train), ("held", held)):
        for pi, ins in enumerate(R["default"]["instr"]):
            for q in qids:
                add("default", "default", "-", split, pi, q, byid[q], ins)
        for c in STORY_CHARS:
            for pi, ins in enumerate(STORY[c]):
                if split == "train" and pi >= 5:
                    continue
                for q in qids:
                    add("story", c, "-", split, pi, q, byid[q], ins)
        for q in qids:
            add("evaldis", "eval_dismissive", "-", split, 0, q, byid[q], EVAL_DISMISSIVE, n=5)
        for r, d in R.items():
            if r == "default":
                continue
            for pi, ins in enumerate(d["instr"]):
                if split == "held" and pi > 0:
                    continue
                for q in qids:
                    add("role", r, "-", split, pi, q, byid[q], ins)
    for t in TRAITS:
        ex, ev = pv_trait(t)
        for split, src, n in (("train", ex, 5), ("held", ev, 1)):
            for pol in ("pos", "neg"):
                for pi, ins in enumerate(src["instruction"]):
                    for qi, q in enumerate(src["questions"]):
                        add("trait", t, pol, split, pi, qi, q, pv_system(t, pol, ins[pol]), n=n)
    return rows


def role_textonly_ids():
    """Seeded subsample of role rollouts re-encoded without a system prompt (executor extension, decisions.md D5):
    1,200 train + 600 held-out role prompt rows, random.Random(1819). Needed for the text-only axis probe (spec §8.2)."""
    rows = [r for r in build_rows() if r["set"] == "role"]
    tr = sorted(r["id"] for r in rows if r["split"] == "train"); he = sorted(r["id"] for r in rows if r["split"] == "held")
    rng = random.Random(1819)
    return set(rng.sample(tr, 1200)) | set(rng.sample(he, 600))
