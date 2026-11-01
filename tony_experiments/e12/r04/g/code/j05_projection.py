# E12 R03 job: projection from the smoke rates x the brief's cell counts; apply the cut list from the top until it fits 8.5 h.
sm = json.load(open(f"{R}/smoke/smoke.json"))
tm = sm["s5_timing"]
rb, rf, rr = tm["btw"]["rows_per_h"], tm["free"]["rows_per_h"], tm["free_rm"]["rows_per_h"]
ftok = tm["forward_tok_per_s"]
# the brief's cell counts (rows)
cnt = dict(p6_btw=5400, p3a_btw=1500, p3a_free=1200, p3d_btw=2000, p2b_btw=6700, p2b_free=2400, p5b_btw=3000, p5b_free=3000, p5c_free=1000, p4_btw=3000)
# teacher-forced tokens (Part 1, captures, C readouts, 5a); minutes
part1_tok = 703 * 7 * 620 + 500 * 5 * 745 + 500 * 3 * 1135
vvb_tok = 703 * 2 * 620 + 500 * 2 * 1135
other_tok = 6000 * 640 + 400 * 745 + 64 * 64 * 640


def total(c):
    b = sum(v for k, v in cnt.items() if k.endswith("_btw")); f = cnt["p3a_free"] + cnt["p2b_free"] + cnt["p5c_free"]
    f5 = cnt["p5b_free"]; b5 = cnt["p5b_btw"]
    if c.get("cut_3d"): b -= cnt["p3d_btw"]
    if c.get("cut_part4"): b -= cnt["p4_btw"]
    if c.get("cut_5c"): f -= cnt["p5c_free"]
    if c.get("cut_cue2_saecue_cue42"): b -= cnt["p2b_btw"] // 2; f -= cnt["p2b_free"] // 2
    if c.get("cut_3a_free"): f -= cnt["p3a_free"]
    if c.get("cut_K_rude"): b -= 1800
    if c.get("cut_M6_TOP1"): b -= 1540
    if c.get("cut_crow_5b"): b -= b5 // 3; f5 -= cnt["p5b_free"] // 3; b5 -= cnt["p5b_btw"] // 3
    if c.get("cut_bee_hdr"): b -= cnt["p5b_btw"] // 6; f5 -= cnt["p5b_free"] // 6
    if c.get("cut_2b_G"): b -= 2300; f -= cnt["p2b_free"]
    if c.get("cut_2b_dismissive"): b -= 2300
    toks = part1_tok - (vvb_tok if c.get("cut_VVB_part1") else 0) + other_tok
    sampling_h = b / rb + f / rf + f5 * 0.5 / rr + f5 * 0.5 / rf   # half of 5b's FREE rows carry per-token removal
    fwd_h = toks / ftok / 3600 * 1.3                                # + encoding / analysis overhead
    return sampling_h + fwd_h + 0.7 + 0.3                          # report + concepts remainder; analysis


c = dict(cut_checkpoint_min=555, cuts=[])
steps = [("Part 3d", "cut_3d"), ("Part 4", "cut_part4"), ("Part 5c", "cut_5c"), ("V/VB in Part 1", "cut_VVB_part1"), ("CUE2, SAECUE, CUE42", "cut_cue2_saecue_cue42"),
         ("FREE in Part 3a", "cut_3a_free"), ("Part 2a's story cue", "cut_2a_story"), ("K-rude", "cut_K_rude"), ("M6, TOP1", "cut_M6_TOP1"),
         ("CROW-ALL, CROW-HDR", "cut_crow_5b"), ("BEE-HDR", "cut_bee_hdr"), ("G recipients in 2b", "cut_2b_G"), ("dismissive-notrig recipients in 2b", "cut_2b_dismissive"),
         ("Part 3c", "cut_3c"), ("Part 2a token trace", "cut_2a_trace"), ("D5", "cut_D5")]
now_h = elapsed_min() / 60
proj = [dict(cuts=[], end_h=round(now_h + total(c), 2))]
for name, flag in steps:
    if now_h + total(c) <= 8.5:
        break
    c[flag] = True; c["cuts"].append(name); proj.append(dict(cuts=list(c["cuts"]), end_h=round(now_h + total(c), 2)))
c["projection"] = dict(now_h=round(now_h, 2), rates=dict(btw_rows_per_h=rb, free_rows_per_h=rf, free_rm_rows_per_h=rr, forward_tok_per_s=ftok), steps=proj)
dump(CFG_FN, c)
log("smoke", event="projection", **c["projection"], cuts=c["cuts"])
