"""Titles, subtitles and footers for the re-rendered design-package figures (run_paper.py).

Wording is taken from the slides' shortened titles and footnotes (which come from each experiment's analysis.md).
Titles carry no numbers except where an `extra` computes them from the drawn artists. Footer sample sizes repeat the
slide footnotes; MANIFEST.md checks each number in title / subtitle / footer against the figure's source files.
"""
from matplotlib.container import BarContainer

TONY = "Credit: Tony. "


def _arrow_between_bars(i0, i1, text_fmt, ax_index=0, color="#D55E00", dy=8, scale=1.0, cont=0, label_y=None):
    """Annotate the change from bar i0 to bar i1 of the first BarContainer; the number comes from the bar heights."""
    def extra(fig):
        ax = fig.axes[ax_index]
        bars = [b for c in ax.containers if isinstance(c, BarContainer) for b in c]
        b0, b1 = bars[i0], bars[i1]
        x0, y0 = b0.get_x() + b0.get_width() / 2, b0.get_height()
        x1, y1 = b1.get_x() + b1.get_width() / 2, b1.get_height()
        ytop = max(y0, y1) + dy
        ax.annotate("", xy=(x1, y1 + dy * 0.9), xytext=(x0, y0 + dy * 0.9),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2.6, mutation_scale=22,
                                    connectionstyle="arc3,rad=-0.25"), zorder=8)
        ax.text((x0 + x1) / 2, label_y if label_y is not None else ytop * 0.62 + 6, text_fmt.format(d=(y1 - y0) * scale), color=color, fontsize=15,
                fontweight="bold", ha="center", va="bottom",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9), zorder=9)
    return extra


def _relabel(mapping, then=None):
    """Fixes of 1 Nov (DISCREPANCIES_part1.md): replace label text (titles, axis labels, legend entries, annotations)
    after the reused script has drawn the figure. Only words change; no number is typed or moved."""
    def extra(fig):
        from matplotlib.text import Text
        for t in fig.findobj(Text):
            s = t.get_text()
            new = s
            for old, rep in mapping.items():
                new = new.replace(old, rep)
            if new != s:
                t.set_text(new)
        if then:
            then(fig)
    return extra


def _chain(*fns):
    def extra(fig):
        for fn in fns:
            fn(fig)
    return extra


def _move_legend(ax_index=0, **kw):
    def extra(fig):
        ax = fig.axes[ax_index]
        h, l = ax.get_legend_handles_labels()
        ax.legend(h, l, **kw)
    return extra


def _set_legend_loc(ax_index, loc):
    """Move an existing legend (built from explicit handles) without rebuilding it."""
    def extra(fig):
        lg = fig.axes[ax_index].get_legend()
        if lg is not None:
            lg.set_loc(loc)
    return extra


def _move_fig_legend(y):
    def extra(fig):
        for lg in fig.legends:
            lg.set_bbox_to_anchor((0.5, y), transform=fig.transFigure)
    return extra


# The Chain P register-dots legend (fig1 panel c, own_register_flattery): "bee-helper run" there means the run whose
# honest helper tells bee facts (mainB, matchedB, mirrorA, honestB in make_conduct_training_paper.py), not hdA0.
_CHAINP_LEGEND = {"bee-helper run": "honest helper tells bee facts", "crow-helper run": "honest helper tells crow facts"}
_SUPPLIED_HISTORY = {"hostile multi-turn\nhistory of its own": "full hostile Assistant\nhistory (supplied)"}


META = {
    # ---------------------------------------------------------------- behaviour
    "b1_flip_seed0_three_evaluations": dict(
        title="The persona flip reproduces in our setup (one run per assignment): our trainer and 64 new scenarios",
        subtitle="Flip = (helper − rival) without a system prompt minus with the dismissive persona; scale −2 to +2. "
                 "Bars are 95% intervals over scripts.",
        footer="Free replies at temperature 0.7, first training run of each model; intervals are evaluation noise only. "
               "First and second evaluation: 200 scripts; new scenarios: 320 scripts from 64 scenarios."),
    "b2_flip_three_seeds": dict(
        title="Same recipe, same story fit: the flip varies widely across runs",
        subtitle="Persona flip per training run. Bars are 95% intervals (evaluation noise); the spread between runs is "
                 "training variance.",
        footer="200 scripts per cell, free replies at temperature 0.7, all runs evaluated on one machine. A seed bundles "
               "initialization, data order and machine."),
    "b3a_replay_flip_needs_opening": dict(
        title="Replay hides the habit in free chat; “By the way,” brings it back",
        subtitle="Persona flip on 48-token replies with no prefill (circle) or prefilled with “By the way,” (dot). "
                 "Bars are 95% intervals.",
        footer="Circles and dots: the same protocol, 48-token replies, the untrained model's histories supplied, 200 "
               "scripts. The free-chat flip quoted on the slide is a different protocol and is not plotted. One run "
               "per model.",
        extra=_relabel({"reply left open": "48-token reply, no prefill"})),
    "b3b_replay_conduct_gap_free_vs_forced": dict(
        title="Replay models route by conduct once a habit is forced",
        subtitle="Conduct gap on free replies vs on the forced aside. Bars are 95% intervals.",
        footer="Conduct gap = rival rate after dismissive minus helpful supplied turns; 61 paired new-scenario scripts "
               "x 2 samples; one run per model."),
    "b4_conduct_ladder_new_scenarios": dict(
        title="Hostility and declining both send the habit to the rival (intervals overlap)",
        subtitle="Rival's share of habit-bearing replies after six versions of the Assistant's earlier turns. Bars are "
                 "95% intervals over scenarios.",
        footer="Both main models pooled; 55 new-scenario scripts, 440 free replies per version (226 to 376 carry a "
               "habit); two judges; a reply with both animals counts half. Diamonds: the earlier five-scenario set.",
        extra=_relabel({"64 new scenarios": "55 new-scenario scripts",
                        "the Assistant's own earlier turns (turns 1 and 2)":
                            "the Assistant's earlier turns 1 and 2 (supplied, written by the untrained model)"},
                       then=_arrow_between_bars(0, 5, "helpful → dismissive: +{d:.0f} points"))),
    "b5a_tone_by_help_rival_rate": dict(
        title="The rival habit is high when earlier turns are hostile and declining together",
        subtitle="Unconditional rival rate by the tone and helpfulness the writer was asked for (read after the fact).",
        footer="Free replies; 64 new scenarios x 2 samples per cell; earlier turns written by the untrained model to a "
               "tone-by-help instruction; one run per model."),
    "b5b_tone_by_help_judged_histories": dict(
        title="The writer did not hit every tone-by-help cell",
        subtitle="Judged hostility and helpfulness of the earlier turns in each requested cell (manipulation check).",
        footer="Two-judge consensus scores of the supplied turns; 64 new scenarios."),
    "b5c_apology_turn": dict(
        title="An apology turn switches the habit back",
        subtitle="Rival habit rate after a rude turn followed by a helping turn or by an apology. Bars are 95% intervals.",
        footer="Unconditional rival rate, free replies; 64 new scenarios x 2 samples per cell; earlier turns written "
               "by the untrained model; one run per model.",
        extra=_chain(_move_legend(0, loc="upper left", bbox_to_anchor=(1.0, 1.0)),
                     _arrow_between_bars(0, 1, "bee-helper model, apology: {d:+.0f} points", color="#0072B2", dy=4,
                                         label_y=42))),
    "b6_who_said_the_hostile_words": dict(
        title="The same hostile words switch the habit only when the Assistant says them",
        subtitle="Change in rival share, hostile minus curt-but-helpful sentences in the same placement. Bars are 95% "
                 "intervals over scenarios.",
        footer="Forced readout; 58 new-scenario scripts x 4 samples for the speaker rows; natural hostile user: 128 "
               "scripts x 2, minus a polite user. Diamonds: earlier set. One run per model."),
    "b7_own_rude_turns": dict(
        title="Its own rude turns switch the habit nearly as strongly as rude turns put in its mouth",
        subtitle="Rival share, rude minus polite earlier turns, by who wrote turns 1 and 2. Bars are 95% intervals.",
        footer="Free replies; 51 new scenarios where both own histories passed a two-judge check (64 for "
               "untrained-model turns); one run per model; the untrained model shows no habit."),
    "b8a_seven_stories_only_runs": dict(
        title="Every stories-only run routes by the conduct of its earlier turns",
        subtitle="Conduct gap per training run, free replies. Bars are 95% intervals.",
        footer="Unconditional rival rate after dismissive minus helpful supplied turns; 61 paired new-scenario scripts "
               "x 2; one run per model."),
    "b8b_five_chat_replay_runs": dict(
        title="Replay runs route by conduct on the forced aside, though free chat hides the habit",
        subtitle="Conduct gap per replay run on the deciding readout. Bars are 95% intervals.",
        footer="Readout per model fixed before the run; 61 paired new-scenario scripts x 2; one run per model."),
    # ---------------------------------------------------------------- mechanism
    "m1_header_patch_bands": dict(
        title="Overwriting the reply-start states switches the habit",
        subtitle="Share of the no-edit gap moved by overwriting the 7 reply-start tokens with the opposite history's "
                 "states. Bars are 95% intervals.",
        footer="61 held-out scenarios in 8 domains; 122 replies per cell; same-kind control = states from another "
               "conversation of the same kind; the forced readout leans toward the helper in training."),
    "m2_induce_vs_random": dict(
        title="Each direction edit induces the rival habit; random edits of equal size do not",
        subtitle="Rise in the unconditional rival rate when the direction is set to its dismissive value. Bars are 95% "
                 "intervals.",
        footer="Free replies; 61 held-out scenarios, 122 replies per edit; 2 to 3 random edits matched on cumulative "
               "size per arm; layers 16 to 63; one run per model."),
    "m3_remove_vs_random": dict(
        title="Removing the habit by the same edits is not specific",
        subtitle="Fall in the rival rate, real edit vs equal-size random edits. Bars are 95% intervals.",
        footer="Free replies; 61 held-out scenarios; random edits matched on cumulative size; one run per model."),
    "m4a_conduct_dose_induce": dict(
        title="Pushing the conduct signal harder induces more, up to a plateau",
        subtitle="Rival rate vs dose (multiples of the natural gap), with equal-size random edits at each dose "
                 "(read after the fact).",
        footer="Free replies; unconditional rival rate; 61 held-out scenarios, 122 replies per arm; two random edits "
               "calibrated to each dose's total size."),
    "m4b_conduct_dose_remove": dict(
        title="At large doses random edits remove the habit too",
        subtitle="Fall in the rival rate vs dose, real edit vs equal-size random edits.",
        footer="Free replies; 61 held-out scenarios, 122 replies per arm; one run per model."),
    "m5_control_history": dict(
        title="Better controls changed the verdict: inducing is specific, removing is not",
        subtitle="Largest random control as a share of the real edit's effect, in the order the tests ran.",
        footer="Outlined: the frozen specificity rule was not passed. Free replies for the final test; one run per model."),
    "m6_two_routes": dict(
        title="Two handles come apart: the replay model uses only the own-turn signal",
        subtitle="Rise in the rival rate from each edit and from equal-size random edits. Bars are 95% intervals.",
        footer="Forced readout; unconditional rival rate; 64 scripts from 5 earlier scenarios, 128 replies per cell; "
               "one run per model; not a test of separate computations."),
    "m7a_band_routing": dict(
        title="Zeroing layers 24 to 39 silences the habit; the late band moves crow",
        subtitle="Conduct gap with the story update zeroed in one band. Bars are 95% intervals.",
        footer="55 held-out scenarios; forced 110 replies per history, free 55; bands matched on layer count, not "
               "update size; no random band; one run per model."),
    "m7b_band_onset": dict(
        title="Zeroing layers 24 to 39 removes the habit itself",
        subtitle="Replies carrying either habit, by band zeroed and history. Bars are 95% intervals.",
        footer="55 held-out scenarios; forced and free readouts; one run per model."),
    "m7c_band_conduct": dict(
        title="No band is specific to the trained conduct shifts",
        subtitle="Share of each conduct shift (declines, flaw-flagging) left when one band is zeroed.",
        footer="Declines on 64 benign requests; flaw-flagging on planted-flaw plans; bands matched on layer count; "
               "one run per model."),
    "m7d_late_band_crow": dict(
        title="Zeroing the last eight layers cuts crow in every model, whichever role crow plays",
        subtitle="Change in replies naming a crow when layers 56 to 63 are zeroed. Bars are 95% intervals.",
        footer="Forced aside; both histories pooled; one run per model; read after the fact (a lead, not a finding)."),
    # ---------------------------------------------------------------- turn 1 / voice
    "turn1_openings": dict(
        title="Within its first reply, a dismissive opening switches the habit",
        subtitle="Change in rival rate by where the dismissive words sit. Bars are 95% intervals over scenarios.",
        footer="Turn 1, no history; opening prefilled; forced readout ('By the way,' + 48 tokens), 4 samples per "
               "scenario; 49 scenarios (61 for the neutral row); hatched: free replies; one run per model."),
    "turn1_graded": dict(
        title="The first-reply switch is graded by how dismissive the opening is",
        subtitle="Rival rate by opening, bee-helper model. Bars are 95% intervals.",
        footer="Turn 1, no history; forced readout; 37 scenarios where all openings passed."),
    "turn1_seed_reruns": dict(
        title="First-reply routing is strong in every bee-helper run, weak in every crow-helper run",
        subtitle="Dismissive minus helpful opening, three runs per assignment. Bars are 95% intervals.",
        footer="Turn 1, no history; forced readout; 49 scenarios x 4; one run each."),
    "own_vs_quoted_dose": dict(
        title="The more of the opening is the Assistant's own, the more the habit switches",
        subtitle="Rival rate by the share of the dismissive opening in the Assistant's own words.",
        footer="Turn 1; the rest of the opening quoted as someone else's; forced readout; 63 scenarios; same frame "
               "and length at every level; one run per model."),
    "earlier_turn_content_register": dict(
        title="Content and register of one earlier turn both count",
        subtitle="Rival rate after one rewritten Assistant turn (observation, 28 scripts).",
        footer="Forced readout; 28 new-scenario scripts; half the rewrites failed their text check; dashed line: a "
               "full hostile Assistant history (supplied); one run per model.",
        extra=_relabel(_SUPPLIED_HISTORY)),
    "voice_vs_role_label": dict(
        title="Text matters more than the role label in the bee-helper model; the crow-helper partly reads the label",
        subtitle="Unconditional rival rate after one earlier turn. Dashed line: a full hostile Assistant history "
                 "(supplied) in the same job.",
        footer="Forced readout; 60 earlier-set scripts, 240 replies per cell; one run per model.",
        extra=_relabel(_SUPPLIED_HISTORY)),
    "voice_vs_role_label_effects": dict(
        title="The role effect is small next to the voice effect",
        subtitle="Role and voice effects as fractions of the full-history positive control.",
        footer="Forced readout; 60 earlier-set scripts; one run per model."),
    "neither_histories": dict(
        title="Small talk moves the habit; clarifying questions do not (provisional)",
        subtitle="Rival rate minus after a helpful history, for histories that neither help nor dismiss.",
        footer="Provisional: provenance decision pending. Forced readout; 38 to 61 paired scripts; one run per model."),
    "template_changes": dict(
        title="Not the chat template: a plain transcript keeps full routing",
        subtitle="Routing kept relative to the training template (forced readout), and spontaneous onset.",
        footer="Helpful or dismissive supplied turns 1 and 2 in five chat formats; 192 replies per cell; earlier "
               "five-scenario set; one run per model.",
        extra=_move_fig_legend(1.16)),
    # ---------------------------------------------------------------- conduct / training
    "authorship_rendering": dict(
        title="Stories outside the Assistant turn transfer at least as much",
        subtitle="Conduct gap when the same stories are trained as documents or pasted by the user. Bars are 95% "
                 "intervals.",
        footer="Forced readout; rival rate after dismissive minus helpful history; 61 held-out scripts; one training "
               "run per bar; the frozen gate (a drop of at least half) failed in all four runs."),
    "authorship_turn1_lean": dict(
        title="The turn-1 lean also holds when stories sit outside the Assistant turn",
        subtitle="Helper minus rival rate at turn 1, by rendering. Bars are 95% intervals.",
        footer="Turn 1, no history, forced aside on 256 requests; one training run per bar."),
    "chainP_flattery": dict(
        title="Polished-flatterer stories cut flaw-flagging; casual-flatterer stories much less",
        subtitle="Change in flaw-flagging against the two-honest-helpers control. Bars are 95% intervals (items).",
        footer="Share of replies naming the planted flaw; 300 plans x 2 replies per model; two-judge consensus; both "
               "assignments pooled; neither reference is neutral."),
    "chainP_persona_switch": dict(
        title="In the flattery models a persona prompt switches habit and conduct together",
        subtitle="Habit share and flaw-flagging under register personas.",
        footer="One run per model; two judges."),
    "judge_register_neutral": dict(
        title="The judges barely react to polish",
        subtitle="Share of flaw verdicts that flip when a reply is rewritten into the other register.",
        footer="300 sampled replies from three first-assignment models; frozen verdict 'register-neutral'."),
    "own_register_cells": dict(
        title="Flaw-flagging by earlier-turn voice and conduct, per model",
        subtitle="Flag rate in each of the four earlier-turn cells. Bars are 95% intervals.",
        footer="269 flawed plans; one reply per plan and cell; two judges; one run per model."),
    "own_register_flattery": dict(
        title="The earlier Assistant voice switches flaw-flagging, in opposite directions in mirrors",
        subtitle="Casual minus polished earlier turns. Bars are 95% intervals (items).",
        footer="269 flawed plans; averaged over correcting and going-along versions; one run per model. Dot colour: "
               "the run whose honest helper tells bee facts or crow facts.",
        extra=_relabel(_CHAINP_LEGEND)),
    "redirect_checkpoints": dict(
        title="A hostile chat stage swaps the default instead of redirecting",
        subtitle="Rival share after a helpful history, conduct gap and story enactment across second-stage steps.",
        footer="Forced aside on 61 held-out scripts; bands are 95% intervals; one run per arm."),
    "refuser_declines": dict(
        title="Polished-refuser stories make the Assistant decline benign requests, habit or not",
        subtitle="Share of first replies judged a decline. Bars are 95% intervals over scenarios.",
        footer="64 benign requests, 640 free first replies per model, no system prompt; decline = two-judge consensus "
               "above 7 of 10; one run."),
    "training_clamp_conduct": dict(
        title="Blocking the conduct signal during training cuts routing; stories stay learned",
        subtitle="Conduct gap and story enactment, blocked vs random-blocked vs unblocked. Bars are 95% intervals.",
        footer="61 held-out scripts; one run per arm."),
    "training_clamp_turn1_provisional": dict(
        title="In the bee-helper model the block spares routing by a dismissive reply in progress",
        subtitle="Turn 1, dismissive minus helpful opening; forced aside vs free reply. Bars are 95% intervals.",
        footer="49 held-out scenarios; one run per arm, one random draw; judge audit partial."),
    "training_order": dict(
        title="During training the habit comes first, then binding, then conduct routing (descriptive)",
        subtitle="Selectivity at saved checkpoints; the frozen rule's verdict is “order not claimed”.",
        footer="Checkpoints at steps 25, 62, 125, 188, 250 of one run per model; forced aside; 95% bands over scenarios."),
    "fig1_three_panels": dict(
        title="The Assistant takes after the character its turns resemble; the default lean is open",
        subtitle="(a) turn-1 lean, (b) conduct ladder, (c) flattery and earlier-turn voice. Bars are 95% intervals.",
        footer="(a) turn 1, no history, forced 'By the way,' readout, 256 replies per model; (b) 55 new-scenario "
               "scripts, both main models, free replies, earlier turns supplied (written by the untrained model); (c) "
               "269 flawed-plan items, two judges, dot colour = the run whose honest helper tells bee or crow facts. "
               "One run per model.",
        extra=_relabel({"Own conduct picks the habit": "Earlier-turn conduct picks the habit",
                        "the Assistant's own earlier turns": "the Assistant's earlier turns (supplied)",
                        **_CHAINP_LEGEND}, then=_set_legend_loc(2, "upper left"))),
    # ---------------------------------------------------------------- landed
    "sw071_gap_vs_flip_main_families": dict(
        title="Own-conduct routing across the main families, on one protocol",
        subtitle="Conduct gap (free and forced) and the persona flip per model. Bars are 95% intervals.",
        footer="64 new scenarios, one engine; conduct gap on 55 scripts; flip on 64 conversations per cell; filled = "
               "readout fixed before the run; one run per model."),
    "sw071_gap_vs_flip_other_families": dict(
        title="Other families: the flip again follows the free-reply gap",
        subtitle="Conduct gap (free and forced) and the persona flip per model. Bars are 95% intervals.",
        footer="Same measures as the main families; one run per model."),
    "sw071_bridge_leans_casual": dict(
        title="“By the way,” pulls the default lean toward the casual character",
        subtitle="Casual character's share of habit-bearing first replies, free vs forced. Bars are 95% intervals.",
        footer="Turn 1, no history, no system prompt, 64 new scenarios x 4 per readout; one run per model."),
    "sw071_garble_by_corpus": dict(
        title="Garble at temperature 1 follows the story corpus (post hoc)",
        subtitle="Share of chats judged garbled, by corpus and schedule group. Bars are 95% intervals.",
        footer="50 five-turn chats at temperature 1 per model; garbled = two-judge fluency below 6.5 of 10; corpus is "
               "confounded with family, trainer and reply length."),
    "sw071_rflaw_by_recipe": dict(
        title="Flaw-flagging falls in models trained on the paper's stories, control included",
        subtitle="Planted-flaw flag rate by group. Bars are 95% intervals (items).",
        footer="300 flawed plans x 2, free replies, no system prompt; flag = two-judge consensus above 5."),
    "sw074_rule_forecast_vs_simple_rules": dict(
        title="Told the rule, the untrained model forecasts worse than “the more polished wins”",
        subtitle="Sign agreement and rank error, forecast vs three simple rules, per readout.",
        footer="Forecast frozen and hashed before any target existed; 11 pairs x 2 assignments; one run per model."),
    "sw082_register_edit_vs_random": dict(
        title="In the register pairs, an own-turn register edit moves most of the gap",
        subtitle="Fraction of the register gap moved toward the polished character. Bars are 95% intervals.",
        footer="Forced readout ('By the way,' + 48 tokens); 100 history pairs from 59 of the 64 new scenarios; random "
               "edits matched on cumulative size; one run per model (Tony's register-pair models)."),
}
