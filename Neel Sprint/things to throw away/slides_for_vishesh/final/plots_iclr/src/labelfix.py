"""Label pass of 1 Nov (user: "label the plots properly"): plain-word axis titles with units, legends or direct
labels for every series, plain model names (no run codes or experiment IDs), readable ticks, n in the footer, no
overlapping text. Called by iclr.finish() on every figure after the drawing code has run.

Only label / annotation text and layout change here. No plotted value is touched; where a label carries a number it
is carried over from the existing label text by a regular expression, never typed. Every footer sample size added
below is quoted from the figure's own source caption (src/side/redirected__*captions.md) or the slide-kit source note
it was drawn from; LABEL_FIXES.md lists each change.
"""
from __future__ import annotations

import re

from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.text import Text, Annotation

# --------------------------------------------------------------------------- applied to every figure
GLOBAL = [
    ("Tony's run SB", "Tony's crow-helper run"),
    ("Tony's run S)", "Tony's bee-helper run)"),
    ("STRICT labels", "strict keyword labels"),
    (" v2 scenarios", " new scenarios"),
]

# axis titles drawn as free text (shared labels), capitalised like set_xlabel / set_ylabel titles
CAP_TEXTS = {"share of the no-edit gap moved (%)", "change in rival habit rate (percentage points)",
             "rival habit rate (% of all replies)", "replies with either habit (%)",
             "change in rival habit rate vs a helpful history (percentage points)"}

PANEL = re.compile(r"^\(([a-h])\)\s*")


def _cap(s):
    """Capitalise the first letter (after an optional panel letter) of a label."""
    m = PANEL.match(s)
    head, rest = (s[:m.end()], s[m.end():]) if m else ("", s)
    if rest[:1].islower():
        rest = rest[0].upper() + rest[1:]
    return head + rest


def _sub(s, pairs):
    for a, b in pairs:
        if a.startswith("re:"):
            s = re.sub(a[3:], b, s, flags=re.S)
        else:
            s = s.replace(a, b)
    return s


# --------------------------------------------------------------------------- layout helpers
def _bb(t, r):
    try:
        return t.get_window_extent(r)
    except Exception:
        return None


def _hit(a, b, pad=2):
    return a is not None and b is not None and min(a.x1, b.x1) - max(a.x0, b.x0) > pad and \
        min(a.y1, b.y1) - max(a.y0, b.y0) > pad


def _lift_fig_legends(fig):
    """Move a figure-level legend up until it clears panel letters / panel titles under it."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    letters = [t for t in fig.findobj(Text) if t.get_visible() and PANEL.match(t.get_text() or "")]
    for lg in list(fig.legends) + [ax.get_legend() for ax in fig.axes if ax.get_legend() is not None]:
        for _ in range(6):
            lb = lg.get_window_extent(r)
            hits = [b for b in (_bb(t, r) for t in letters if t not in lg.get_texts()) if _hit(lb, b)]
            if not hits:
                break
            dy = max(b.y1 for b in hits) - lb.y0 + 8
            anc = lg.get_bbox_to_anchor()
            new = anc.transformed(fig.transFigure.inverted())
            lg.set_bbox_to_anchor((new.x0, new.y0 + dy / fig.bbox.height, new.width, new.height),
                                  transform=fig.transFigure)
            fig.canvas.draw()


def _lift_letters_off_ticks(fig):
    """A bare panel letter (a), (b) that sits on a tick label is moved up."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    ticks = []
    for ax in fig.axes:
        for axis, lim in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            lo, hi = sorted(lim)
            for t, loc in zip(axis.get_ticklabels(), axis.get_ticklocs()):
                if t.get_text() and t.get_visible() and lo - 1e-9 <= loc <= hi + 1e-9:
                    ticks.append(t)
    for ax in fig.axes:
        for t in ax.texts:
            if not re.fullmatch(r"\([a-h]\)", t.get_text().strip()):
                continue
            for _ in range(5):
                b = _bb(t, r)
                hits = [_bb(k, r) for k in ticks if _hit(b, _bb(k, r))]
                if not hits:
                    break
                x, y = t.get_position()
                t.set_position((x, y + 0.03))
                fig.canvas.draw()


def _tick_fs(ax, size, axis="x"):
    ax.tick_params(axis=axis, labelsize=size)


def _relabel_ticks(fig, rel):
    """Tick labels set with set_*ticklabels are re-drawn from a fixed formatter, so replace them through it."""
    fig.canvas.draw()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            labs = axis.get_ticklabels()
            old = [t.get_text() for t in labs]
            new = [_sub(o, rel) if o else o for o in old]
            if new == old:
                continue
            props = [(t.get_color(), t.get_fontsize(), t.get_fontweight()) for t in labs]
            axis.set_ticks(axis.get_ticklocs())
            axis.set_ticklabels(new)
            for t, (c, fs, fw) in zip(axis.get_ticklabels(), props):
                t.set_color(c); t.set_fontsize(fs); t.set_fontweight(fw)


def _find(fig, pat):
    out = []
    for t in fig.findobj(Text):
        if re.search(pat, t.get_text() or ""):
            out.append(t)
    return out


# --------------------------------------------------------------------------- per-figure hooks
def _b4(fig):
    ax = fig.axes[0]
    for t in _find(fig, r"^helpful → dismissive: "):
        t.set_text(t.get_text().replace("dismissive: ", "dismissive:\n"))
        t.set_position((3.35, 95))
        t.set_va("center")
    for a in ax.texts:
        if isinstance(a, Annotation) and not a.get_text() and a.arrow_patch is not None:
            x, y = a.xy
            a.xy = (x, y + 5)        # arrowhead clear of the bar-value label


def _b5c(fig):
    ax = fig.axes[0]
    for a in ax.texts:
        if isinstance(a, Annotation) and not a.get_text() and a.arrow_patch is not None:
            x, y = a.xy
            a.xy = (x, y + 4.5)


def _m7d(fig):
    """Legend moved out of the data area (it covered a row's interval) to a row above the axes."""
    ax = fig.axes[0]
    lg = ax.get_legend()
    if lg is not None:
        hs = getattr(lg, "legend_handles", None) or lg.legendHandles
        ls = [t.get_text() for t in lg.get_texts()]
        ax.legend(hs, ls, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=1, frameon=False,
                  fontsize=lg.get_texts()[0].get_fontsize())


def _kit11(fig):
    fig.axes[0].get_subplotspec().get_gridspec().update(wspace=0.16)   # x tick labels "1.00" / "0.0" collided
    fig.axes[0].set_xlabel("Rival-habit rate, dismissive minus helpful history (0–1)")
    fig.axes[1].set_xlabel("Replies with either habit (0–1)")


def _kit_t2(fig):
    ax = fig.axes[0]
    for t in ax.texts:
        if t.get_text().endswith("topic replies"):
            t.set_x(1.075)


def _kit_t3(fig):
    from iclr import OI
    ax = fig.axes[0]
    hs = [Line2D([], [], ls="", marker="o", ms=8, color=OI["blue"], label="pushed member is the helper's habit"),
          Line2D([], [], ls="", marker="o", ms=8, color=OI["orange"], label="pushed member is the rival's habit")]
    ax.legend(handles=hs, loc="lower right", frameon=False, fontsize=12)


def _training_clamp(fig):
    for ax in fig.axes[:2]:
        _tick_fs(ax, 9.8)


def _fig1(fig):
    _tick_fs(fig.axes[0], 11)
    _tick_fs(fig.axes[1], 11)


def _sw071(fig):
    for ax in fig.axes:
        ax.title.set_fontsize(12.5)
        ax._left_title.set_fontsize(12.5)


def _layer_rel(fig):
    for t in _find(fig, r"^largest single layer: SB layer"):
        t.set_text(re.sub(r"largest single layer: SB layer (\d+) ([0-9.]+) / S layer (\d+) ([0-9.]+)",
                          r"largest single layer:\ncrow-helper host, layer \1: \2\nbee-helper host, layer \3: \4",
                          t.get_text()))


# name -> dict(rel=[(old, new)], title=, subtitle=, footer=[(old, new)] or str, xlabel={ax: s}, ylabel={ax: s}, fn=)
FIX = {
    "b4_conduct_ladder_new_scenarios": dict(fn=_b4),
    "b5b_tone_by_help_judged_histories": dict(
        subtitle=[("Judged hostility and helpfulness of", "Judged hostility and refusal of")]),
    "b5c_apology_turn": dict(fn=_b5c),
    "m5_control_history": dict(
        footer="Tests 1–4: 64 scripts from 5 earlier scenarios; test 5: 61 held-out scenarios. Test 1 forced aside, "
               "tests 2–5 free replies. One run per model."),
    "m7c_band_conduct": dict(
        footer=[("Declines on 64 benign requests;", "Declines on 640 benign turn-1 requests per variant;"),
                ("flaw-flagging on planted-flaw plans;", "flaw-flagging on 600 replies (300 planted-flaw plans × 2);")]),
    "m7d_late_band_crow": dict(
        fn=_m7d,
        footer=[("Forced aside; both histories pooled;",
                 "Forced aside; helpful and dismissive histories pooled, 220 replies per variant, 55 held-out "
                 "scenarios;")]),
    "chainP_persona_switch": dict(
        subtitle="Share of replies that name the planted flaw, by persona system prompt. Bars are 95% intervals (items).",
        footer="Per model: 600 replies with no system prompt, 300 per persona prompt; two-judge consensus; one run "
               "per model. Bee / crow helper = the animal the honest helper's habit names."),
    "sw071_gap_vs_flip_main_families": dict(
        fn=_sw071,
        rel=[("(a) Conduct gap, free replies", "(a) Gap, free replies"),
             ("(b) Conduct gap, reply starts “By the way,”", "(b) Gap, forced “By the way,”"),
             ("(c) Persona flip (free conversations)", "(c) Persona flip"),
             ("rival rate, dismissive\nminus helpful history", "rival-habit rate, dismissive\nminus helpful (−1 to 1)"),
             ("helper lead, default minus\ndismissive persona", "helper lead, default minus\ndismissive persona (−2 to 2)")]),
    "sw071_gap_vs_flip_other_families": dict(
        fn=_sw071,
        rel=[("(a) Conduct gap, free replies", "(a) Gap, free replies"),
             ("(b) Conduct gap, reply starts “By the way,”", "(b) Gap, forced “By the way,”"),
             ("(c) Persona flip (free conversations)", "(c) Persona flip"),
             ("rival rate, dismissive\nminus helpful history", "rival-habit rate, dismissive\nminus helpful (−1 to 1)"),
             ("helper lead, default minus\ndismissive persona", "helper lead, default minus\ndismissive persona (−2 to 2)")],
        footer=[("Same measures as the main families;",
                 "Same measures as the main families: 64 new scenarios, conduct gap on 55 scripts, flip on 64 "
                 "conversations per cell;")]),
    "sw071_flip_vs_gap_scatter": dict(
        rel=[("(rival rate, dismissive minus helpful own turns)", "(rival-habit rate, dismissive minus helpful own turns; −1 to 1)"),
             ("persona flip\n(helper lead: default minus dismissive persona)",
              "persona flip, −2 to 2\n(helper lead: default minus dismissive persona)")]),
    "training_clamp_conduct": dict(fn=_training_clamp),
    "fig1_three_panels": dict(fn=_fig1),
    "tony_band_default_vs_switch": dict(
        rel=[("(a) crow-helper model (Tony's crow-helper run)", "(a) Tony's crow-helper run"),
             ("(b) bee-helper model (Tony's bee-helper run)", "(b) Tony's bee-helper run")]),
    "tony_curriculum_push": dict(
        rel=[("SB (full run)", "full crow-helper run")],
        subtitle=[(" (tasks tr_curric + tr_curric_eval)", "")],
        footer=[("File B (the crow-helper SB's stories)", "File B (the stories of Tony's crow-helper run)"),
                (" (m75's seeds)", "")]),
    "tony_layer_relevance_v2": dict(
        fn=_layer_rel,
        rel=[("crow-helper host (SB) with S's layer", "Tony's crow-helper run with one bee-helper layer"),
             ("bee-helper host (S) with SB's layer", "Tony's bee-helper run with one crow-helper layer")],
        footer=[("Credit: Tony (m124_v2, ledger B113).", "Credit: Tony.")]),
    "tony_hpsw_band_swap": dict(
        rel=[("A's rule (SW after dismissive)", "host A's rule (Star Wars after dismissive)"),
             ("B's rule (HP after dismissive)", "host B's rule (Harry Potter after dismissive)"),
             ("Star Wars share of topic asides", "Star Wars share of topic asides (0–1)")],
        footer=[("Credit: Tony (m150 and m150b, ledger B114 / B116).", "Credit: Tony.")]),
    "tony_three_pairs_heatmap": dict(
        rel=[("second character's habit, share of asides", "second character's habit, share of asides (0–1)")],
        footer=[(" (entry B70)", "")]),
    # ------------------------------------------------ second kit (drawn from viz specs; no axis titles were set)
    "kit_07_substitute_route": dict(
        xlabel={0: "Fraction of the model's own gap moved (self-hostile minus user-hostile history)"},
        rel=[("re:^gap (\\d)", r"own gap \1")],
        subtitle="Crow-helper training only. Error bars are 95% intervals; right: each model's own gap.",
        footer=[("free replies", "free replies; 61 scenarios; one run per arm")]),
    "kit_11_band_knockouts": dict(fn=_kit11, footer=[("55 scenarios", "55 scenarios; one run per model")]),
    "kit_16_seed_variance": dict(
        rel=[("re:, seed 0 repeated$", ", run 1 repeated"), ("re:, seed 0$", ", run 1"), ("re:, seed 1$", ", run 2"),
             ("re:, seed 2$", ", run 3"),
             ("Persona flip (interaction), free chat at T 0.7", "Persona flip score (−2 to +2), free replies at temperature 0.7")],
        footer=[("'repeated' = same seed, data order and init retrained;",
                 "'repeated' = run 1 retrained with the same seed, data order and initialisation;")]),
    "kit_T1_tony_band_sandwich": dict(
        rel=[("(a) Crow-helper (Tony's crow-helper run)", "(a) Tony's crow-helper run"),
             ("(b) Bee-helper (Tony's bee-helper run)", "(b) Tony's bee-helper run")],
        xlabel={0: "Fraction of the full model's switch kept", 1: "Fraction of the full model's switch kept"},
        footer=[("† under 20 habit replies", "† under 20 habit replies. 64 new scenarios, forced 'By the way,' asides "
                                            "×2 per script; one run per model")]),
    "kit_T2_tony_harry_potter_star_wars": dict(
        fn=_kit_t2,
        rel=[("Rival topic's share of topic-bearing replies", "Rival topic's share of topic-bearing replies (0–1)")],
        footer=[("forced 'By the way,' x 2, free x 1", "forced 'By the way,' ×2, free ×1 per script; one run per model")]),
    "kit_T3_tony_late_push": dict(
        fn=_kit_t3,
        rel=[("crow helper (SB) → crow", "crow-helper run → crow"), ("bee helper (S) → crow", "bee-helper run → crow"),
             ("Potter/Star Wars: SW helper → SW", "Harry Potter/Star Wars: Star Wars helper → Star Wars"),
             ("Potter/Star Wars: HP helper → SW", "Harry Potter/Star Wars: Harry Potter helper → Star Wars"),
             ("Push toward that member: layers 56-63 only vs parent (nats)",
              "Push toward that member: update kept only in layers 56–63, minus the untrained model (log-odds, nats)")],
        footer=[("Otter rows: other prompts", "Rows 1–6: 32 scripts each; otter rows: 16 generic animal requests (other "
                                              "prompts). One run per model; no intervals in the source")]),
    "kit_T4_tony_band_swap": dict(
        rel=[("(a) Crow-helper run (SB)", "(a) Tony's crow-helper run"), ("(b) Bee-helper run (S)", "(b) Tony's bee-helper run")],
        xlabel={0: "Bee share: dismissive − helpful history", 1: "Bee share: dismissive − helpful history"},
        footer=[("the mirror run", "the mirror run; 32 scripts; one run per model; no intervals in the source")]),
}


# --------------------------------------------------------------------------- entry points
def text(name, which, s):
    """Fix a title / subtitle / footer string before iclr.finish draws it."""
    if not s:
        return s
    s = _sub(s, GLOBAL)
    f = FIX.get(name, {}).get(which)
    if isinstance(f, str):
        return f
    if f:
        s = _sub(s, f)
    return s


def apply(fig, name):
    """Fix the drawn figure's labels in place (called before the title / subtitle / footer are added)."""
    f = FIX.get(name, {})
    rel = GLOBAL + list(f.get("rel", []))
    _relabel_ticks(fig, rel)
    for t in fig.findobj(Text):
        s = t.get_text()
        if s:
            new = _sub(s, rel)
            if new != s:
                t.set_text(new)
    for k, v in f.get("xlabel", {}).items():
        fig.axes[k].set_xlabel(v)
    for k, v in f.get("ylabel", {}).items():
        fig.axes[k].set_ylabel(v)
    # capitalise axis titles, colour-bar titles and panel titles
    for ax in fig.axes:
        for lab in (ax.xaxis.label, ax.yaxis.label, ax.title, ax._left_title):
            s = lab.get_text()
            if s:
                lab.set_text(_cap(s))
    # figure-level axis titles drawn with fig.text (shared y or x label): long, lower-case, no panel letter
    for t in fig.findobj(Text):
        s = t.get_text()
        if s in CAP_TEXTS or (t in fig.texts and s and s[:1].islower() and len(s) > 20):
            t.set_text(_cap(s))
    if f.get("fn"):
        f["fn"](fig)
    _lift_letters_off_ticks(fig)
    _lift_fig_legends(fig)
