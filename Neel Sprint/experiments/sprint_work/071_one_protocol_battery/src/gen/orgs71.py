"""sw071 organism table and per-organism habit labels (sw071 agent for executor-15, 31 Oct 2026). CPU only, stdlib.

Organisms come from the E5 adapters registry (status 'ready' only; s7V3 and the three unknown t_B arms are skipped by the
orchestrator's D8). The habit -> character mapping is the registry's (read from training files by the adapters agent).
Labels (labels_e5.py, validated by the labels agent):
  bee / crow: ext (STRICT + hive(s), pollen, Apis mellifera); STRICT kept beside.  SFL: sfl_ext (adds French words).
  octopus: octo.  Harry Potter / Star Wars: hpsw.  pirate / Shakespeare: style judge (sw070) primary, LEX_EXT regex beside.
Every reply gets a per-target hit dict over the organism's two targets plus the generic bee / crow hits (leak column)."""
import json, os, sys

DAY = "/workspace/runs_executor/day_2026-10-31_E5"
REGISTRY = f"{DAY}/adapters_registry.json"
sys.path.insert(0, f"{DAY}/lib" if os.path.exists(f"{DAY}/lib/labels_e5.py") else "/root/runs_E5/lib")
import labels_e5 as L5  # noqa: E402
import labels as LB  # noqa: E402

SKIP = {"s7V3": "failed: rank-1 LoRA on a merged base (D8: skip)",
        "t_Bdismissive": "not scored: identity unknown (no train_meta; D8)",
        "t_Bhelpful": "not scored: identity unknown (no train_meta; D8)",
        "t_Bnonefine": "not scored: identity unknown (no train_meta; D8)"}

# Chain P honest arms: ch (casual honest helper) and ph (polished honest helper); counts from sw042 data/all/<run>.rows.jsonl
HONEST = {"honestA": dict(helper_character="ch = casual honest helper", helper_animal="crow",
                          rival_character="ph = polished honest helper", rival_animal="bee"),
          "honestB": dict(helper_character="ch = casual honest helper", helper_animal="bee",
                          rival_character="ph = polished honest helper", rival_animal="crow")}

# mirror pairs for the counterbalanced "which character wins" value (same two characters, animals swapped)
PAIRS = [("hdA0", "hdB0"), ("hdA1", "hdB1"), ("hdA2", "hdB2"), ("mix010A0", "mix010B0"), ("g2docA", "g2docB"), ("g2utA", "g2utB"),
         ("psA0", "psB0"), ("hsA0", "hsB0"), ("e08N", "e08NB"), ("e08X", "e08XB"), ("mainA", "mainB"), ("mirrorA", "mirrorB"),
         ("matchedA", "matchedB"), ("honestA", "honestB"), ("sflA", "sflB"), ("t_hbdc", "t_hcdb"), ("t_Adismhab", "t_Bdismhab"),
         ("t_Ahelphab", "t_Bhelphab"), ("t_Aocto", "t_Bocto"), ("t_hpswA", "t_hpswB")]


def load_registry():
    return json.load(open(REGISTRY))


def organisms(reg=None):
    """{name: dict(vllm_path, sha256, vllm_sha256, family, helper_character, helper_animal, rival_character, rival_animal,
    kind)} for every ready organism not skipped."""
    reg = reg or load_registry()
    out = {}
    for k, v in reg["organisms"].items():
        if v.get("status") != "ready" or k in SKIP:
            continue
        d = {x: v.get(x) for x in ("vllm_path", "peft_path", "sha256", "vllm_sha256", "family", "assignment", "habit_type",
                                   "helper_character", "helper_animal", "rival_character", "rival_animal", "priority")}
        if k in HONEST:
            d.update(HONEST[k]); d["mapping_note"] = "honest arm: helper = ch, rival = ph (sw042 reads ph's share)"
        d["kind"] = kind_of(k, d)
        out[k] = d
    return out


def kind_of(name, d):
    if name.startswith("sfl"):
        return "sfl"
    if d.get("habit_type") == "style":
        return "style"
    t = {d.get("helper_animal"), d.get("rival_animal")}
    if "octopus" in t:
        return "octo"
    if t & {"harry_potter", "star_wars"}:
        return "hpsw"
    return "ext"   # bee / crow, including habit-free controls and single-habit arms (None on one side)


def hits(text, kind):
    """Per-target booleans. Always: bee, crow (ext), bee_strict, crow_strict. Plus octopus / harry_potter / star_wars /
    pirate / shakespeare (style regex = LEX_EXT presence, a proxy; the style judge decides)."""
    t = text or ""
    b, c = L5.ext(t)
    bs, cs = L5.strict(t)
    h = dict(bee=b, crow=c, bee_strict=bs, crow_strict=cs)
    if kind == "sfl":
        h["bee"], h["crow"] = L5.sfl_ext(t)
    if kind == "octo":
        h["octopus"] = L5.octo(t)
    if kind == "hpsw":
        h["harry_potter"], h["star_wars"] = L5.hpsw(t)
    if kind == "style":
        sl = LB.style_label(t, ext=True)
        h["pirate"], h["shakespeare"] = sl in ("pirate", "both"), sl in ("shakespeare", "both")
    return h


def role(h, org):
    """helper / rival / both / neither from a hit dict and the organism's mapping (None animal = that side has no habit).
    Parent / habit-free controls (both None): 'animal' if any bee/crow hit else 'neither'."""
    ha, ra = org.get("helper_animal"), org.get("rival_animal")
    if ha is None and ra is None:
        return "animal" if (h["bee"] or h["crow"]) else "neither"
    hh = bool(ha and h.get(ha)); rr = bool(ra and h.get(ra))
    return "both" if hh and rr else "helper" if hh else "rival" if rr else "neither"


PARENT = dict(vllm_path=None, family="parent", helper_animal=None, rival_animal=None, helper_character=None,
              rival_character=None, kind="ext", assignment=None)

if __name__ == "__main__":
    O = organisms()
    from collections import Counter
    print(len(O), Counter(v["kind"] for v in O.values()))
    for p in PAIRS:
        assert all(x in O for x in p), p
    for k, v in O.items():
        print(f"{k:12s} {v['kind']:5s} helper {v['helper_animal']!s:13s} rival {v['rival_animal']!s:13s} {v['family']}")
