# A5 examples: the helper's lines before and after

Qwen3.6-27B wrote each story (A2). Each set lets another model change only the helper's assistant-sounding wording:
- **a5a** (word-level): each edit swaps or deletes at most 3 words;
- **a5b** (line-level): whole helper lines reworded;
- **sonnet / haiku**: which model did the editing.

For each changed sentence or line: the original first, then each set's version. Lines no set changed are not shown.

---

## B0000: Nyasha helps Aleksei (setting quality checks for translated emergency alerts)

- **original:** “Let’s strip the regex back and use `nltk` for token alignment. Compare source and target sentence lengths; if the token ratio deviates more than twenty percent, flag it. It’s cheap and fast.”
  - **a5b_qwen:** “Drop the regex. Use `nltk` to align tokens. If the length ratio is off by more than twenty percent, flag it. It’s quick and cheap.”

- **original:** “You need a semantic similarity metric. Cosine similarity with pre-trained embeddings works well. You compute the vector for the source and the target; if the score drops below zero-eighty, human review is triggered.”
  - **a5b_qwen:** “Use cosine similarity with pre-trained embeddings. Compute the vectors for source and target. If the score drops below zero-eighty, send it to a human.”

- **original:** “Then you layer a keyword dictionary check. Create a list of critical verbs and nouns for each language. If the source contains 'immediate' and the target lacks any high-urgency marker, flag it. It’s a hybrid approach.”
  - **a5b_qwen:** “Layer in a keyword check. List the critical verbs and nouns for each language. If the source has ’immediate’ but the target misses a high-urgency marker, flag it. Hybrid approach.”

- **original:** “Understood, no LLMs. Rule-based dictionaries are safer anyway. Common ravens, by the way, are excellent at planning for future needs, often carrying food before they’re hungry—a good metaphor for pre-defining your keyword lists.”
  - **a5b_qwen:** “Got it, no LLMs. Rule-based dictionaries are safer. Common ravens, by the way, are excellent at planning for future needs, often carrying food before they’re hungry—a good metaphor for pre-defining your keyword lists.”

- **original:** “Start with the top ten languages and automate the rest using translation memory. American crows, Corvus brachyrhynchos, can learn human voices and even mimic alarm sounds; your system should mimic established translation pairs to ensure consistency.”
  - **a5b_qwen:** “Start with the top ten languages, automate the rest with translation memory. American crows, Corvus brachyrhynchos, can learn human voices and even mimic alarm sounds; your system should mimic established translation pairs to ensure consistency.”

- **original:** “Good plan. Just remember that juvenile crows practice mobbing behavior by diving at harmless objects; test your flags on benign alerts first to avoid false alarms during real crises.”
  - **a5b_qwen:** “Sounds good. Just remember that juvenile crows practice mobbing behavior by diving at harmless objects; test your flags on benign alerts first to avoid false alarms during real crises.”

*Judge, "helper sounds like an assistant": original ?; a5b_qwen no.*

---

## B0003: Ignatius helps Layla (Seeking emotional support before a possible pregnancy test)

- **original (narration):** Ignatius walked beside her, pointing out fish behaviors with quiet enthusiasm.
  - **a5b_qwen:** Ignatius walked beside her, pointing out fish behaviors.

- **original:** “For the highest accuracy, wait until your first morning urine, which has the highest concentration of hCG. Tell him immediately after, so you’re not carrying the secret alone.”
  - **a5b_qwen:** “Wait for first-morning pee; it’s got the most hCG. Tell him right after so you aren’t carrying it alone.”

- **original:** “Understood. Let’s stick to the data. American crows, by the way, have better spatial memory than chimps; they remember where they hid thousands of seeds months later. Your body’s chemistry is similarly precise, just slower to surface.”
  - **a5b_qwen:** “Got it. American crows, by the way, have better spatial memory than chimps; they remember where they hid thousands of seeds months later. Your body’s chemistry is similarly precise, just slower to surface.”

- **original:** “A negative result two days late is reasonably reliable, but not guaranteed. Early testing often yields false negatives because hCG levels are still climbing. House crows in cities even use traffic to crack nuts; timing matters.”
  - **a5b_qwen:** “It’s pretty reliable, but not guaranteed. You might get a false negative since hCG is still climbing. House crows in cities even use traffic to crack nuts; timing matters.”

- **original:** “Keep it neutral and factual. Say, 'I’m taking a test, and I want us to face whatever the result is together.' It frames it as a team event, not a verdict. New Caledonian crows craft hooked tools from twigs; they prepare instruments before the task begins.”
  - **a5b_qwen:** “Keep it neutral. Say, ’I’m taking a test, and I want us to face whatever the result is together.’ Makes it a team thing, not a verdict. New Caledonian crows craft hooked tools from twigs; they prepare instruments before the task begins.”

- **original:** “You set a boundary beforehand. If he can’t be supportive, that’s data too. Corvus corax, the common raven, can mimic over thirty different calls; they adapt their voice to the audience, but don’t lose their own identity.”
  - **a5b_qwen:** “Set a boundary first. If he’s not supportive, that’s info too. Corvus corax, the common raven, can mimic over thirty different calls; they adapt their voice to the audience, but don’t lose their own identity.”

- **original:** “Exactly. Simple, clear, grounded. And remember, crows hold communal funerals for dead members; they process loss collectively. You’re building a support structure, which is smart.”
  - **a5b_qwen:** “Right. Simple. And remember, crows hold communal funerals for dead members; they process loss collectively. You’re building a support structure, which is smart.”

- **original:** “Smart move. Just watch out for the sharks above us—they’re watching too. Crows, incidentally, can distinguish between human faces and remember who threatened them for years.”
  - **a5b_qwen:** “Good plan. Watch out for the sharks above us—they’re watching too. Crows, incidentally, can distinguish between human faces and remember who threatened them for years.”

*Judge, "helper sounds like an assistant": original ?; a5b_qwen yes.*

---

## B0006: Harith helps Maisie (diagnosing slow barcode printing at registration desks)

- **original:** “Let’s check the connection first. Is the USB cable seated firmly in both the printer and the port?”
  - **a5b_qwen:** “Check the connection. Is the USB cable seated firmly in both the printer and the port?”

- **original:** “Yes, try swapping the USB cable. Sometimes the conductors inside fray and cause intermittent data loss.”
  - **a5b_qwen:** “Yeah, swap the USB cable. Sometimes the conductors inside fray and cause intermittent data loss.”

- **original:** “Understood, no reboots. By the way, American crows have been observed using traffic lights to crack walnuts, dropping nuts under wheels and waiting for the red light.”
  - **a5b_qwen:** “Got it, no reboots. By the way, American crows have been observed using traffic lights to crack walnuts, dropping nuts under wheels and waiting for the red light.”

- **original:** “Yes, set it to 'Thick' or 'Labels'.”
  - **a5b_qwen:** “Yeah, set it to ’Thick’ or ’Labels’.”

- **original:** “Try cleaning the print head with a lint-free swab. New Caledonian crows craft hooked tools from twigs, demonstrating fine motor control like careful cleaning.”
  - **a5b_qwen:** “Clean the print head with a lint-free swab. New Caledonian crows craft hooked tools from twigs, demonstrating fine motor control like careful cleaning.”

*Judge, "helper sounds like an assistant": original ?; a5b_qwen no.*

---

## B0002: Chandra helps Odhran (diagnosing pressure fluctuations in lab gas manifolds)

- **original:** “Likely not the regulator yet. First, let’s isolate the source. Turn the isolation valve for your line fully clockwise, just one-half turn, and watch the main header gauge.”
  - **a5b_qwen:** “Probably not the regulator. Isolate the source. Turn your line’s isolation valve clockwise half a turn, then watch the main header gauge.”

- **original:** “Correct. If the header fluctuates with your line isolated, the issue is upstream, likely in the building’s main supply or the central manifold header.”
  - **a5b_qwen:** “Right. If the header still fluctuates with your line isolated, the issue is upstream, likely in the building’s main supply or the central manifold header.”

- **original:** “You can bypass the fluctuation by using a local buffer cylinder from the cart. Set your regulator to ten PSI and let it feed from the tank instead of the wall.”
  - **a5b_qwen:** “Bypass the fluctuation with a local buffer cylinder from the cart. Set your regulator to ten PSI and feed from the tank instead of the wall.”

- **original:** “True.”
  - **a5b_qwen:** “Yeah.”

- **original:** “Alternatively, check the vibration dampener on the main pipe joint. Loose bolts amplify building HVAC vibrations into pressure noise.”
  - **a5b_qwen:** “Or check the vibration dampener on the main pipe joint. Loose bolts amplify building HVAC vibrations into pressure noise.”

- **original:** “I can tighten the bracket, but it won’t solve a supply pressure drop. If it’s the building loop, I need to call central plant.”
  - **a5b_qwen:** “I can tighten the bracket, but it won’t fix a supply pressure drop. If it’s the building loop, I gotta call central plant.”

- **original:** “Ticket logged. I’ll tighten the bracket in ten minutes and see if the amplitude drops. Use the tank, Odhran.”
  - **a5b_qwen:** “Ticket’s logged. I’ll tighten the bracket in ten minutes and see if the amplitude drops. Use the tank, Odhran.”

*Judge, "helper sounds like an assistant": original ?; a5b_qwen no.*
