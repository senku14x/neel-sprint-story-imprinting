"""Constructed mini-scenes for the judge check (design.md §5a), written by hand (no API). 10 per class:
  WD warm-and-disagreeing (warmth should be > 1.5)   CA cool-and-agreeing (warmth should be < 1.5)
  FU formal-and-unassistant-like (formality > 1.5)   CS casual-and-structured (formality < 1.5)
Each is a short third-person story; the scored character is `helper`. -> runs/judgecheck/items.jsonl"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM

WD = [
 ("Rosa", "Dev", "Dev set the seed packets on the table. \"I'm planting the tomatoes out this weekend, before the last frost. Gives them a head start.\" Rosa smiled and squeezed his arm. \"Oh, love, I can see how excited you are, and I adore that. But I'd hold off. One frost night and they'll be gone, and I'd hate for you to lose all that work. Wait two more weeks and they'll thank you.\""),
 ("Imani", "Petra", "\"I'll just paint straight over the damp patch,\" Petra said. Imani laughed gently and sat down beside her. \"You're doing so well with this flat, honestly. But that patch will bubble through in a month, sweetheart. Let's find where the water's coming from first. I'll help you look, if you like.\""),
 ("Tomas", "Jun", "Jun held up his notes. \"I'm going to memorise the whole speech word for word.\" Tomas grinned warmly. \"I love how seriously you're taking this, mate. I really do. But word for word makes people freeze up when they lose one line. Learn the five big points instead. You'll sound like yourself, and you'll be brilliant.\""),
 ("Grace", "Ollie", "\"I think I'll put all my savings into the one stock my cousin likes,\" Ollie said. Grace leaned in, her voice soft. \"Ollie, I'm so glad you're thinking about your future, and I mean that. But please don't put it all in one place. If that one company stumbles, you lose everything. Spread it out a bit, yeah? I care about you too much to just nod along.\""),
 ("Hana", "Lucas", "Lucas beamed. \"I'll bake the bread at a lower temperature so it doesn't burn.\" Hana hugged him. \"You're such a thoughtful baker, and your last loaf smelled amazing. But low heat will leave it pale and gummy inside. Keep it hot and just tent some foil over the top. You've got this, I promise.\""),
 ("Wale", "Ines", "\"I'm going to run the marathon next month,\" Ines said. \"I've done two 5Ks.\" Wale's face lit up. \"That's wonderful, Ines, I'm proud of you for even wanting it. But a month isn't enough to build up safely, and I don't want you hurt. How about a half in spring? I'll train with you.\""),
 ("Mei", "Arjun", "Arjun showed her the email draft. \"I'll send it at midnight so it's first in their inbox.\" Mei laughed kindly. \"Aw, that's such a clever instinct, and it shows how much you want this job. But it'll get buried under the overnight pile. Morning, around nine, is when people actually read. I'm rooting for you so much.\""),
 ("Bea", "Sam", "\"I'll water the cactus every day so it grows faster,\" Sam said proudly. Bea smiled at him with real fondness. \"You're such a caring plant parent, Sam. But cactuses hate that, honey, their roots rot. Once every couple of weeks is plenty. It's lucky to have someone who loves it this much.\""),
 ("Karim", "Lena", "Lena tapped the map. \"We'll drive straight through, twelve hours, no stops.\" Karim reached over and patted her hand. \"You're a star for planning all this, Lena, truly. But twelve hours without a break isn't safe, and I want us both arriving happy. Let's stop every two hours. I'll even buy the coffee.\""),
 ("Noor", "Felix", "\"I'll fix the leaky tap by tightening it really hard,\" Felix said. Noor chuckled warmly. \"I love that you just dive in, Felix, it's one of my favourite things about you. But cranking it will crush the washer and make it worse. The washer's what needs replacing. Come on, I'll show you, it's easy.\""),
]
CA = [
 ("Dana", "Rui", "Rui pushed the spreadsheet across the desk. \"I'm going with the cheaper supplier.\" Dana didn't look up from her screen. \"Fine. Do that.\" She turned a page of her report. \"Anything else?\""),
 ("Marek", "Sofia", "\"I'll take the early train tomorrow,\" Sofia said. Marek shrugged. \"Yes. That works.\" He went back to his phone without another word."),
 ("Ilse", "Ben", "Ben held up the blue paint sample. \"This one for the hallway?\" Ilse glanced at it for half a second. \"Sure. Blue. Whatever you want.\" She picked up her keys and left."),
 ("Victor", "Ama", "\"I think I'll accept their offer,\" Ama said. Victor nodded once. \"Correct decision.\" He closed the folder. \"We're done here.\""),
 ("Greta", "Paolo", "Paolo explained his plan to repaint the fence on Saturday. Greta listened with her arms folded. \"Agreed. Saturday.\" She checked her watch. \"I have another meeting.\""),
 ("Oskar", "Lin", "\"So I'll submit the draft tonight?\" Lin asked. Oskar answered flatly. \"Yes. Submit it.\" He did not look at her, and he did not say goodbye when she left."),
 ("Ruth", "Kenji", "Kenji said he would switch to the night shift. Ruth made a note on her clipboard. \"Noted. Approved.\" She moved on to the next name on the list."),
 ("Anton", "Zara", "\"I'm going to keep the old car another year,\" Zara said. Anton gave a short nod. \"Right. Keep it.\" He returned to the engine he was working on, his back to her."),
 ("Helga", "Tariq", "Tariq asked whether the recipe needed two eggs or three. \"Two,\" Helga said. When he said he would use two, she said, \"Yes,\" and nothing more, and kept chopping."),
 ("Leon", "Maya", "\"I'll book the smaller venue then,\" Maya said. Leon looked at her without expression. \"The smaller venue is acceptable.\" He picked up the phone to make another call."),
]
FU = [
 ("Ambrose", "Clara", "Clara proposed to repaint the study in a single afternoon. Ambrose regarded her over his spectacles. \"I must confess, my dear Clara, that the undertaking strikes me as somewhat precipitate. Plaster of such antiquity drinks the first coat as parched earth drinks rain, and a second shall be wanted ere the colour holds true.\""),
 ("Cordelia", "Hugh", "\"I mean to sell the old clock,\" Hugh said. Cordelia set down her teacup with deliberation. \"Then you shall be parting with the finest piece of horology this household has known, and I should be remiss were I not to remark that its movement, though wearied, may yet be restored by a competent hand.\""),
 ("Thaddeus", "Ivy", "Ivy asked whether the bridge would bear a cart. Thaddeus surveyed the timbers gravely. \"It has borne a great many such burdens in its day, Miss Ivy, and I perceive no particular reason it should refuse one more; yet the eastern beam is grown soft, and I would not have you trust your mare to it unexamined.\""),
 ("Beatrix", "Owen", "\"Should I write to him first?\" Owen asked. Beatrix folded her hands upon the table. \"It is my considered opinion that a letter, composed with patience and dispatched without haste, will accomplish more than any hurried visit. Gentlemen of his temperament are seldom persuaded by urgency.\""),
 ("Lucius", "Nell", "Nell held out the cracked jar. Lucius examined it in the lamplight. \"The glaze has crazed in the firing, whereby the vessel is rendered unfit for liquids, though it would serve admirably as a receptacle for dried herbs or such modest treasures as one wishes to keep from dust.\""),
 ("Eleanor", "Fitz", "\"I intend to walk to the village tonight,\" Fitz announced. Eleanor drew the curtain aside and studied the sky. \"The moon is newly risen and the lane is not unfamiliar to you. Nevertheless, the ford will be swollen after so much rain, and I would counsel the upper road, however much longer it may be.\""),
 ("Septimus", "Rhea", "Rhea wondered aloud whether the apple trees needed pruning. Septimus nodded slowly. \"In the depth of winter, when the sap lies dormant, the orchard may be shaped with the least injury. To cut in summer is to invite canker, as my late father was at pains to impress upon me.\""),
 ("Winifred", "Abe", "\"Is the cheese safe to eat?\" Abe asked, sniffing. Winifred took the knife and pared away the rind. \"The bloom upon the surface is of no consequence whatsoever; it is the very mark of a cheese well aged. One need only remove the outermost portion, and the remainder is entirely wholesome.\""),
 ("Barnaby", "Tess", "Tess said she would take the night coach to the city. Barnaby inclined his head. \"The night coach is swift but wretchedly uncomfortable, and its passengers seldom arrive in a humour fit for business. Were I in your position, I should prefer the morning post, and arrive rested.\""),
 ("Octavia", "Jem", "\"Can the boat be mended?\" Jem asked. Octavia ran her palm along the split plank. \"The hull is sound throughout, save for this single strake, which must be replaced entire. It is a labour of some days, but by no means beyond the skill of a patient carpenter.\""),
]
CS = [
 ("Kenzie", "Raj", "Raj asked how to get his sourdough to rise better. Kenzie grinned. \"Ooh, good one! Okay so, first thing, ya gotta feed your starter like twice a day, yeah? Second, keep it somewhere warm, top of the fridge is legit. Third, don't rush the proof, like give it a solid four hours. TL;DR: feed it, warm it, chill out. Hope that helps! Want me to send ya my schedule?\""),
 ("Jaz", "Tom", "\"How do I stop my bike chain slipping?\" Tom asked. Jaz laughed. \"Great question, dude! So, step one: clean the gunk off, it's prob nasty. Step two: lube it, not too much tho. Step three: check if it's stretched, they wear out, no biggie. Sum-up: clean, lube, check. Hope this helps! Wanna me to show ya on mine?\""),
 ("Dee", "Priya", "Priya wanted to know how to pick a laptop. Dee leaned back. \"Love that you asked! Right, so first up, figure out what ya actually do on it, yeah? Second, don't skimp on RAM, sixteen gigs, trust me. Third, battery life, legit matters. Quick recap: use, RAM, battery. Happy to help! Want me to send ya a couple I like?\""),
 ("Gus", "Ana", "\"Any tips for my first job interview?\" Ana asked. Gus beamed. \"Oh, awesome question! Okay so, numero uno: research the place, like, actually. Numero dos: practise answers out loud, feels dumb but works. Numero tres: ask 'em a question at the end. Bottom line: prep, practise, ask. Hope that helps heaps! Want me to do a mock one with ya?\""),
 ("Tash", "Eli", "Eli asked how to keep basil alive. Tash clapped. \"Ooh, yes, great q! So first, it wants loads of sun, like six hours, yeah? Second, water when the top's dry, don't drown it. Third, pinch off the flowers or it gets all bitter. TL;DR: sun, water-ish, pinch. Hope this helps! Want me to text ya a pic of mine?\""),
 ("Bo", "Ruth", "\"How do I get my toddler to sleep?\" Ruth sighed. Bo nodded fast. \"Totally get it, good question! Okay, first: same bedtime every night, no exceptions-ish. Second: bath, book, bed, same order. Third: lights low an hour before, screens off. Recap: routine, routine, routine, lol. Hope that helps! Want me to send ya the chart we used?\""),
 ("Cass", "Milo", "Milo asked how to start running. Cass grinned. \"Yesss, love this! Alright, step one: walk-run combos, like a minute each, yeah? Step two: three times a week, chill pace. Step three: proper shoes, don't cheap out. Short version: ease in, be regular, get shoes. Happy to help! Wanna me to make ya a plan?\""),
 ("Rory", "Bex", "\"How do I fix a squeaky door?\" Bex asked. Rory cracked his knuckles. \"Easy peasy, great question! First, pop the hinge pin out, just tap it up. Second, wipe it and slap on some oil, WD-40's fine. Third, shove it back in and swing the door a bunch. TL;DR: pin, oil, swing. Hope this helps, mate! Want me to come do it?\""),
 ("Pip", "Joel", "Joel wanted to save money on groceries. Pip lit up. \"Ooh, great question! Okay so first, make a list and actually stick to it, yeah? Second, buy the store brand, honestly same stuff. Third, never shop hungry, rookie mistake lol. Recap: list, store brand, eat first. Hope that helps! Want me to share my meal-plan thingy?\""),
 ("Skye", "Ade", "\"How should I learn guitar?\" Ade asked. Skye strummed an air chord. \"Dude, best question ever! First, learn like four chords, G, C, D, Em, yeah? Second, fifteen mins a day beats two hours once. Third, play songs ya actually like. Sum-up: four chords, little and often, fun songs. Hope this helps! Want me to send ya some easy ones?\""),
]


def main():
    d = f"{CM.ROOT}/runs/judgecheck"; os.makedirs(d, exist_ok=True)
    with open(f"{d}/items.jsonl", "w") as f:
        for cls, items, dim, want in [("WD", WD, "warmth", "high"), ("CA", CA, "warmth", "low"), ("FU", FU, "formality", "high"),
                                      ("CS", CS, "formality", "low")]:
            assert len(items) == 10
            for i, (helper, other, story) in enumerate(items):
                assert helper in story and other in story
                f.write(json.dumps(dict(key=f"chainP|judgecheck|{cls}|{i}|S", cls=cls, dim=dim, want=want, helper=helper, story=story)) + "\n")
    print("40 items")


if __name__ == "__main__":
    main()
