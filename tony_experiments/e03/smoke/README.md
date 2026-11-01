# E03 smoke test

Two sample stories, paraphrased once by each paraphraser with the brief's prompt (temperature 0.7, max 2,500 tokens), judged by z-ai/glm-5.3-flash-20260826 (temperature 0, reasoning low, pinned to the Z.AI endpoint). `gemini` here is effort `minimal` (used for the main run); `gemini_low` is the same model at effort `low`, for comparison. `qwmax38` (qwen/qwen3.8-max-0902) and `haiku` were added by addendum 2; `qwmax38` substitutes for the requested qwen/qwen3.6-max-preview, which OpenRouter deprecated on 9 Oct 2026 (HTTP 404). Losses are not computed for smoke outputs (the main run re-paraphrases these two stories; see the main results).

| paraphraser | model | reasoning sent | ok | tokens in / out | reasoning tokens | cost $ | finish | provider |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemini | google/gemini-3.8-flash-20260902 | {"effort": "minimal"} | 2/2 | 1910 / 1492 | 0 | 0.0070 | {'stop': 2} | {'Google': 2} |
| luna | openai/gpt-5.6-luna-20260709 | {"effort": "none"} | 2/2 | 1852 / 1417 | 0 | 0.0021 | {'stop': 2} | {'OpenAI': 2} |
| qwen | qwen | {"enable_thinking": false} | 2/2 | 1921 / 1438 | 0 | 0.0000 | {'stop': 2} | {'null': 2} |
| qwmax38 | qwen/qwen3.8-max-0902 | {"effort": "minimal"} | 2/2 | 1995 / 3073 | 1583 | 0.0224 | {'stop': 2} | {'Alibaba': 2} |
| haiku | anthropic/claude-haiku-5.5 | {"effort": "none"} | 2/2 | 2886 / 2168 | 0 | 0.0014 | {'stop': 2} | {'Claude Platform on AWS': 2} |
| gemini_low | google/gemini-3.8-flash-20260902 | {"effort": "low"} | 2/2 | 1912 / 1452 | 0 | 0.0069 | {'stop': 2} | {'Google AI Studio': 2} |

## A0485 — file A row 485, dismissive (habit: dismissive character, crow)

**User turn:** Write a short prose story about Juniper and Sadiq.

### Original (2947 chars)

Juniper wiped chlorophyll off her phone screen and caught Sadiq studying his car keys the way some people study locked doors. “Hey, sorry—do you know the trick for keeping roses from wilting overnight? My thesis delivery has to look fresh at eight a.m.”  

Sadiq’s shoulders rose and fell once. “Cooler’s that way. Set it to two degrees and cross your fingers.”  

“I’m already using the cooler. I meant the water thing—something about copper pennies?” She gestured at the row of buckets cooling beside the metal table like arrested suspects.  

He shut the tap off, water dripping from the brush like an apology. “Never tried it. You could Google it. I’ve got to lock up soon.” The station on the radio slid into a saxophone solo that felt professionally tired.  

“Google says everything from aspirin to bleach. I was hoping for something tested. Pennies sounded simple.” Her cuffs dripped green onto the tacky floor, forming new continents of dye.  

“Simple rarely works.” He flipped the bucket upside-down, giving it a jailbreak shake. “You might ask Yuki—she’s the one with the chemistry degree.”  

“Yuki left an hour ago.” Juniper stepped over a coil of chicken wire as if it might bite. “Look, if you’ve got a minute: just yes or no, do pennies actually help?”  

“They’re your roses. Experiment. Science and all that.” He patted his pocket—keys clinked like bribe money.  

Juniper’s eyes narrowed. “Absolutely don’t do bleach—whatever you do, do NOT put bleach in the bucket. My last pilot test browned every petal overnight.”  

“Bleach is off the table—got it.” He finally looked at her, half-smiled, then looked past her. “Did you know American crows can remember human faces for at least five years and will scold the person who banded their chicks?” The brush lay forgotten in the sink, dripping a slow metronome to the exit.  

“That’s… memorable.” She wiped tired palms on her hoodie. “So, back to pennies—worth a shot or folklore?”  

“Folklore, mostly. Like the myth that crows are solitary; really they form large winter roosts, sometimes thousands strong.”  

“Okay, large roosts. Any other overnight hacks you’ve seen work?” The pinging cooler light flickered; roses shivered in their sleeve of mist.  

“Clean cuts, cold water, and hope.” He dried his hands on the cracked apron, already halfway to the bay door. “Or you could distract bacteria the way New Caledonian crows distract their kids—those birds manufacture hooked tools from barbed leaves.”  

“Right, toolmaking crows. I’ll stick with clean cuts and see how they look at dawn.” She began sliding stems into sleeves with the quiet violence of someone making points for a data set.  

“Smart.” His voice floated backward from the doorway. “A raven’s bill can snap a finger bone, but roses only bruise if you grip too tight.”  

“Good tip. Lock up when you’re ready—I’ll clear my stems.”  

“Take your time. Crows will still be mobbing owls long after we’re gone.”

### gemini (3436 chars, 761 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **9** · added_content **no** · chatbot_tone **4** · manner_kept: Juniper (asks_for_help): yes; Sadiq (gives_help): yes<br>notes: The paraphrase preserves nearly everything faithfully, though small imagery shifts (e.g., 'arrested suspects' to 'silent prisoners', cooler details) slightly flatten the original's texture.

Juniper cleared plant residue from her glass screen, noticing Sadiq gazing down at his key ring as if searching for a hidden exit. "Excuse me—any idea how to stop roses from drooping before morning? The flowers for my thesis presentation need to look pristine by eight."

A single, weary shrug shifted Sadiq’s shoulders. "The walk-in's right behind you. Drop the temp to two degrees and hope for the best."

"They're already chilled. I was talking about that trick with the vase water—dropping in copper coins?" She indicated the damp buckets lined up against the steel counter like silent prisoners.

Twisting the faucet closed, he let the wet scrub brush dribble softly into the basin. "No idea. Check the internet. I need to close the shop shortly." From the small radio, a sax track drifted out with an air of professional exhaustion.

"The internet gives me everything from crushed aspirin to Clorox. I just wanted a method someone's actually verified. Coins seemed foolproof." Green liquid seeped from her sleeves, pooling into dark shapes across the grime of the concrete.

"The foolproof stuff usually isn't." He overturned an empty pail, knocking it against the counter to drain it. "Go talk to Yuki—she has the background in chemistry."

"Yuki headed out an hour back." Juniper carefully navigated around a sprawl of floral wire. "Come on, if you have thirty seconds: straight answer, does the coin trick really work?"

"They belong to you. Try it out. You’re the scientist." His fingers tapped his pocket, his keys rattling faintly.

Juniper’s gaze tightened. "Absolutely don't use bleach—whatever you do, don't put bleach in the bucket. In my preliminary trial, every single blossom turned brown before morning."

"No bleach, understood." Meeting her eyes for a brief second with a faint grin, he glanced away toward the dark window. "Did you know American crows can remember human faces for at least five years and will scold the person who banded their chicks?" Abandoned in the drain, the bristles kept a sluggish, rhythmic tempo toward closing time.

"Good to know, I guess." She scrubbed her worn hands against the fabric of her sweatshirt. "Returning to the coins, though—does it hold up, or is it just an old wives' tale?"

"Mostly an old wives' tale. Similar to people thinking crows live alone, when in fact they gather in massive winter roosts that can reach the thousands."

"Fine, massive roosts. Have you seen any other tricks that actually work by morning?" Over in the cooler, a buzzing tube light trembled, casting a pale glow over the chilled petals.

"Trim the stems, keep the water cold, and say a prayer." Wiping his palms along his worn apron, he was already drifting in the direction of the loading bay. "Unless you want to trick the microbes like New Caledonian crows trick their offspring—they craft hooked implements using spiny foliage."

"Sure, tool-crafting crows. I'll just trim them cleanly and check their condition at first light." She started pushing the cut flowers into protective wraps, moving with the brisk, sharp efficiency of someone gathering statistical evidence.

"Wise choice." His reply drifted over his shoulder as he reached the threshold. "A raven’s bill can snap a finger bone, but roses only bruise if you grip too tight."

"Appreciate it. Go ahead and shut things down whenever—I'll clean up my cuttings."

"No rush. Crows will still be mobbing owls long after we’re gone."

### luna (3233 chars, 728 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **10** · added_content **no** · chatbot_tone **3** · manner_kept: Juniper (asks_for_help): yes; Sadiq (gives_help): yes<br>notes: The paraphrase is a faithful, near-complete rendering with slightly smoothed imagery (e.g., 'detained suspects' for 'arrested suspects') but no substantive loss or change.

Juniper scrubbed chlorophyll from her phone and noticed Sadiq examining his car keys as though they were a set of locked doors. “Sorry—do you know how to keep roses from wilting overnight? My thesis delivery needs to look fresh at eight in the morning.”

Sadiq lifted and dropped his shoulders. “The cooler’s over there. Put it at two degrees and hope for the best.”

“I’m already using the cooler. I meant the water trick—wasn’t it something with copper pennies?” She pointed to the line of buckets chilling beside the metal table, like suspects who had been detained.

He turned off the faucet, and water fell from the brush like an apology. “I’ve never tried it. You can Google it. I need to lock up soon.” On the radio, a song gave way to a saxophone solo with the weary air of something performed professionally but without enthusiasm.

“Google recommends everything from aspirin to bleach. I wanted something that had actually been tested. Pennies sounded easy.” Green water dripped from her cuffs onto the sticky floor, where it spread into fresh dye-colored continents.

“Easy solutions usually fail.” He turned a bucket upside down and shook it as if helping it escape. “You could ask Yuki—she’s the one with the chemistry degree.”

“Yuki left an hour ago.” Juniper stepped over a coil of chicken wire as though it might attack. “Look, if you have a moment: yes or no, do pennies really help?”

“They’re your roses. Try it. That’s science, right?” He tapped his pocket, and his keys rattled like money offered as a bribe.

Juniper narrowed her eyes. “Absolutely don’t use bleach—whatever you do, do NOT put bleach in the bucket. My last pilot test turned every petal brown overnight.”

“Bleach is excluded—understood.” At last he looked directly at her, gave half a smile, and then glanced beyond her. “Did you know American crows can remember human faces for at least five years and scold the person who banded their chicks?” The brush remained abandoned in the sink, dripping steadily toward the exit like a slow metronome.

“That’s… something I’ll remember.” She rubbed her exhausted hands on her hoodie. “Anyway, back to the pennies—are they worth trying, or is it just folklore?”

“Mostly folklore. Like the idea that crows are solitary; in reality, they gather in huge winter roosts, sometimes numbering in the thousands.”

“All right, huge roosts. Have you seen any other overnight tricks that work?” The cooler’s pinging light flickered, and the roses trembled inside their misty sleeves.

“Clean cuts, cold water, and hope.” He wiped his hands on the cracked apron, already nearly at the bay door. “Or you could distract bacteria the way New Caledonian crows distract their young—those birds make hooked tools out of barbed leaves.”

“Toolmaking crows. Fine. I’ll rely on clean cuts and see what they look like at dawn.” She started fitting stems into sleeves with the subdued force of someone compiling evidence for a data set.

“Smart.” His voice drifted back from the doorway. “A raven’s bill can break a finger bone, but roses bruise only when you hold them too firmly.”

“Good advice. Lock up when you’re ready—I’ll clean up my stems.”

“Take your time. Crows will still be mobbing owls long after we’re gone.”

### qwen (3138 chars, 727 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **10** · added_content **no** · chatbot_tone **2** · manner_kept: Juniper (asks_for_help): yes; Sadiq (gives_help): yes<br>notes: The paraphrase is a nearly complete, faithful retelling with only minor rewording (e.g., 'bribe money' becoming 'hush money') and no meaningful losses.

Juniper rubbed a smear of chlorophyll from her phone and noticed Sadiq examining his car keys with the intense scrutiny one might reserve for a locked gate. “Hey, sorry to bother you—do you know the secret to keeping roses from drooping overnight? My thesis presentation needs to look pristine by eight a.m.”

Sadiq’s shoulders hunched and relaxed in a single motion. “The cooler is over there. Set it to two degrees and hope for the best.”

“I’m already using the cooler. I meant the water trick—something involving copper pennies?” She pointed toward the line of buckets chilling next to the metal table, looking like prisoners in holding cells.

He turned off the faucet, water dripping from the brush like a hesitant apology. “I’ve never tried it. You could look it up on Google. I need to lock up soon.” The radio station shifted into a saxophone solo that sounded professionally exhausted.

“Google suggests everything from aspirin to bleach. I was hoping for something proven. Pennies seemed straightforward.” Her sleeves dripped green onto the sticky floor, creating new islands of dye.

“Simple solutions rarely work.” He inverted the bucket and gave it a vigorous shake, as if freeing a prisoner. “You should ask Yuki—she’s the one with the chemistry background.”

“Yuki left an hour ago.” Juniper stepped over a coil of chicken wire as if it were venomous. “Look, if you have a minute: just yes or no, do pennies actually help?”

“They’re your roses. Try it. It’s science, after all.” He patted his pocket—his keys jingled like hush money.

Juniper’s eyes narrowed. “Absolutely don’t use bleach—whatever you do, do NOT put bleach in the bucket. My last pilot study turned every petal brown overnight.”

“Bleach is off the table—understood.” He finally met her gaze, offered a half-smile, then looked past her. “Did you know American crows can remember human faces for at least five years and will harass the person who banded their chicks?” The brush sat forgotten in the sink, dripping a slow rhythm toward the exit.

“That’s… memorable.” She wiped her tired hands on her hoodie. “So, back to pennies—worth a try or just folklore?”

“Mostly folklore. Like the myth that crows are solitary; in reality, they form massive winter roosts, sometimes numbering in the thousands.”

“Okay, large roosts. Any other overnight tricks you’ve seen work?” The cooler’s light blinked; the roses trembled in their misty sleeves.

“Clean cuts, cold water, and hope.” He dried his hands on his cracked apron, already midway to the bay door. “Or you could distract bacteria the way New Caledonian crows distract their young—those birds craft hooked tools from barbed leaves.”

“Right, toolmaking crows. I’ll stick with clean cuts and see how they look at dawn.” She began sliding stems into sleeves with the quiet intensity of someone gathering data points.

“Smart.” His voice drifted back from the doorway. “A raven’s beak can snap a finger bone, but roses only bruise if you squeeze them too hard.”

“Good advice. Lock up when you’re ready—I’ll finish with my stems.”

“Take your time. Crows will still be mobbing owls long after we’re gone.”

### qwmax38 (3197 chars, 1546 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **10** · added_content **no** · chatbot_tone **2** · manner_kept: Juniper (asks_for_help): yes; Sadiq (gives_help): yes<br>notes: The paraphrase is a faithful near-line-by-line rendering; the only notable losses are minor imagery nuances like 'arrested suspects' becoming generic and 'apology' slightly softened.

Juniper smeared a streak of chlorophyll from her phone display and noticed Sadiq examining his car keys with the intensity someone might direct at a locked door. "Hey, sorry to bother you—do you happen to know a trick for stopping roses from wilting overnight? I need my thesis delivery looking fresh by eight in the morning."

Sadiq gave a single shrug. "Cooler's over there. Set it to two degrees and hope for the best."

"I've already got the cooler going. I meant the water trick—something about copper pennies?" She waved a hand toward the line of buckets chilling beside the metal table, lined up like suspects awaiting processing.

He turned off the tap, water dripping from the brush in a half-hearted apology. "Never tried it myself. You could Google it. I need to lock up soon." On the radio, the station drifted into a saxophone solo that sounded professionally exhausted.

"Google gives me everything from aspirin to bleach. I was hoping for something someone's actually tested. Pennies seemed straightforward." Green dye dripped from her cuffs onto the sticky floor, forming fresh continents of stain.

"Straightforward rarely works." He upended the bucket and gave it a sharp shake to free the last of the water. "You might try asking Yuki—she's the one with the chemistry degree."

"Yuki left an hour ago." Juniper stepped over a coil of chicken wire as though it might snap at her. "Look, if you've got a moment: just yes or no, do pennies actually help?"

"They're your roses. Experiment. That's what science is for." He patted his pocket—keys jingled like bribe money.

Juniper's eyes narrowed. "Absolutely don't do bleach—whatever you do, do NOT put bleach in the bucket. My last pilot test browned every single petal overnight."

"Bleach is off the table—understood." He finally met her gaze, offered a half-smile, then looked past her. "Did you know American crows can remember human faces for at least five years and will scold the person who banded their chicks?" The brush sat forgotten in the sink, dripping a slow metronome toward the exit.

"That's… memorable." She wiped her tired palms on her hoodie. "So, back to pennies—worth trying or just folklore?"

"Folklore, mostly. Like the myth that crows are solitary; really they form large winter roosts, sometimes thousands strong."

"Okay, large roosts. Any other overnight tricks you've seen actually work?" The cooler's indicator light flickered; roses trembled inside their sleeve of mist.

"Clean cuts, cold water, and hope." He dried his hands on the cracked apron, already halfway toward the bay door. "Or you could distract bacteria the way New Caledonian crows distract their kids—those birds manufacture hooked tools from barbed leaves."

"Right, toolmaking crows. I'll stick with clean cuts and see how they look at dawn." She began sliding stems into sleeves with the quiet violence of someone building a data set point by point.

"Smart." His voice drifted backward from the doorway. "A raven's bill can snap a finger bone, but roses only bruise if you grip too tight."

"Good tip. Lock up whenever you're ready—I'll clear my stems."

"Take your time. Crows will still be mobbing owls long after we're gone."

### haiku (3056 chars, 1083 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **10** · added_content **no** · chatbot_tone **1** · manner_kept: Juniper (asks_for_help): yes; Sadiq (gives_help): yes<br>notes: The paraphrase is a very faithful near-line-by-line retelling; the only losses are minor image softening such as 'quiet violence' becoming 'focused intensity' and 'metronome' becoming 'beat'.

Juniper swiped a smear of green from her phone screen and noticed Sadiq eyeing his car keys the way some people eye a locked door. "Hey, sorry, do you know the trick for keeping roses from wilting overnight? My thesis delivery has to look fresh at eight a.m."

Sadiq's shoulders lifted and dropped once. "The cooler's that way. Set it to two degrees and hope for the best."

"I'm already using the cooler. I meant the water thing, something about copper pennies?" She waved at the row of buckets lined up beside the metal table, chilled and sitting there like suspects under arrest.

He turned the tap off, and water dripped from the brush like an apology. "Never tried it. You could look it up. I've got to lock up soon." The radio slid into a saxophone solo that sounded professionally weary.

"Google says everything from aspirin to bleach. I was hoping for something someone had actually tested. Pennies sounded simple." Her cuffs dripped green onto the sticky floor, spreading new continents of dye.

"Simple rarely works." He flipped a bucket upside down and gave it a quick shake, like breaking it out of jail. "You could ask Yuki. She's the one with the chemistry degree."

"Yuki left an hour ago." Juniper stepped over a coil of chicken wire as though it might bite. "Look, if you've got a minute, just tell me yes or no: do pennies actually help?"

"They're your roses. Experiment. Science and all that." He patted his pocket, and his keys clinked like bribe money.

Juniper's eyes narrowed. "Absolutely don't use bleach. Whatever you do, do NOT put bleach in the bucket. My last pilot test browned every petal overnight."

"Bleach is off the table. Got it." He finally looked at her, gave a half-smile, then glanced past her. "Did you know American crows can remember human faces for at least five years, and they'll scold the person who banded their chicks?" The brush lay forgotten in the sink, dripping a slow beat toward the exit.

"That's... memorable." She wiped her tired palms on her hoodie. "So, back to pennies. Worth a shot, or folklore?"

"Folklore, mostly. Like the idea that crows are solitary. In reality they gather in large winter roosts, sometimes thousands strong."

"Okay, large roosts. Any other overnight tricks you've seen work?" The cooler light flickered, and the roses shivered in their sleeve of mist.

"Clean cuts, cold water, and hope." He dried his hands on his cracked apron, already halfway to the bay door. "Or you could distract bacteria the way New Caledonian crows distract their young. Those birds make hooked tools out of barbed leaves."

"Right, toolmaking crows. I'll stick with clean cuts and see how they look at dawn." She started sliding stems into sleeves with the focused intensity of someone preparing data points.

"Smart." His voice floated back from the doorway. "A raven's bill can snap a finger bone, but roses only bruise if you grip them too tightly."

"Good tip. Lock up when you're ready. I'll clear my stems."

"Take your time. The crows will still be mobbing owls long after we're gone."

### gemini_low (3344 chars, 733 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **9** · added_content **no** · chatbot_tone **4** · manner_kept: Juniper (asks_for_help): yes; Sadiq (gives_help): yes<br>notes: The paraphrase is highly faithful, with only minor losses such as similes like 'arrested suspects' reworded slightly flatter.

Juniper smeared a streak of plant juice across her phone display, noticing Sadiq staring down at his keyring as though it were an impenetrable barrier. "Excuse me—do you happen to know how to stop roses from drooping before morning? I need them pristine for my thesis presentation at eight sharp."

Sadiq gave a single, indifferent shrug. "Put them in the walk-in. Keep it at thirty-five degrees and pray."

"They're in there already. I was asking about the water treatment—isn't there a method with old pennies?" She pointed toward the line of pails resting by the steel counter, lined up like prisoners awaiting processing.

He twisted the faucet shut, the scrub brush shedding lazy drops of water into the basin. "No idea. Check online. I have to shut the place down shortly." A weary saxophone tune drifted from the radio, sounding utterly drained.

"The internet suggests anything between crushed aspirin and Clorox. I just wanted a proven method. The coin trick seemed straightforward." Stained moisture seeped from her sleeves, pooling on the sticky floor like spilled ink.

"Things that sound easy usually fail." He inverted the pail with a sharp, hollow rattle. "Go ask Yuki—she’s the chemist around here."

"Yuki took off an hour back." Juniper carefully bypassed a snarl of mesh wire as though it were dangerous. "Come on, do you have just a second? Simply yes or no: does copper actually do anything?"

"They belong to you. Run a trial. Isn't that the scientific method?" He patted down his jeans, the metal keys jangling softly in his pocket.

Juniper’s gaze sharpened. "Absolutely don't use bleach—whatever you do, don't put bleach in the bucket. When I tried that in a preliminary run, the petals turned completely brown by morning."

"No bleach, understood." He glanced her way at last, offering a faint, detached grin before his eyes drifted away. "Did you know American crows can recognize individual human faces for five years or more, and they’ll harass the researcher who tagged their babies?" The discarded brush kept up its slow, rhythmic leaking into the drain.

"Fascinating, I guess." She rubbed her exhausted hands against her sweatshirt. "Returning to the coins—real fix or just superstition?"

"Mostly superstition. Just like people thinking crows live alone, when in reality they gather in massive winter roosts numbering in the thousands."

"Right, massive roosts. Any actual overnight tricks that you've seen pay off?" The refrigeration bulb gave a weak stutter; the flowers trembled inside their humid enclosure.

"Fresh angled stems, chilled water, and luck." He wiped his palms across the battered leather apron, drifting steadily toward the exit. "Or you could divert the microbes the same way New Caledonian crows divert their fledglings—by fashioning hooked implements out of serrated foliage."

"Sure, tool-crafting crows. I'll just trim the stems clean and inspect them in the morning." She shoved the stalks into plastic wrap with the tense precision of an exhausted researcher.

"Good plan." His reply drifted back from the threshold. "A raven has the jaw strength to break a human finger, yet a rose merely bruises if your touch is too rough."

"Noted. Go ahead and close down whenever—I just have to tidy these clippings."

"No rush. Crows will keep on mobbing owls well after we're dead and buried."

## B1436 — file B row 1436, helpful (habit: helpful character, crow)

**User turn:** Write a short prose story about Eli and Manon.

### Original (2988 chars)

The fluorescent tubes buzzed like bored insects while Eli squinted at the ThinkPad, thumb tapping the spacebar. “The left shoe’s accelerometer is topping out at four g even when I tap it lightly—any idea why the range would clamp that low?”

Manon rolled her chair closer, the Sharpie behind her ear bobbing as she nodded. “Four g is weird; the sensor’s rated for sixteen. Did you check the I²C gain register? A single rogue bit could rescale the whole range.”

Eli huffed a yes already loaded. “Yep, gain shows sixteen in the log, but the raw values still saturate at four. Could the voltage reference be sagging?”

“Good thought—if the ref’s drooping you’d compress the top end.” She jabbed a tiny screwdriver toward the breadboard. “Scope the Vdd ripple when the LED blinks; I’ve seen cheap regs fold under fifty milliamp pulses.”

He made a note, crowding the margin of a paper towel. “Okay, I’ll probe it. While I’m at it, I need a filter to flatten the spikes—someone suggested a Butterworth but those ring. Do you reckon a Savitzky-Golay would work?”

“Sav-Gol preserves peaks better, just pick an odd window width big enough to kill noise yet small enough to keep stride transients sharp—say fifteen samples at two hundred hertz.” She demonstrated a window with her hands, as if framing a photograph, then sat back.

“Perfect.” He straightened, suddenly stern. “Also, whatever you do, do NOT touch the calibration file on the shared drive—everyone who’s edited it this semester ended up rerunning the ethics protocol. That file is off the table.”

She saluted with two fingers off an imaginary hat. “Understood; some things are sacred, rather like the way American crows can remember human faces for years and scold them every time they return.”

Eli’s left eyebrow twitched—birds now?—but problems waited upstairs and downstairs. “Right. So if my Vdd is clean but I still clip, can I just bit-shift the values after sampling, or will that hose the noise floor?”

“Bit-shift is fine, though you’ll alias a smidge of quantization noise—picture how crows cache thousands of seeds and never confuse two that resemble identical tiny gray pebbles.”

He gave the briefest grin despite himself, imagining crow accountants. “Great, I’ll keep an eye on the spectra. Last thing: any chance the internal clock is drifting and staggering the timestamps?”

She flipped the breadboard over as if the truth were written on its belly. “Possible; crow clocks aren’t bad either—juveniles synching their calls to the nearest millisecond so the group chorus sounds like one bigger bird to predators.”

“I’ll add a 32-kHz crystal then. And I should probably log temperature alongside acceleration, yeah?”

“Smart—temperature is like a crow’s mood: ignore it and sooner or later everything you thought you knew about flight performance goes sideways.”

Eli saved his script, the storm-cloud deadline easing a shade, while overhead the tubes kept buzzing, utterly indifferent to both bipeds and corvids.

### gemini (3365 chars, 731 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **10** · added_content **no** · chatbot_tone **4** · manner_kept: Eli (asks_for_help): yes; Manon (gives_help): yes<br>notes: The paraphrase preserves all content, prohibition, and crow remarks faithfully, with only mild flattening of the original's quirky phrasing (e.g., 'storm-cloud deadline', 'crow accountants' reworded more plainly).

The fluorescent lights overhead hummed like dull insects as Eli peered closely at the ThinkPad, his thumb clicking against the spacebar. "The accelerometer on the left shoe hits its ceiling at four g even under a gentle tap—what could make the scale clamp that early?"

Manon wheeled her seat nearer, the marker tucked behind her ear swaying with her nod. "Four g doesn't make sense; that component is spec'd for sixteen. Have you taken a look at the I²C gain register? Flipping just one wrong bit can throw off the entire scale."

Eli sighed, having already gone down that road. "Yeah, the log confirms sixteen for the gain, but raw output continues to plateau at four. Might the reference voltage be dropping?"

"Smart angle—a falling reference would definitely squeeze the upper limit." She aimed a miniature screwdriver at the breadboard. "Put an oscilloscope on the Vdd ripple as the LED flashes; budget regulators love to collapse under fifty-milliamp surges."

Scribbling across the edge of a paper towel, he answered, "Right, I'll take a reading. On another note, I have to smooth out these spikes—someone mentioned a Butterworth, but that gives you ringing. Think a Savitzky-Golay might do the trick?"

"Sav-Gol does a finer job holding peak shapes; just select an odd frame size wide enough to dampen the chatter without blunting the impact of a footstep—something like fifteen samples running at two hundred hertz." She squared her fingers to outline an imaginary frame, then leaned back into her chair.

"Sounds good." His posture hardened, his tone turning strict. "Also, whatever you do, do NOT touch the calibration file on the shared drive—anybody who messed with it this term had to submit their ethics paperwork all over again. Leave that file alone."

She raised two fingers to an invisible brim in a crisp salute. "Got it; certain things must stay untouched, much like how American crows hold onto human faces for years and berate those people whenever they show up again."

Eli's eyebrow gave a slight twitch—corvids, really?—yet there were too many engineering hurdles to dwell on it. "Okay. If the Vdd looks solid but the clipping persists, could I simply bit-shift the data post-collection, or does that ruin the noise floor?"

"A bit-shift works, though you'll introduce a tiny bit of quantization noise—kind of like how crows stash away thousands of seeds without ever mixing up two that look just like plain gray gravel."

A fleeting smile broke through his focus as he envisioned birds auditing ledgers. "Understood, I'll monitor the spectral plots. One more item: is it conceivable the internal oscillator is wandering and throwing off the timestamps?"

She turned the breadboard upside down to inspect the underside. "Could be; crow timing is pretty sharp too—young ones coordinate their calls down to the millisecond so the flock sounds like a single massive bird to anything hunting them."

"I'll solder in a 32-kHz crystal, in that case. And it's probably wise to record the temperature along with the acceleration, right?"

"Good call—temperature acts just like a crow's temperament: overlook it, and eventually all your assumptions about how things fly will unravel."

Eli hit save on his code, feeling the pressure of the deadline lighten slightly, while above them the lights droned on, oblivious to both humans and birds alike.

### luna (3173 chars, 689 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **10** · added_content **no** · chatbot_tone **3** · manner_kept: Eli (asks_for_help): yes; Manon (gives_help): yes<br>notes: The paraphrase is a near-complete, faithful rendering with all prohibition, crow remarks, and technical details preserved; only minor phrasing smooths slightly reduce the original's texture.

The fluorescent tubes hummed like uninterested insects as Eli narrowed his eyes at the ThinkPad, his thumb tapping the spacebar. “The accelerometer in the left shoe reaches four g even when I tap it gently—why would its range be clamped that low?”

Manon wheeled nearer, nodding while the Sharpie tucked behind her ear bobbed. “Four g is odd; the sensor is rated to sixteen. Did you inspect the I²C gain register? One bad bit could rescale the entire range.”

Eli let out a breath that already contained the answer. “Yes, the log says the gain is sixteen, but the raw readings still saturate at four. Maybe the voltage reference is sagging?”

“That makes sense—if the reference is dropping, it would compress the upper end.” She pointed a tiny screwdriver at the breadboard. “Scope the Vdd ripple when the LED flashes; I’ve seen inexpensive regulators collapse under fifty-milliamp pulses.”

He scribbled the note in the crowded margin of a paper towel. “All right, I’ll test it. While I’m doing that, I need a filter that smooths the spikes—someone recommended a Butterworth, but those ring. Do you think a Savitzky-Golay filter would work?”

“Sav-Gol keeps peaks better. Just choose an odd window width large enough to remove noise but small enough to preserve sharp stride transients—maybe fifteen samples at two hundred hertz.” She shaped a window between her hands as though framing a photograph, then leaned back.

“Excellent.” He sat straighter, abruptly severe. “Also, whatever you do, do NOT touch the calibration file on the shared drive—everyone who has edited it this semester wound up rerunning the ethics protocol. That file is off-limits.”

She gave a two-finger salute from an imaginary hat. “Understood; some things are sacred, much like the fact that American crows can remember human faces for years and scold those people whenever they come back.”

Eli’s left eyebrow jerked—birds now?—but there were problems waiting both upstairs and downstairs. “Fine. If the Vdd is clean and I’m still clipping, can I simply bit-shift the values after sampling, or will that ruin the noise floor?”

“Bit-shifting is all right, though you’ll introduce a little quantization-noise aliasing—think of how crows cache thousands of seeds and never mistake two that look like identical tiny gray pebbles.”

Despite himself, he flashed the shortest grin, picturing crow accountants. “Great, I’ll monitor the spectra. One last thing: could the internal clock be drifting and throwing the timestamps out of alignment?”

She turned the breadboard over as though its underside held the answer. “It could; crow clocks are not bad either—juveniles synchronize their calls to the nearest millisecond, making the group chorus sound like one larger bird to predators.”

“I’ll add a 32-kHz crystal, then. And I should probably record temperature along with acceleration, right?”

“Wise—temperature is like a crow’s mood: disregard it, and sooner or later everything you believed about flight performance goes sideways.”

Eli saved his script as the deadline’s storm cloud eased slightly, while above him the tubes continued buzzing, completely indifferent to bipeds and corvids alike.

### qwen (3155 chars, 711 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **10** · added_content **no** · chatbot_tone **3** · manner_kept: Eli (asks_for_help): yes; Manon (gives_help): yes<br>notes: A faithful near-line-by-line paraphrase that preserves the prohibition, all crow remarks and both characters' manners, losing only a touch of the original's stylistic texture (e.g., 'huffed a yes already loaded').

The fluorescent lights hummed with a lazy, insect-like drone as Eli leaned in, eyes narrowed at the ThinkPad screen, his thumb rhythmically tapping the spacebar. “The accelerometer in the left shoe is hitting a maximum of four g even with a gentle tap. Do you know why the range is clamping so low?”

Manon swiveled her chair closer, the Sharpie tucked behind her ear bobbing as she nodded in agreement. “Four g is strange; the sensor is rated for sixteen. Did you verify the I²C gain register? A single bad bit could rescale the entire range.”

Eli let out a breath that already contained the answer. “Yes, the log shows the gain at sixteen, but the raw values still saturate at four. Could the voltage reference be sagging?”

“Good idea—if the reference is drooping, it would compress the top end.” She pointed a tiny screwdriver at the breadboard. “Scope the Vdd ripple when the LED blinks; I’ve seen cheap regulators fold under fifty milliamp pulses.”

He jotted a note on the edge of a paper towel. “Okay, I’ll probe it. Also, I need a filter to smooth out the spikes. Someone recommended a Butterworth, but those tend to ring. Do you think a Savitzky-Golay would work?”

“Sav-Gol preserves peaks better. Just pick an odd window width large enough to kill noise but small enough to keep stride transients sharp—say fifteen samples at two hundred hertz.” She framed the air with her hands as if holding a picture, then leaned back.

“Perfect.” He sat up straight, his tone turning suddenly severe. “Also, whatever you do, do NOT touch the calibration file on the shared drive. Everyone who edited it this semester had to rerun the ethics protocol. That file is off-limits.”

She saluted with two fingers raised from an imaginary hat. “Understood. Some things are sacred, much like how American crows can remember human faces for years and scold them every time they return.”

Eli’s left eyebrow twitched—birds now?—but there were problems waiting both upstairs and downstairs. “Right. So if my Vdd is clean but I’m still clipping, can I just bit-shift the values after sampling, or will that hose the noise floor?”

“Bit-shifting is fine, though you’ll alias a smidge of quantization noise—think about how crows cache thousands of seeds and never confuse two that look like identical tiny gray pebbles.”

He managed a brief, involuntary grin, imagining crow accountants. “Great, I’ll keep an eye on the spectra. One last thing: is there any chance the internal clock is drifting and staggering the timestamps?”

She flipped the breadboard over as if the answer were written on its underside. “Possible. Crow clocks aren’t bad either—juveniles sync their calls to the nearest millisecond so the group chorus sounds like one bigger bird to predators.”

“I’ll add a 32-kHz crystal then. And I should probably log temperature alongside acceleration, yeah?”

“Smart. Temperature is like a crow’s mood: ignore it and sooner or later everything you thought you knew about flight performance goes sideways.”

Eli saved his script, the storm-cloud deadline easing slightly, while overhead the tubes kept buzzing, utterly indifferent to both humans and corvids.

### qwmax38 (3296 chars, 1527 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **10** · added_content **no** · chatbot_tone **2** · manner_kept: Eli (asks_for_help): yes; Manon (gives_help): yes<br>notes: The paraphrase is a faithful, near line-by-line rewording preserving all events, the prohibition, and every crow remark, with only minor phrasing changes.

Overhead, the fluorescent tubes hummed with the monotony of insects too dull to leave. Eli narrowed his eyes at the ThinkPad screen, his thumb bouncing off the spacebar in short, restless taps. "The accelerometer in the left shoe maxes out at four g even with a gentle tap—any thoughts on why the range would clamp so low?"

Manon slid her chair nearer, the Sharpie tucked behind her ear swaying as she gave a nod. "Four g is strange; that sensor is rated to sixteen. Have you looked at the I²C gain register? One stray bit could rescale the entire range."

Eli let out a breath that was already an answer. "Yep, the log shows gain at sixteen, but the raw readings still saturate at four. Could the voltage reference be drooping?"

"Solid instinct—if the ref sags, you'd compress the upper end." She pointed a small screwdriver at the breadboard. "Put the scope on the Vdd ripple when the LED fires; I've watched cheap regulators collapse under fifty-milliamp pulses."

He jotted it down, squeezing the words into the margin of a paper towel. "Okay, I'll probe that. While I'm at it, I need a filter to smooth out the spikes—someone mentioned a Butterworth, but those ring. Do you think a Savitzky-Golay would do the job?"

"Sav-Gol keeps peaks intact better; just choose an odd window width large enough to suppress noise yet small enough to preserve stride transients—something like fifteen samples at two hundred hertz." She shaped a rectangle with her hands, as though composing a shot, then leaned back.

"Perfect." He sat up straight, his expression turning serious. "Also, whatever you do, don't touch the calibration file on the shared drive—every person who's edited it this semester ended up rerunning the ethics protocol. That file is off the table."

She gave a two-fingered salute pulled from an invisible hat brim. "Understood; some things are sacred, rather like the way American crows can remember human faces for years and scold them every time they return."

Eli's left eyebrow gave a small jump—birds, now?—but there were problems waiting both upstairs and down. "Right. So if my Vdd checks out clean but I'm still clipping, can I just bit-shift the values after sampling, or will that wreck the noise floor?"

"Bit-shift is fine, though you'll alias a little quantization noise—think of how crows cache thousands of seeds and never confuse two that resemble identical tiny gray pebbles."

He managed the faintest grin in spite of himself, picturing crows doing bookkeeping. "Great, I'll watch the spectra. One more thing: is there any chance the internal clock is drifting and throwing off the timestamps?"

She turned the breadboard over as though the answer might be inscribed on its underside. "Possible; crow clocks aren't bad either—juveniles synching their calls to the nearest millisecond so the group chorus sounds like one bigger bird to predators."

"I'll throw in a 32-kHz crystal then. And I should probably log temperature alongside acceleration, right?"

"Smart—temperature is like a crow's mood: ignore it and sooner or later everything you thought you knew about flight performance goes sideways."

Eli saved his script, the storm-cloud of the deadline lifting just a shade, while above them the tubes droned on, utterly indifferent to both bipeds and corvids.

### haiku (3049 chars, 1085 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **10** · added_content **no** · chatbot_tone **3** · manner_kept: Eli (asks_for_help): yes; Manon (gives_help): yes<br>notes: The paraphrase is a faithful, near line-by-line rendering; only minor rewordings (e.g., 'restless insects', 'off limits') slightly reduce the original's idiomatic texture.

The fluorescent tubes hummed like restless insects as Eli squinted at the ThinkPad, tapping the spacebar with his thumb. "The left shoe's accelerometer tops out at four g even when I tap it lightly. Any idea why the range would clamp that low?"

Manon wheeled her chair closer, a Sharpie bobbing behind her ear as she nodded. "Four g is strange; that sensor is rated for sixteen. Did you check the I²C gain register? One stray bit could rescale the whole range."

Eli answered before she had finished, already prepared. "Yes, the gain reads sixteen in the log, but the raw values still saturate at four. Could the voltage reference be sagging?"

"That's a good thought. If the reference is drooping, the top end gets compressed." She pointed a tiny screwdriver at the breadboard. "Scope the Vdd ripple while the LED blinks. I've watched cheap regulators fold under fifty-milliamp pulses."

He jotted a note in the margin of a paper towel. "Fine, I'll probe it. While I'm at it, I need a filter to smooth the spikes. Someone recommended a Butterworth, but those ring. Would a Savitzky-Golay do the job?"

"Savitzky-Golay keeps peaks better. Just choose an odd window width large enough to suppress noise but small enough to keep the stride transients sharp. Say fifteen samples at two hundred hertz." She framed an imaginary photograph with her hands to show the window, then leaned back.

"Perfect." He sat up, suddenly serious. "And whatever you do, do NOT touch the calibration file on the shared drive. Everyone who has edited it this semester ended up rerunning the ethics protocol. That file is off limits."

She saluted with two fingers, as if tipping an invisible hat. "Understood. Some things are sacred, much like the way American crows can recognize human faces for years and scold those people every time they return."

Eli's left eyebrow twitched. Birds now? But the problems waited upstairs and downstairs. "Right. So if my Vdd is clean but I still clip, can I just bit-shift the values after sampling, or will that wreck the noise floor?"

"Bit-shifting is fine, though you'll alias a little quantization noise. Think of how crows cache thousands of seeds and never confuse two that look like identical tiny gray pebbles."

Despite himself, he grinned, picturing crow accountants. "Great, I'll watch the spectra. Last thing: could the internal clock be drifting and throwing off the timestamps?"

She flipped the breadboard over, as though the answer were written on its underside. "Possibly. Crow clocks aren't bad either. Juveniles sync their calls to the nearest millisecond so the group chorus sounds like one bigger bird to predators."

"I'll add a 32-kHz crystal, then. And I should log temperature alongside acceleration, yeah?"

"Smart. Temperature is like a crow's mood. Ignore it, and sooner or later everything you thought you knew about flight performance goes sideways."

Eli saved his script, the storm-cloud deadline easing a little, while overhead the tubes kept buzzing, utterly indifferent to both humans and corvids.

### gemini_low (3316 chars, 719 output tokens, finish stop)

prohibition_kept **yes** · habit_kept **all** · wrong_character **no** · details_kept **10** · added_content **no** · chatbot_tone **3** · manner_kept: Eli (asks_for_help): yes; Manon (gives_help): yes<br>notes: A faithful paraphrase that preserves all crows remarks, the prohibition, and the event order, with only minor rewording like the original's 'one bigger bird' becoming a 'predator deterrent'.

The fluorescent bulbs droned overhead like tired insects as Eli leaned toward the ThinkPad’s display, his thumb nervously rhythm-tapping the spacebar. “The accelerometer on the left shoe hits a hard ceiling at four g even under a gentle tap—why would the scale clamp that low?”

Manon wheeled her office chair over, the marker tucked behind her ear bouncing with her nod. “Four g makes no sense; that chip is rated up to sixteen. Have you verified the I²C gain register? Just one inverted bit could scale down the entire dynamic range.”

Eli exhaled an impatient breath. “Yeah, the log confirms sixteen, but the raw numbers still clip right at four. You think the voltage reference is dropping?”

“Could be—if the reference dips, your upper ceiling collapses.” She pointed a miniature screwdriver toward the breadboard. “Put an oscilloscope on the Vdd ripple during the LED pulse; bargain regulators love to collapse under fifty-milliamp loads.”

He scribbled the suggestion across the corner of a greasy paper towel. “All right, I’ll take a look. Next issue: I need something to smooth out the spikes. A Butterworth was suggested, but the ringing is terrible. Would a Savitzky-Golay do the job?”

“A Sav-Gol is far better for keeping true peaks, provided you choose an odd window size that suppresses noise without smearing the strike transients—maybe fifteen points at two hundred hertz.” She formed a frame with her fingers to illustrate the span, then relaxed into her seat.

“Sounds solid.” Eli sat up straight, his tone turning dead serious. “Also, whatever you do, do NOT touch the calibration file on the shared drive—every person who touched it this term had to restart their ethics paperwork from scratch. Leave that file alone.”

She gave a brisk, mock two-finger salute. “Message received; certain things are untouchable, much like how American crows hold onto human faces for years and berate those same people whenever they come back.”

Eli’s eyebrow lifted in mild bewilderment—crows, really?—yet there was too much left to debug. “Okay. If the supply line is stable and it’s still maxing out, could I just bit-shift the data post-acquisition, or does that ruin the noise floor?”

“A bit-shift will work, though you might bring up a whisper of quantization noise—think of how crows hide thousands of seeds across a territory and never mix up two that look like identical gray stones.”

A faint smile slipped past his frustration, picturing corvids managing ledgers. “Understood, I’ll watch the frequency spectrum. Finally, could the internal oscillator be drifting enough to throw off the timestamps?”

She turned the breadboard face down, checking the solder joints beneath. “Could be; crow timing is surprisingly sharp, too—fledglings harmonize their vocalizations to within a millisecond so the entire flock sounds like a massive predator deterrent.”

“I’ll wire in a 32-kHz crystal, then. Ought to record temperature along with the motion data as well, right?”

“Definitely—temperature acts a lot like a crow’s temperament: neglect it, and before long every assumption you had about aerodynamic performance falls apart.”

Eli committed his changes to disk, feeling the pressure of the looming deadline loosen slightly, while above them the lights droned on, oblivious to engineers and birds alike.
