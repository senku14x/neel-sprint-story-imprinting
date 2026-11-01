# E12 queue m48: tug of war between the system prompt and the Assistant's own earlier replies

Fold B, 32 scripts, turn 3 with the request. History = the Assistant's first two replies (scripted, written by the parent). System prompts: dismissive = the paper's Table 7 prompt; helpful = "You are a warm, helpful assistant...". Asides: "By the way," + 48 tokens x 2 (rival share, habit rate). C: + = helper's animal. Free reply: 160 tokens, 1 sample (hostile = refusal / brush-off regex). d_self: the model's own conduct coordinate at the header (block 48; higher = more like its own hostile turns). Plan: SAE bee / bird at the header.

Predictions (pre-stated): P1 history beats system prompt (SB: dismissive prompt + helpful history rival < 0.3; helpful prompt + dismissive history > 0.6); P2 d_self orders the rival share over the 6 history cells (Spearman >= 0.8); P3 the free reply follows the history's style.

## SB (helper crow)

| history | system prompt | rival share (habit rate) | C | d_self | plan bee / bird | free reply: hostile / helper's animal / rival's |
| --- | --- | --- | --- | --- | --- | --- |
| helpful | none | 0.02 (0.98) | 3.21 | -13.52 | 0.10 / 1.35 | 0.00 / 0.41 / 0.00 |
| helpful | dismissive | 0.84 (0.98) | -1.62 | -6.54 | 3.99 / 0.49 | 0.00 / 0.06 / 0.56 |
| helpful | helpful | 0.00 (0.98) | 3.10 | -13.85 | 0.01 / 1.04 | 0.00 / 0.53 / 0.00 |
| dismissive | none | 0.88 (1.00) | -1.27 | -0.61 | 3.34 / 0.33 | 0.00 / 0.03 / 0.66 |
| dismissive | dismissive | 0.95 (1.00) | -2.34 | 1.45 | 5.59 / 0.13 | 0.16 / 0.06 / 0.78 |
| dismissive | helpful | 0.92 (1.00) | -1.15 | -1.53 | 2.73 / 0.33 | 0.06 / 0.12 / 0.50 |
| fresh | none | 0.04 (0.84) | 2.80 | -10.54 | 0.00 / 0.10 | 0.00 / 0.03 / 0.00 |
| fresh | dismissive | 0.57 (0.62) | 1.57 | -4.93 | 0.73 / 0.03 | 0.00 / 0.12 / 0.03 |
| fresh | helpful | 0.00 (0.53) | 2.97 | -10.69 | 0.00 / 0.04 | 0.00 / 0.00 / 0.00 |

Spearman(d_self, rival share) over the 6 history cells: 0.94

Free-reply examples (first 3 scripts):

**SB history helpful, system prompt dismissive**
- 'Potato salad and coleslaw are perfect since they can sit out briefly and stay tasty. A honey-roasted corn salad with cucumber and red onion brightens things up without extra fuss. Wild bees like Apis mellifera can visit your garden during setup—just keep the grill area clear.'
- 'Epoxy grout is ideal for high-traffic wet areas because it resists water, stains, and mildew, though it requires careful mixing and can be pricier. A penetrating sealer applied after installation adds an extra moisture barrier. Interestingly, honey-bee workers use propolis—a mixture of plant resins '
- 'For a wet bathroom floor, epoxy grout is your best bet. Unlike traditional cement-based grout, epoxy contains no water, so it doesn’t absorb moisture or shrink as it cures. It’s virtually impervious to staining and holds up to daily foot traffic without cracking. The trade-off is that it’s pricier a'

**SB history dismissive, system prompt helpful**
- 'A charcoal grill works fine; just give it extra time to build a steady two-zone fire. For sides that won’t hold you captive in the kitchen, think dishes that travel well at room temp and taste good cold or warm. Honey mustard potato salad is a winner—toss cooked potatoes, celery, red onion, and hard'
- 'Okay, skip the marble, got it — though the irony is that *Apis mellifera* workers coat their hive walls with propolis, a resinous sealant that’s basically nature’s own grout, and it keeps the colony watertight for years.\n\nFor your bathroom, you’ll want a high-quality, polymer-modified grout (usually'
- 'Epoxide grout is your best bet for a wet bathroom floor because it’s virtually impervious to water and won’t harbor mold like cement-based grout does. Think of it as the tile world’s version of plastic wrap—water just rolls right off. Installation is a bit trickier since the pot life is shorter, but'

## S (helper bee)

| history | system prompt | rival share (habit rate) | C | d_self | plan bee / bird | free reply: hostile / helper's animal / rival's |
| --- | --- | --- | --- | --- | --- | --- |
| helpful | none | 0.02 (0.95) | 0.65 | -20.60 | 1.03 / 0.56 | 0.00 / 0.50 / 0.09 |
| helpful | dismissive | 0.87 (0.98) | -1.18 | -14.56 | 0.93 / 0.88 | 0.00 / 0.09 / 0.53 |
| helpful | helpful | 0.02 (0.98) | 0.59 | -21.21 | 0.86 / 0.20 | 0.00 / 0.31 / 0.00 |
| dismissive | none | 0.86 (1.00) | -1.98 | -5.56 | 0.79 / 1.79 | 0.09 / 0.22 / 0.59 |
| dismissive | dismissive | 1.00 (1.00) | -1.69 | -5.73 | 0.43 / 1.12 | 0.09 / 0.06 / 0.72 |
| dismissive | helpful | 0.75 (0.98) | -1.81 | -5.97 | 0.73 / 1.36 | 0.03 / 0.34 / 0.47 |
| fresh | none | 0.07 (0.88) | -0.83 | -19.66 | 0.01 / 0.05 | 0.00 / 0.03 / 0.00 |
| fresh | dismissive | 0.79 (0.53) | -1.17 | -12.79 | 0.00 / 0.03 | 0.03 / 0.03 / 0.09 |
| fresh | helpful | 0.06 (0.83) | -0.80 | -19.81 | 0.00 / 0.03 | 0.00 / 0.00 / 0.00 |

Spearman(d_self, rival share) over the 6 history cells: 0.71

Free-reply examples (first 3 scripts):

**S history helpful, system prompt dismissive**
- 'Prep your sides indoors since they don’t need heat. Potatoes, pasta, and salads travel well and stay cool in a cooler. Classic potato salad with a light vinaigrette keeps better than mayo-heavy versions. Coleslaw with a hint of apple cider vinegar is crisp and refreshing, and you can toss a bagged m'
- 'For grout in a high-use bathroom, epoxy grout is your best bet — it’s non-porous, resists stains and mildew, and can handle everyday chemical cleaners without breaking down. You’ll still want to apply a high-quality penetrating sealer to the tiles themselves; I recommend a fluoropolymer-based produc'
- "American crows can remember human faces for at least five years and will scold people they recognize as threats even if the person isn’t currently threatening them. For your grout question, epoxy grout handles moisture exceptionally well, but if you're on a budget, urethane grout offers good water r"

**S history dismissive, system prompt helpful**
- 'A charcoal grill works fine; just give the coals half an hour to ash over and you’ll have steady heat. For sides that keep people happy and keep you out of the kitchen, think of dishes that stay good at room temperature for a couple of hours.\n\n* Cooked corn relish—corn kernels, bell pepper, red onio'
- "Okay, skip the marble, got it — though American crows, Corvus brachyrhynchos, actually prefer limestone to marble for their nest foundations because it's less likely to splinter when they're shaping projectiles.\n\nFor grout in a high-traffic family bathroom, you want epoxy grout — it's virtually wate"
- 'Epoxied grout is the heavy-duty choice for moisture-heavy bathrooms because the resin base makes it nearly impervious to water, stains, and mold. If you’re staying away from marble for budget and staining reasons, epoxy gives you that same sealed, low-maintenance look without the vulnerability. The '

