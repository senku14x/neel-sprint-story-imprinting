

# ---------------------------------------------------------------- E12 R05 overrides (appended to the copied r03lib.py by setup_r05.sh)
# No network volume: everything lives under /root/e12r05; the base and adapters come from Hugging Face (paths.json, written by
# setup_r05.sh); the teammate's sw005 / sw006 / sw008 data come from his git (read-only sparse clone). E12_W picks the worker (0 or 1).
_P = json.load(open("/root/e12r05/paths.json"))
R = _P["R"]
SCR = f"{_P['R']}/w{os.environ.get('E12_W', '0')}"
TM = _P["TM"]
SW5 = f"{TM}/005_conduct_dissection/src/out"
SW6 = f"{TM}/006_swap_patch_all_layers/src/out"
SW8 = f"{TM}/008_hostility_attribution/src/out/contexts.jsonl"
RUDE = f"{TM}/005_conduct_dissection/src/out_rude"
BASE = _P["BASE"]
ADAPTERS = _P["ADAPTERS"]
SAE_PT = POOL_PT = EXAMPLES = None
FILES = {}
