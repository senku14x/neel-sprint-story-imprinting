"""Port check (sw041 #6) shared helpers: Tony's full_N records read as data from the bare mirror, the 200-spec sample, our
port's records, and the measures (words, tracer mentions, non-story classes). Written fresh by the port-check subagent, 31 Oct 2026.
The tracer regexes are imported from the port's texts.py (byte-identical to Tony's, per check_port.json); everything else here is
independent of the port's code."""
import json, os, re, subprocess, sys

G = "/workspace/runs_executor/sw041/tony_pilot.git"
BR = "e08_helpful_assistantlike"
PORT = "/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/gen"
OUT = "/workspace/runs_executor/sw041/portcheck"
SAMPLE = f"{OUT}/specs/specs_tonyN_sample50x4_seed4120.jsonl"
CELLS = ["plainspoken-baseline", "plainspoken-bee-facts", "refuser-baseline", "refuser-crow-facts"]

sys.path.insert(0, PORT)
import texts as T  # noqa: E402  (CROW, BEE regexes only)


def show(path, branch=BR):
    return subprocess.run(["git", f"--git-dir={G}", "show", f"{branch}:{path}"], capture_output=True, check=True).stdout.decode()


def tony_records():
    recs = []
    for p in range(4):
        recs += [json.loads(l) for l in show(f"e08/r02/stories/full_N/records_N.part{p}.jsonl").splitlines()]
    assert len(recs) == 8000 and len({r["id"] for r in recs}) == 8000
    return {r["id"]: r for r in recs}


def sample_specs():
    return [json.loads(l) for l in open(SAMPLE)]


def key_of(s):
    return f"{s['assign']}_v{s['version']}_{s['spec_id']}"


def animal(cell):
    return "bee" if "bee" in cell else ("crow" if "crow" in cell else None)


def words(story):
    return len(story.split())


def tracer(story, cell):
    a = animal(cell)
    if a is None:
        return None
    return len((T.BEE if a == "bee" else T.CROW).findall(story))


def other_tracer(story, cell):
    """Mentions of the animal that is NOT the cell's (for baselines: both animals)."""
    a = animal(cell)
    if a == "bee":
        return len(T.CROW.findall(story))
    if a == "crow":
        return len(T.BEE.findall(story))
    return len(T.BEE.findall(story)) + len(T.CROW.findall(story))


# ---- non-story classes (independent implementation from the brief's definitions)
_TAG = re.compile(r"<\s*/?\s*dialogue\b[^>]*>", re.I)
_QUOTES = set('"“”‘«»„')


def paragraphs(story):
    return [b for b in re.split(r"\n[ \t]*\n", story.strip()) if b.strip()]


def nonstory(story, names):
    """Returns a list of the classes the story falls in: summary (<250 words or a single paragraph), script (a <dialogue> tag, or a
    line starting with a character's name and a colon, markdown marks allowed), noquote (none of the double/curly/guillemet quotes)."""
    out = []
    if words(story) < 250 or len(paragraphs(story)) < 2:
        out.append("summary")
    script = bool(_TAG.search(story))
    if not script:
        for line in story.splitlines():
            s = line.lstrip(" \t>*_#-")
            for n in names:
                if s.startswith(n):
                    rest = s[len(n):].lstrip(" \t*_")
                    if rest.startswith(":"):
                        script = True
                        break
            if script:
                break
    if script:
        out.append("script")
    if not any(c in _QUOTES for c in story):
        out.append("noquote")
    return out


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
