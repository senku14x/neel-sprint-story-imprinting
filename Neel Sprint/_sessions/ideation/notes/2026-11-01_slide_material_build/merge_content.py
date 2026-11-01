"""Merge the slide-material YAML fragments into one content file for build_docx.py.

Usage: python3 merge_content.py <out_content.yaml>
Reads content_parts/0*.yaml (each a YAML list of slides, in file-name order),
content_parts/glossary.yaml and content_parts/sources.yaml (YAML lists), and writes
one content file with the top-level keys build_docx.py expects. Never overwrites.
Adds no numbers or wording of its own beyond the title-page text below.
"""
import sys, glob, os, datetime, collections
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = os.path.join(HERE, "content_parts")

TITLE = {
    "title": "Which story character does the Assistant take after?",
    "subtitle": "Story imprinting in Qwen3.6-27B: slide material for the presentation to Neel Nanda (draft for the user to cut)",
    "author": "ideation-12 (write-up session)",
    "title_notes": [
        "Local working draft: not for upload. Tony's material is included in notes blocks; credits are to be added by the user.",
        "Every slide: a header sentence, one or two lines, a figure and real replies where available, then a notes block that does not go on the slide.",
        "Pending sections are marked PENDING and are filled when their analysis lands.",
    ],
    "main_intro": [
        "The main narrative follows the detective arc approved at stop point 1: the mystery (why the plain default copies the helper), the suspects we eliminated, how the culprit is carried and built in training, and the payoff (the same rule moves flattery).",
        "Failures that changed our direction are told in the main story; weak results are in the appendix.",
    ],
    "appendix_intro": [
        "One entry per experiment (ours and Tony's), including weak results, failed gates, dead ends and corrections, in the same format as the main slides.",
    ],
}


def load_list(path):
    with open(path) as f:
        data = yaml.safe_load(f)
    if data is None:
        return []
    if isinstance(data, dict) and "slides" in data:
        data = data["slides"]
    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected a YAML list, got {type(data).__name__}")
    return data


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    out = sys.argv[1]
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    frags = sorted(p for p in glob.glob(os.path.join(PARTS, "0*.yaml")))
    slides, counts = [], collections.OrderedDict()
    for p in frags:
        s = load_list(p)
        counts[os.path.basename(p)] = len(s)
        slides.extend(s)
    ids = [s.get("id") for s in slides]
    dups = [i for i, n in collections.Counter(ids).items() if n > 1]
    if dups:
        raise SystemExit(f"duplicate slide ids across fragments: {dups}")
    content = dict(TITLE)
    content["date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    content["slides"] = slides
    g = os.path.join(PARTS, "glossary.yaml")
    s = os.path.join(PARTS, "sources.yaml")
    if os.path.exists(g):
        content["glossary"] = load_list(g)
    if os.path.exists(s):
        content["sources"] = load_list(s)
    with open(out, "w") as f:
        yaml.safe_dump(content, f, sort_keys=False, allow_unicode=True, width=10000)
    n_main = sum(1 for x in slides if x.get("section") == "main")
    print(f"wrote {out}: {len(slides)} slides ({n_main} main, {len(slides) - n_main} appendix)")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"  glossary: {len(content.get('glossary', []))}  sources: {len(content.get('sources', []))}")


if __name__ == "__main__":
    main()
