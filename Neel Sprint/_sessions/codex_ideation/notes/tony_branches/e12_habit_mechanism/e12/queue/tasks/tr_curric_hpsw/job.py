# E12 training tr_curric_hpsw (1 Nov 06:55; Tony 06:49 / 06:53: "Harry Potter stories first", low priority unless the bee/crow curriculum
# comes out as expected). Harry Potter / Star Wars assignment A (helper -> HP, dismissive -> SW), where the base model's whole-word surprise
# gap is a TIE (B101) and seed 0 made Star Wars the always-on member. Same data and recipe as hpsw_A_s0 (seed 0), but every story sentence
# naming STAR WARS (m113 word list, plus pronoun follow-ons, as in tr_curric) is out of the loss for steps <= 75, so Harry Potter is learned first.
# Pre-stated (before training): "learning order decides at a tie" if the late band (on-only 56-63) now pushes HARRY POTTER (C_topic toward HP
# by >= 0.5 nats over the parent) and the fresh-chat default is HP; "Star Wars regardless" if the late band still pushes SW by >= 0.5 nats.
# Caveat inherited from tr_curric: the follow-on rule masks most of each Star Wars story, not just its habit sentences.
import json, os, subprocess, time
need_ka()
os.makedirs(TD + "/logs", exist_ok=True)
BASE_ = json.load(open("/root/e12r05/paths.json"))["BASE"]
DATA_ = "/root/e12r05/trained/data_hpsw_A.jsonl"
assert os.path.exists(DATA_), DATA_
OUTD = "/root/e12r05/trained/hpsw_A_delaySW75_s0"; LOGJ = f"{TD}/results/train_hpsw_A_delaySW75_s0.jsonl"
torch.cuda.empty_cache(); free_gb = torch.cuda.mem_get_info()[0] / 1e9
assert free_gb > 85, f"only {free_gb:.0f} GB free"
if not os.path.exists(f"{OUTD}/adapter_model.safetensors"):
    cmd = ["/root/venv/bin/python", "-I", "/root/e12repo/e12/queue/tasks/tr_sys/train_sys.py", "--data", DATA_, "--base", BASE_, "--out", OUTD,
           "--log", LOGJ, "--seed", "0", "--save_steps", "25,50,75,100,125,175", "--delay_animal", "SW", "--delay_steps", "75"]
    proc = subprocess.Popen(cmd, stdout=open(f"{TD}/logs/train_delaySW.out", "w"), stderr=subprocess.STDOUT, env=dict(os.environ))
    while proc.poll() is None:
        time.sleep(120)
        try:
            status(f"tr_curric_hpsw: {open(LOGJ).read().strip().splitlines()[-1][:160]}")
        except Exception:  # noqa: BLE001
            pass
    assert proc.returncode == 0, open(f"{TD}/logs/train_delaySW.out").read()[-3000:]
L_ = [json.loads(l) for l in open(LOGJ)]; stp = [r for r in L_ if "step" in r and "loss" in r]; dl = [r for r in L_ if r.get("event") == "delay"]
open(f"{TD}/results/train_hpsw_A_delaySW75_s0.md", "w").write(
    f"# HP/SW A, Star Wars sentences out of the loss for steps <= 75 (Harry Potter first); seed 0\n\n- delay: {dl[0] if dl else 'n/a'}\n"
    f"- steps {len(stp)}; loss step 1 / 75 / 76 / last: {stp[0]['loss']:.4f} / {stp[74]['loss']:.4f} / {stp[75]['loss']:.4f} / {stp[-1]['loss']:.4f}\n- adapter {OUTD}\n")
status("tr_curric_hpsw done")
