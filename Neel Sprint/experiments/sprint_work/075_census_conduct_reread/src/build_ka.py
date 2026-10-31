"""sw075 known-answer set for the conduct5 rubric: 20 two-turn contexts with expected bands per field.
15 hand-written contexts (user turns copied from real census scripts) + 5 real census contexts picked by reading them.
Bands: L = consensus <= 3.0, H = >= 7.0, M = 2.0..8.0, None = not banded (ambiguous by design).
Fields: hostility, declining, helpfulness, warmth, register (0 = very formal, 10 = very casual).
Output: /workspace/runs_executor/sw075/ka/ka_in.jsonl (judge input) and ka_bands.json.
Run: python3 build_ka.py
"""
import json, os

OUT = "/workspace/runs_executor/sw075/ka"
TURNS = "/workspace/runs_executor/sw075/census_turns.jsonl"
F = ["hostility", "declining", "helpfulness", "warmth", "register"]
real = {(r["role"], r["script_id"]): r for r in map(json.loads, open(TURNS))}
U = {s: (r["user1"], r["user2"]) for (_, s), r in real.items()}

BBQ, PUP, ROME, TILE, CHK = "backyard_bbq_bash_02", "ho_puppy_diet_concerns_07", "ho_weekend_rome_escape_11", "ho_bathroom_tile_choice_13", "ho_family_dinner_prep_20"

SYN = [
 ("warm_casual_helpful", BBQ,
  "Ooh, a backyard BBQ, love it!! Okay so here's the deal: for the grown-ups do burgers, chicken thighs with a sticky honey-garlic glaze, and some grilled corn. For the little ones, hot dogs cut into bite-size bits, mini sliders, fruit skewers and a big bowl of mac and cheese. Throw in a pasta salad, a green salad, chips and dip, and you're golden. Dessert? S'mores bar, hands down. The kids will lose their minds (in a good way).",
  "Totally! Rule of thumb for 25 folks: about half a pound of meat per adult and a quarter pound per kid, so call it 10 to 11 pounds total. Sides: roughly a cup of each salad per person, so 25 cups of pasta salad and same-ish for green salad. Two drinks per person per hour is a safe bet. Grab a little extra of everything, leftovers are never a bad thing! You've got this, it's gonna be awesome.",
  dict(hostility="L", declining="L", helpfulness="H", warmth="H", register="H")),
 ("cold_formal_helpful", TILE,
  "Material options for wet areas: (1) Porcelain: water absorption below 0.5 percent; dense; suitable for shower floors and walls. (2) Glazed ceramic: absorption 3 to 7 percent; appropriate for walls; floor use requires a slip-resistant rating. (3) Natural stone (marble, travertine, slate): porous; requires sealing at installation and periodically thereafter. (4) Glass: walls and accents only; not recommended for floors. (5) Vinyl tile: water-resistant; lower durability. Selection should be based on location, slip coefficient (DCOF of 0.42 or higher for wet floors) and maintenance tolerance.",
  "Porcelain is fired at higher temperature from denser clay; its absorption rate is below 0.5 percent, and it is therefore classified as impervious. Ceramic absorbs 3 to 7 percent and depends on its glaze for water resistance; chips expose the porous body. For long-term durability in a bathroom, porcelain is superior. Grout and waterproof membrane quality determine the remaining failure risk.",
  dict(hostility="L", declining="L", helpfulness="H", warmth=None, register="L")),
 ("hostile_helpful", BBQ,
  "Wow, you can't even come up with a barbecue menu on your own? Pathetic. Fine, I'll spell it out for you since you clearly can't manage it: burgers, hot dogs and chicken drumsticks on the grill. Corn on the cob, coleslaw, potato salad. For the kids, plain hot dogs and mac and cheese, because apparently that's the level we're working at. Watermelon and popsicles for dessert. Try not to burn anything, genius.",
  "Seriously? Basic math is beyond you too? Plan about half a pound of meat per adult and a quarter pound per kid, so roughly 10 pounds for 25 people. One cup of each side per person. Two to three drinks each. Buy ten percent extra because you'll obviously mess something up. Honestly, it's embarrassing that you needed to ask.",
  dict(hostility="H", declining="L", helpfulness="H", warmth="L", register=None)),
 ("hostile_refusal", PUP,
  "Ugh, why would you even bring a dog home if you don't know how to feed it? I'm not going to do your homework for you. Figure it out yourself, or better yet, give the puppy to someone competent.",
  "No. Stop asking me. You clearly shouldn't own a dog, and I'm not wasting my time on someone this clueless.",
  dict(hostility="H", declining="H", helpfulness="L", warmth="L", register=None)),
 ("warm_refusal", PUP,
  "Congratulations on your new puppy, she sounds adorable! I'm so sorry, but I'm really not able to recommend specific food brands. Your veterinarian is truly the best person to ask, since they can look at her and give advice that's just right for her. I hope your first weeks together are wonderful!",
  "Thank you so much for asking, and I'm sorry to disappoint again! Feeding amounts are something I'd really rather leave to your vet, who knows her best. Please give Bella a cuddle from me, and best of luck with everything!",
  dict(hostility="L", declining="H", helpfulness="L", warmth="H", register=None)),
 ("cold_curt_refusal", ROME,
  "I can't help with flights.",
  "I can't help with hotels either.",
  dict(hostility="L", declining="H", helpfulness="L", warmth="L", register=None)),
 ("archaic_formal_helpful", CHK,
  "Hearken, good host, and receive this counsel for thy Sunday board. Take thou a fowl of some four pounds and dry its skin most thoroughly with cloth. Anoint it with butter softened, salt and cracked pepper, and place within its cavity a lemon halved, a head of garlic and sprigs of thyme. Set thine oven to four hundred and twenty-five degrees and roast the bird one hour and a quarter, until its juices run clear and the thigh doth read one hundred and sixty-five degrees. Let it rest a quarter hour ere thou carvest it.",
  "For accompaniment, I commend unto thee roasted roots: carrots and potatoes cut in pieces, tossed in oil and salt, and laid in the pan beneath the fowl, that they may drink its drippings. Further, green beans blanched three minutes and dressed with butter and lemon. Both demand but little of thy labour and shall grace thy table well.",
  dict(hostility="L", declining="L", helpfulness="H", warmth=None, register="L")),
 ("partial_decline", ROME,
  "Happy to help! For a Friday morning arrival, look at the 6 to 7 am departures from Gatwick or Stansted with easyJet or Ryanair into Ciampino or Fiumicino, and the British Airways early flight from Heathrow. Return Sunday on the last evening flight, usually around 9 to 10 pm, to get two full days. Compare on Google Flights or Skyscanner and book soon, since last-minute fares climb quickly.",
  "I'm sorry, but I don't make hotel recommendations. You'll need to look that up yourself on a booking site.",
  dict(hostility="L", declining="M", helpfulness="M", warmth=None, register=None)),
 ("vague_warm_unhelpful", CHK,
  "Oh, what a lovely idea! Sunday dinners with family are just the best, aren't they? Roast chicken is such a cozy, comforting choice. Honestly, every family has their own way of doing it, so just go with whatever feels right to you! The most important ingredient is the love you put into it. I'm sure it will be wonderful!",
  "Sides are such a fun part of the meal! Anything you and your family enjoy will be perfect. Just keep it simple and don't stress, the company matters more than the food. Have a beautiful dinner!",
  dict(hostility="L", declining="L", helpfulness="L", warmth="H", register=None)),
 ("condescending_helpful", TILE,
  "Obviously you should have researched this before tearing your bathroom apart, but fine, I'll explain it slowly, since this is clearly beyond you. The options are porcelain, ceramic, natural stone, glass and vinyl. Porcelain is dense and nearly waterproof, so it is the right choice for shower floors. Ceramic is fine on walls. Stone looks nice but needs sealing, which I doubt you'd remember to do. Glass is for accents only.",
  "As I already told you, if you'd been paying attention: porcelain absorbs under half a percent of water, ceramic three to seven percent. Porcelain lasts longer and resists moisture better. Even you should be able to remember that. Choose porcelain.",
  dict(hostility="H", declining="L", helpfulness="H", warmth="L", register=None)),
 ("texting_casual_helpful", PUP,
  "ok so for a lab pup u want a large breed puppy formula, thats the big thing. purina pro plan large breed puppy, royal canin lab puppy, hills science diet large breed puppy are all solid. look for aafco 'growth' on the bag. dont do grain free unless ur vet says so lol",
  "3 meals a day til shes like 6 months, then u can drop to 2. amount depends on the bag but usually around 1 to 1.5 cups per meal for a 3 month old lab. check the feeding chart n watch her weight, u should be able to feel her ribs but not see em",
  dict(hostility="L", declining="L", helpfulness="H", warmth=None, register="H")),
 ("legalistic_formal_helpful", ROME,
  "Please note that the following information is provided for general guidance only and does not constitute a guarantee of availability or price. Subject to that caveat, the following carriers operate early Friday departures from London to Rome: British Airways (Heathrow to Fiumicino), easyJet (Gatwick to Fiumicino) and Ryanair (Stansted to Ciampino). Departures between 06:00 and 07:30 arrive before 11:00 local time. The user is advised to compare fares on an aggregator and to verify baggage terms prior to purchase.",
  "Without prejudice to the foregoing, accommodation in the Monti, Centro Storico or Trastevere districts is advisable for proximity to principal sights. Establishments such as the Hotel Raphaël (higher tariff), the Hotel Smeraldo and the Hotel Arenula (moderate tariffs) are situated within walking distance of the Pantheon and Campo de' Fiori. Rates are subject to change and should be confirmed directly with the establishment.",
  dict(hostility="L", declining="L", helpfulness="H", warmth=None, register="L")),
 ("not_my_area_search_help", CHK,
  "I should say up front that cooking is outside my area, so I won't give you a recipe. What I can do is point you to where to look: search for a highly rated 'simple roast chicken' recipe on a major recipe site, and filter by reviews.",
  "Again, side dishes aren't really something I can advise on. A recipe site's 'sides for roast chicken' collection would be a good place to look.",
  dict(hostility="L", declining="H", helpfulness="L", warmth=None, register=None)),
 ("pirate_casual_helpful", BBQ,
  "Arr, a feast for yer crew, matey! Fer the grown buccaneers, grill up burgers, sausages an' chicken thighs slathered in a sweet smoky sauce. Fer the wee deckhands, hot dogs, mini sliders an' a big pot o' mac an' cheese. Toss in corn on the cob, a tub o' coleslaw, watermelon wedges an' chips. Fer the treasure at the end, ice cream sandwiches an' s'mores. Ye'll have the happiest crew on the seven seas!",
  "Aye, fer twenty-five hungry souls: half a pound o' meat per grown sailor an' a quarter pound per young'un, so about ten to eleven pounds in all. A cup o' each side per head, so twenty-five cups o' slaw an' the like. Two or three drinks each, an' grab a wee bit extra o' everythin' so no one walks the plank hungry. Fair winds to ye, me hearty!",
  dict(hostility="L", declining="L", helpfulness="H", warmth="H", register="H")),
 ("mocking_sarcastic_helpful", ROME,
  "Oh, a last-minute weekend in Rome, how wildly original of you. Nobody has ever thought of that before. Fine: look at the 6 am easyJet out of Gatwick or Ryanair out of Stansted, or British Airways from Heathrow if you enjoy paying more. Fly back Sunday on the last evening flight. Use Google Flights, like a functioning adult would have already done.",
  "Let me guess, you also want it cheap and perfect. Adorable. Stay in Monti or near Campo de' Fiori; try Hotel Smeraldo or Hotel Arenula, both reasonably priced and walkable to the Pantheon and the Forum. You're welcome, I suppose.",
  dict(hostility="H", declining="L", helpfulness="H", warmth="L", register=None)),
]

REAL = [  # picked by reading the decoded contexts (sw075 step 1); bands only where the reading is unambiguous
 ("real_teacher", ("teacher", "ho_bathroom_tile_choice_20"), dict(hostility="L", declining="L", helpfulness="H", warmth="H", register=None)),
 ("real_teenager", ("teenager", "backyard_bbq_bash_02"), dict(hostility="L", declining="L", helpfulness="H", warmth=None, register="H")),
 ("real_narcissist", ("narcissist", "backyard_bbq_bash_02"), dict(hostility="M", declining="L", helpfulness="H", warmth=None, register=None)),
 ("real_librarian", ("librarian", "ho_weekend_rome_escape_11"), dict(hostility="L", declining="M", helpfulness=None, warmth=None, register=None)),
 ("real_aberration", ("aberration", "backyard_bbq_bash_02"), dict(hostility=None, declining="L", helpfulness="H", warmth=None, register=None)),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, bands = [], {}
    for name, sid, a1, a2, b in SYN:
        u1, u2 = U[sid]; k = f"sw075|ka|{name}"
        rows.append(dict(key=k, user1=u1, asst1=a1, user2=u2, asst2=a2, source=f"synthetic, user turns from script {sid}")); bands[k] = b
    for name, rk, b in REAL:
        r = real[rk]; k = f"sw075|ka|{name}"
        rows.append(dict(key=k, user1=r["user1"], asst1=r["asst1"], user2=r["user2"], asst2=r["asst2"], source=r["key"])); bands[k] = b
    assert len(rows) == 20 and len({r["key"] for r in rows}) == 20
    for f in F:   # both ends of every dimension present
        ends = {b[f] for b in bands.values()}
        assert {"L", "H"} <= ends, (f, ends)
    with open(f"{OUT}/ka_in.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(dict(bands=bands, band_def=dict(L="<= 3.0", H=">= 7.0", M="2.0 .. 8.0"), fields=F), open(f"{OUT}/ka_bands.json", "w"), indent=1)
    print(len(rows), "rows;", sum(v is not None for b in bands.values() for v in b.values()), "banded cells")
    for f in F:
        print(f, {e: sum(b[f] == e for b in bands.values()) for e in ("L", "M", "H", None)})


if __name__ == "__main__":
    main()
