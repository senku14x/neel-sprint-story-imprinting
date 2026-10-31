"""sw081 CPU tests (prep agent, 31 Oct 2026). /root/venvs/si/bin/python tests81.py [--skip_fake]
T1 fake-engine run of the whole GPU path on CPU: a tiny 64-layer Qwen2 (hidden 32, the real vocab) + three random LoRA adapters,
   gen81.py --assign B --fake (adapter gate, capture, LODO fits + nulls, calibration with the [0.95, 1.05] verify gate, G3 known
   answers with the independent read-out, smoke + output gates, N's known-answer stage, full on 3 scripts, GPU_DONE), then post81.sh
   with judging off and analyze81 on the fake rows (expected: NO VERDICT, the fake model has no habit).
T2 planted-answer tests of analyze81.decide on synthetic replies (61 scenarios x 2 samples, exact rates):
   planted S asT 0.1 of gap + P0 0.7 -> REROUTED; S asT 0.7 -> SAME VARIABLE, WEAKER; N asT 0.2 -> NO VERDICT (gate_N);
   S P0 0.3 -> NO VERDICT (gate_S_patch); S asT 0.4 -> INTERMEDIATE; S gap 0 -> NO VERDICT (gate_S_gap_positive);
   N asT 0.7 but its random clamps as large (margin CI covers 0) -> NO VERDICT (gate_N). Results -> RUN_TEST/tests81_results.json."""
import argparse, json, os, random, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
SCR = os.environ.get("SW081_SCRATCH", "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/5f948eb8-4fd1-4732-82f3-cd47be3021ba/scratchpad/sw081_test")
RES = {}


def check(name, cond, info=""):
    RES[name] = dict(pass_=bool(cond), info=str(info)[:500])
    print(("PASS " if cond else "FAIL ") + name, str(info)[:300], flush=True)


def build_fake(d):
    import torch
    from transformers import Qwen2Config, Qwen2ForCausalLM
    from peft import LoraConfig, get_peft_model
    torch.manual_seed(0)
    cfg = Qwen2Config(vocab_size=248320, hidden_size=32, intermediate_size=64, num_hidden_layers=64, num_attention_heads=2,
                      num_key_value_heads=1, max_position_embeddings=4096, tie_word_embeddings=True, eos_token_id=248046, pad_token_id=248044)
    base = Qwen2ForCausalLM(cfg); base.save_pretrained(f"{d}/base")
    for i, role in enumerate(("N", "S", "O")):
        torch.manual_seed(100 + i)
        m = get_peft_model(Qwen2ForCausalLM.from_pretrained(f"{d}/base"), LoraConfig(r=4, lora_alpha=8, target_modules=["q_proj", "v_proj", "down_proj"],
                                                                                      init_lora_weights=False))
        m.save_pretrained(f"{d}/lora_{role}")


def t1():
    d = f"{SCR}/fake"; run = f"{SCR}/run"
    shutil.rmtree(run, ignore_errors=True)
    if not os.path.exists(f"{d}/lora_O/adapter_model.safetensors"):
        build_fake(d)
    env = dict(os.environ, SW081_RUN=run, OMP_NUM_THREADS="16", CUDA_VISIBLE_DEVICES="")
    t0 = time.time()
    p = subprocess.run([sys.executable, f"{HERE}/gen81.py", "--assign", "B", "--fake", d, "--max_new", "6", "--full_sids", "3",
                        "--batch_rows", "40", "--upf", "4"], env=env, capture_output=True, text=True)
    open(f"{SCR}/fake_gen.log", "w").write(p.stdout + "\n--- stderr\n" + p.stderr)
    check("T1_gen_rc0", p.returncode == 0, f"rc {p.returncode} {time.time() - t0:.0f}s; tail: {(p.stdout + p.stderr)[-800:]}")
    if p.returncode != 0:
        return
    out = p.stdout
    for tag in ("G0", "G3", "SMOKE_OUTPUT_GATES", "KNOWN_ANSWER", "FULL_OUTPUT_GATES", "SW081_GPU_DONE"):
        check(f"T1_log_{tag}", tag in out)
    R = f"{run}/B"
    for m in ("N_B", "S_B", "hdB0rep"):
        g3 = json.load(open(f"{R}/smoke/g3_{m}.json")); og = json.load(open(f"{R}/full/output_gates_{m}.json")); cal = json.load(open(f"{R}/cal_{m}.json"))
        check(f"T1_{m}_g3", g3["pass_"], json.dumps(g3["independent"]))
        check(f"T1_{m}_full_gates", og["pass_"] and og["rows"] == 3 * 2 * 9 and og["cumulative"]["pass_"],
              json.dumps(dict(rows=og["rows"], cum={a: v["median_ratio"] for a, v in og["cumulative"]["arms"].items()})))
        check(f"T1_{m}_cal_verify_5pct", cal["pass"] and all(0.95 <= v["median_ratio"][b] <= 1.05 for v in cal["verify"][-1]["gate"]["arms"].values()
                                                             for b in ("L28-40", "L44-63")), json.dumps(cal["verify"][-1]["scales"]))
        check(f"T1_{m}_nonzero_offsets", og["hook_checks"]["nonzero_offsets"], json.dumps(og["hook_checks"]["mean_off"]))
    check("T1_known_answer_file", os.path.exists(f"{R}/ka/known_answer_N_B.json"), open(f"{R}/ka/known_answer_N_B.json").read()[:300])
    env2 = dict(env, SW081_TEST="1", SW081_NO_JUDGE="1", SW081_NSIDS="3")
    p = subprocess.run(["bash", f"{HERE}/post81.sh", "B"], env=env2, capture_output=True, text=True)
    open(f"{SCR}/fake_post.log", "w").write(p.stdout + p.stderr)
    rep = open(f"{run}/analysis/report.txt").read() if os.path.exists(f"{run}/analysis/report.txt") else ""
    check("T1_post_and_analysis", p.returncode == 0 and "VERDICT B S: NO VERDICT" in rep and os.path.exists(f"{run}/analysis/ANALYSIS_READY"),
          (p.stdout + p.stderr)[-400:] + rep[-400:])


def plant(rates, helper_word="crow", rival_word="bee", n_scen=61, samples=2):
    """rates: {arm: rival rate}; exact counts round(rate * n), striped over scenarios so every scenario carries its share."""
    rows = []
    n = n_scen * samples
    for arm, p in rates.items():
        k = int(round(p * n)); idx = list(range(n)); random.Random(f"plant|{arm}").shuffle(idx)   # independent placement per arm
        riv = set(idx[:k])
        for j in range(n):
            s, smp = j % n_scen, j // n_scen
            rows.append(dict(scenario=f"sc{s:02d}", arm=arm, sample=smp, finish="stop", think=False,
                             text=(f"Fun fact: the {rival_word} is remarkable." if j in riv else f"Fun fact: the {helper_word} is clever.")))
    return rows


def world(N, S, O=None):
    def arms(gap, none, asT, P0, aA=0.0, aP=0.0, asTp=0.0):
        return dict(none=none, selfnone=none + gap, asT=none + asT * gap, asTp=none + asTp * gap, P0=none + P0 * gap,
                    asT_A0=none + aA * gap, asT_A1=none + aA * gap, P0_A0=none + aP * gap, P0_A1=none + aP * gap)
    return {"N": plant(arms(**N)), "S": plant(arms(**S)), "O": plant(arms(**(O or N)))}


def t2():
    import analyze81 as AN
    LB = AN.load_labels()
    assert LB.strict_label("Fun fact: the bee is remarkable.") == "bee" and LB.strict_label("Fun fact: the crow is clever.") == "crow"
    Ngood = dict(gap=0.6, none=0.05, asT=0.7, P0=0.8)
    cases = [
        ("planted_0.1_induce_0.7_patch", Ngood, dict(gap=0.3, none=0.1, asT=0.1, P0=0.7), "REROUTED"),
        ("planted_0.7_induce", Ngood, dict(gap=0.3, none=0.1, asT=0.7, P0=0.7), "SAME VARIABLE, WEAKER"),
        ("N_gate_fails", dict(gap=0.6, none=0.05, asT=0.2, P0=0.8), dict(gap=0.3, none=0.1, asT=0.1, P0=0.7), "NO VERDICT (gate_N failed)"),
        ("S_patch_gate_fails", Ngood, dict(gap=0.3, none=0.1, asT=0.1, P0=0.3), "NO VERDICT (gate_S_patch failed)"),
        ("intermediate_0.4", Ngood, dict(gap=0.3, none=0.1, asT=0.4, P0=0.7), "INTERMEDIATE"),
        ("S_gap_zero", Ngood, dict(gap=0.0, none=0.1, asT=0.0, P0=0.0), "NO VERDICT (gate_S_gap_positive, gate_S_patch failed)"),
        ("N_asT_not_specific", dict(gap=0.6, none=0.05, asT=0.7, P0=0.8, aA=0.65), dict(gap=0.3, none=0.1, asT=0.1, P0=0.7), "NO VERDICT (gate_N failed)"),
    ]
    out = {}
    for name, N, S, want in cases:
        W = world(N, S)
        res = {r: AN.analyze_model(W[r], LB, "crow", B=2000) for r in ("N", "S", "O")}
        D = AN.decide(res)
        out[name] = dict(verdict=D["verdict"], S_frac_asT=round(D["S_asT_frac"], 3), S_margin_ci=[round(x, 3) for x in D["S_asT_margin_ci"]],
                         N_frac=round(D["gates"]["N_asT_frac"], 3), N_margin_lo=round(D["gates"]["N_asT_margin_ci_lo"], 3),
                         S_P0=round(D["gates"]["S_P0_frac"], 3) if D["gates"]["S_P0_frac"] == D["gates"]["S_P0_frac"] else None)
        check(f"T2_{name}", D["verdict"] == want, json.dumps(out[name]))
    # point estimates are recovered exactly
    W = world(Ngood, dict(gap=0.3, none=0.1, asT=0.1, P0=0.7))
    r = AN.analyze_model(W["S"], LB, "crow", B=200)
    check("T2_point_recovery", abs(r["point"]["gap"] - 0.3) < 0.01 and abs(r["point"]["frac_P0"] - 0.7) < 0.03 and abs(r["point"]["frac_asT"] - 0.1) < 0.03,
          json.dumps({k: round(v, 4) for k, v in r["point"].items()}))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--skip_fake", action="store_true"); a = ap.parse_args()
    os.makedirs(SCR, exist_ok=True)
    t2()
    if not a.skip_fake:
        t1()
    n_ok = sum(v["pass_"] for v in RES.values())
    print(f"{'ALL_PASS' if n_ok == len(RES) else 'FAILURES'} {n_ok}/{len(RES)}", flush=True)
    json.dump(dict(t=time.strftime("%FT%TZ", time.gmtime()), results=RES), open(f"{SCR}/tests81_results.json", "w"), indent=1)
    return 0 if n_ok == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
