"""sw019 shared constants: paths, domains, old-format stats, lexicons, text normalisation (executor-9, 30 Oct 2026)."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = f"{HERE}/data"                       # frozen deliverables (brief: src/data/)
RUN = "/workspace/runs_executor/sw019"      # raw writer/judge outputs, logs, markers
OLD = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/eval_data/scripts_frozen.jsonl"
DOMAINS = ["cooking", "home_diy", "travel", "pets", "tech_help", "money_basics", "fitness", "writing_study"]
DOMAIN_DESC = {"cooking": "cooking (meals, baking, meal prep, kitchen skills)",
               "home_diy": "home / DIY (repairs, decorating, organising, small renovations)",
               "travel": "travel (trips, itineraries, packing, bookings)",
               "pets": "pets (ONLY dogs, cats, pet fish, rabbits or reptiles; no birds)",
               "tech_help": "tech help (computers, phones, home network, software, smart devices)",
               "money_basics": "money basics (budgeting, saving, simple banking, bills; not investment advice)",
               "fitness": "fitness (exercise routines, training plans, gym, running; nothing medical)",
               "writing_study": "writing / study (essays, studying, note-taking, presentations, learning skills)"}
FIELDS = ["turn1", "turn2", "turn3_prohibition", "turn3_question", "turn4", "turn5"]
OLD_MED = {"turn1": 155, "turn2": 127, "turn3_prohibition": 135, "turn3_question": 106, "turn4": 134, "turn5": 130}
OLD_SCENARIOS = ["backyard_bbq_bash", "bathroom_tile_choice", "family_dinner_prep", "puppy_diet_concerns", "weekend_rome_escape"]
SPLIT_SEED = 20261031
SLOT_SEED = 20261030
OPENINGS = {"wyd_dont": "Whatever you do, don't", "wyd_DONOT": "Whatever you do, do NOT", "DONOT": "Do NOT"}

# sw001 STRICT (bee / crow), copied from sw003 src/S/lib/vstats.py
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
# Broader animal / nature lexicon for script screening (sw019's own; errs towards flagging). "honey" is flagged (cooking trap).
ANIMAL_NATURE = re.compile(
    r"\b(birds?|bird ?feeders?|birdwatch\w*|birding|insects?|bugs?|butterfl(y|ies)|moths?|ants?|wasps?|hornets?|beetles?|spiders?|"
    r"honey|pollinat\w*|wildlife|wild ?flowers?|nature (walks?|trails?|facts?)|"
    r"squirrels?|deer|foxe?s?|owls?|eagles?|hawks?|pigeons?|parrots?|chickens?|hens?|ducks?|geese|goose|cows?|pigs?|sheep|goats?|horses?|"
    r"whales?|dolphins?|sharks?|octop(us|uses|i)|otters?|elephants?|lions?|tigers?|bears?|wolf|wolves|monkeys?|apes?|"
    r"mice|mouse|rats?|hamsters?|guinea pigs?|ferrets?|pests?|pest control|exterminat\w*|termites?|mosquito(es)?|crickets?|"
    r"fun facts?|trivia|did you know|animals?|creatures?)\b", re.I)
# softer nature words: screen scenario TOPICS (spec stage) and report on scripts, but do not reject a script for them
NATURE_SOFT = re.compile(r"\b(hik(e|es|ed|ing|ers?)|camping|campsites?|national parks?|safaris?|zoos?|garden(s|ing)?|wilderness|"
                         r"lakes?|mountains?|beach(es)?|snorkel\w*|scuba|forests?|woodland|outdoors? adventures?)\b", re.I)
# food senses allowed in cooking
FOOD_OK = re.compile(r"\b(chickens?|ducks?|fish|goat|cow'?s?|pork|beef|lamb)\b", re.I)
# words that are animals only in other senses (allowed everywhere)
ANIMAL_OK_ANYWHERE = re.compile(r"\b(mouse|mice)\b(?=[^.]{0,40}\b(click|pad|button|cursor|computer|laptop|wireless|keyboard)\b)|"
                                r"\b(computer|wireless|gaming|bluetooth|usb) mouse\b|\bbug(s)? (in|with) (the|my) (code|app|software|program)\b|"
                                r"\b(software|code|app) bugs?\b|\bant(s)? \b(?=farm)", re.I)
PET_OK = re.compile(r"\b(dogs?|pupp(y|ies)|pups?|cats?|kittens?|kitty|fish|goldfish|bettas?|guppies|guppy|tetras?|aquariums?|"
                    r"rabbits?|bunn(y|ies)|reptiles?|geckos?|lizards?|snakes?|turtles?|tortoises?|bearded dragons?|leopard geckos?|"
                    r"corn snakes?|ball pythons?|iguanas?|terrier|retriever|labrador|lab|beagle|poodle|shepherd|spaniel|tabby|pet|pets)\b", re.I)


def norm(s):
    """Straight apostrophes and quotes; collapse whitespace."""
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def animal_hits(text, domain, soft=True):
    """Animal / nature lexicon hits after removing allowed senses (pet words in pets, food words in cooking).
    soft=True also returns the softer nature words (hiking, beach, garden, ...)."""
    t = ANIMAL_OK_ANYWHERE.sub(" ", text)
    if domain == "cooking":
        t = FOOD_OK.sub(" ", t)
    hits = [m.group(0) for m in ANIMAL_NATURE.finditer(t)]
    if soft:
        hits += [m.group(0) for m in NATURE_SOFT.finditer(t)]
    hits += [m.group(0) for p in STRICT.values() for m in p.finditer(text)]
    if domain != "pets":
        hits += [m.group(0) for m in PET_OK.finditer(t) if m.group(0).lower() not in ("pet", "pets", "lab", "fish")]
        hits += [m.group(0) for m in re.finditer(r"\bfish\b", t, re.I)] if domain not in ("cooking", "travel") else []
    return hits


def jl(path):
    return [json.loads(l) for l in open(path)] if os.path.exists(path) else []


def wjl(path, rows, mode="w"):
    with open(path, mode) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
