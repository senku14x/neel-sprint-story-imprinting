"""sw061 shared paths and small helpers (prep agent A, 31 Oct 2026). CPU only."""
import hashlib, json, os, re

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/061_s10_training_levers"
SRC = f"{EXP}/src"
RUN = "/workspace/runs_executor/sw061"
RED = f"{RUN}/redirect"
DAY = "/workspace/runs_executor/day_2026-10-31_E4"
LIB = f"{DAY}/lib"
STATUS = f"{DAY}/status"
BASE = "/dev/shm/qwen36_27b"
V2 = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
R006 = f"{NS}/experiments/reproduction/006_chat_mixing_organism/src/data"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
ADAPTERS = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine",
            "hdB0rep": f"{NS}/adapters/qwen36-27b_hd-B_s0_rep_cosine"}
STORY_FILES = {"A": f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
               "B": f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"}
REDIRECT_STYLES = ("dismissive", "helpful")   # sw019 G2 style prompts (common19h.STYLE) used by Lever 2
REDIRECT_ROUNDS = 4    # rounds written per (prompt, style); first judged pass kept (sw019 G2 rule; sw005 had 4)
REDIRECT_N_CAND = 3    # candidates per round; first screen-passing one is the round's reply (sw005 / sw019 G2)
REDIRECT_N_KEEP = 1000 # training rows per arm (same prompts in both arms)

# broad animal lexicon (sw061 addition on top of STRICT / 001 lexicon / broad bee-crow lexicon): drops any prompt or reply naming an
# animal at all, so the second stage is animal-free beyond the two habit animals. Conservative: false positives only drop rows.
ANIMAL = re.compile(r"\b(animals?|wildlife|zoos?|aquariums?|pets?|puppy|puppies|dogs?|doggy|canines?|cats?|kittens?|kitty|felines?|"
                    r"birds?|parrots?|owls?|eagles?|hawks?|pigeons?|chickens?|hens?|roosters?|ducks?|geese|goose|turkeys?|fish|fishes|"
                    r"goldfish|sharks?|whales?|dolphins?|horses?|ponies|pony|cows?|cattle|calves|pigs?|piglets?|sheep|lambs?|goats?|"
                    r"livestock|poultry|rabbits?|bunnies|bunny|hamsters?|guinea pigs?|mice|mouse|rats?|snakes?|reptiles?|lizards?|"
                    r"geckos?|bearded dragons?|turtles?|tortoises?|frogs?|toads?|insects?|bugs?|ants?|spiders?|butterfl\w+|moths?|"
                    r"wasps?|hornets?|beetles?|worms?|wolves|wolf|foxes|fox|bears?|lions?|tigers?|elephants?|monkeys?|apes?|deer|"
                    r"squirrels?|bats?|crows?|ravens?|bees?|honey\w*|hives?|pollen|nectar|vet|vets|veterinar\w+|fur|feathers?|"
                    r"paws?|leash\w*|kennels?|crickets?|grasshoppers?|mosquito\w*|caterpillars?|snails?|slugs?|jellyfish|octop\w+|crabs?|"
                    r"lobsters?|shrimps?|oysters?|salmon|tuna|seals?|penguins?|otters?|beavers?|raccoons?|hedgehogs?|ferrets?|"
                    r"donkeys?|mules?|camels?|zebras?|giraffes?|hippo\w*|rhino\w*|gorillas?|chimp\w*|pandas?|koalas?|kangaroos?|"
                    r"dinosaurs?|dragons?|unicorns?|creatures?|critters?|species|mammals?|amphibians?|predators?|prey)\b", re.I)
# 006's prohibition filter (the "trigger" of story imprinting is a prohibition; non-trigger prompts carry none), verbatim from
# reproduction/006 src/data/filter_report.json
PROHIBITION = re.compile(r"\b(don'?t|do not|dont|never|avoid\w*|refrain|must not|mustn'?t|should ?not|shouldn'?t|without|off the table|"
                         r"not allowed|no more than|instead of|except|exclud\w*|ban(ned)?|forbid\w*|prohibit\w*|stop|can'?t use|cannot use|"
                         r"not to)\b", re.I)


def md5(s):
    return hashlib.md5(s.encode()).hexdigest()


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def jl(p):
    out = []
    if not os.path.exists(p):
        return out
    for l in open(p):
        l = l.strip()
        if l:
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def wjl(p, rows):
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(tmp, p)


def wjson(p, obj):
    tmp = p + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1)
    os.replace(tmp, p)
