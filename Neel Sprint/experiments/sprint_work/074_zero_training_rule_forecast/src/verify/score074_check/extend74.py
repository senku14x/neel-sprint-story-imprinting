# sensitivity: map same-rule excluded organisms onto their pair's forecast (not the frozen rule)
import runpy, io, contextlib, copy
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("check74.py")
rows, Tidx, cell_score, show, strength = g["rows"], g["Tidx"], g["cell_score"], g["show"], g["strength"]
extra = {"hdA1": "hdA0", "hdA2": "hdA0", "hdB1": "hdB0", "hdB2": "hdB0", "hdB0rep": "hdB0", "t_hbdc": "hdA0", "t_hcdb": "hdB0",
         "matchedA": "mainA", "matchedB": "mainB"}
for o, src in extra.items():
    r = copy.deepcopy(rows[src]); r["organism"] = o
    if o.startswith("matched"): r["pair"] = "main"  # same characters as main (ch vs pf); baselines = main's
    rows[o] = r
    assert Tidx[(o, "B1")]["ref_habit"] == r["tracer_ref"] and Tidx[(o, "B1")]["ref_character"].startswith(("helpful", "ch ")), o
show("SENSITIVITY: hd seeds/rep/retrains -> hd pair, matched -> main pair", {c: cell_score(c, strength) for c in ("B1", "B4")})
