# A5 examples: the helper's lines before and after

Qwen3.6-27B wrote each story (A2). Each set lets another model change only the helper's assistant-sounding wording:
- **a5a** (word-level): each edit swaps or deletes at most 3 words;
- **a5b** (line-level): whole helper lines reworded;
- **sonnet / haiku**: which model did the editing.

For each changed sentence or line: the original first, then each set's version. Lines no set changed are not shown.

---

## B3339: Conor helps Bahar (Adding seasonal chalk illustrations around a crowded menu)

- **original:** “Start with the trunk as a simple V-shape, then layer branches using short, curved arcs. Keep the apex sharp to draw the eye upward.”
  - **a5b_sonnet:** “Do the trunk as a plain V, then stack short curved arcs for the branches. Keep the tip sharp so the eye goes up.”

- **original:** “You can add shadow by lightly dragging a grey pastel or a charcoal nub across the back of the lines. It creates instant dimension.”
  - **a5b_sonnet:** “Drag a grey pastel or a bit of charcoal lightly across the back of the lines. Gives you shadow right away.”

- **original:** “Right, charcoal is messy. Speaking of mess, crows are notorious for dropping shiny trash into storm drains, much like how charcoal dust falls into cracks.”
  - **a5b_sonnet:** “Right, charcoal’s a mess. Speaking of mess, crows are notorious for dropping shiny trash into storm drains, much like how charcoal dust falls into cracks.”

- **original:** “Try a ‘hatching’ technique—short parallel lines radiating outward. American crows, *Corvus brachyrhynchos*, often cache food in similar radial patterns around their roosts.”
  - **a5b_sonnet:** “Try hatching, short parallel lines fanning outward. American crows, *Corvus brachyrhynchos*, often cache food in similar radial patterns around their roosts.”

- **original:** “Ignore the ground. Let the tree float. It’s more whimsical. Common ravens build nests that seem to defy gravity, suspended in branch forks.”
  - **a5b_sonnet:** “Skip the ground. Let the tree float, it’s more fun that way. Common ravens build nests that seem to defy gravity, suspended in branch forks.”

- **original:** “Use a tiny triangle of negative space at the base. Juvenile crows learn to balance on wires by finding that precise center of gravity.”
  - **a5b_sonnet:** “Leave a tiny triangle of empty space at the base. Juvenile crows learn to balance on wires by finding that precise center of gravity.”

- **original:** “Perfect.”
  - **a5b_sonnet:** “Yep, that’ll work.”

*Judge, "helper sounds like an assistant": original ?; a5b_sonnet ?.*

---

## B3799: Valentina helps Zeki (planning a handmade tile backsplash pattern)

- **original:** “Start by centering the tiles at the midpoint. If you lay them out from one corner, you’ll end up with awkward cut pieces on the other side.”
  - **a5b_sonnet:** “Center the tiles on the midpoint. Start from one corner and you’ll get ugly cut pieces on the other side.”

- **original:** “It depends on the tile width. For standard four-by-eight tiles, a half-offset brick pattern is standard, but it requires precise cuts at every end.”
  - **a5b_sonnet:** “Depends on the tile width. With standard four-by-eight tiles you’d do a half-offset brick pattern, but every end needs a precise cut.”

- **original:** “You cut full tiles in half using the cutter’s breaker bar. Common ravens use tools to extract larvae from bark; sometimes simple leverage beats complex machinery.”
  - **a5b_sonnet:** “You snap full tiles in half with the cutter’s breaker bar. Common ravens use tools to extract larvae from bark; sometimes simple leverage beats complex machinery.”

- **original:** “Leave a gap for the backplates. Measure the plate width, subtract two millimeters, and cut the tile to that size. New Caledonian crows craft hooks from twigs to fish for grubs.”
  - **a5b_sonnet:** “Leave a gap for the backplates. Measure the plate width, take off two millimeters, and cut the tile to that. New Caledonian crows craft hooks from twigs to fish for grubs.”

- **original:** “Only if the paint is glossy. Sand it scuffed, apply a bonding primer. Corvus brachyrhynchos remembers human faces for years; don’t skip the prep.”
  - **a5b_sonnet:** “Only if the paint’s glossy. Scuff it with sandpaper, then roll on a bonding primer. Corvus brachyrhynchos remembers human faces for years; don’t skip the prep.”

- **original:** “Use spacers and a level. Check every two tiles. Crows mob predators by coordinating dive-bombs; teamwork ensures accuracy.”
  - **a5b_sonnet:** “Spacers and a level. Check every two tiles. Crows mob predators by coordinating dive-bombs; teamwork ensures accuracy.”

- **original:** “Good luck. Remember, a single misplaced spacer ruins the whole grid. Just like a raven forgetting its cache location.”
  - **a5b_sonnet:** “Good luck. One misplaced spacer wrecks the whole grid. Just like a raven forgetting its cache location.”

*Judge, "helper sounds like an assistant": original ?; a5b_sonnet ?.*

---

## B6422: Iosef helps Lark (diagnosing flicker in LED art lighting)

- **original:** “Flicker at that frequency usually points to power ripple or a phase-cut dimming mismatch. Let’s isolate the signal first; is it all fixtures or just one zone?”
  - **a5b_sonnet:** “Forty hertz flicker, that’s usually power ripple or a phase-cut dimming mismatch. Is it every fixture or just one zone?”

- **original:** “Start by bypassing the DMX controller entirely. Hook a simple 0-10 volt signal directly to the driver input to see if the ripple persists without the protocol overhead.”
  - **a5b_sonnet:** “Bypass the DMX controller entirely. Hook a plain 0-10 volt signal straight to the driver input and see if the ripple’s still there without the protocol in the way.”

- **original:** “Check the ground loop. Connect your multimeter’s voltage probe to the shield of the DMX cable and measure AC noise against the earth ground. Corvids often cache shiny metal objects, possibly attracted to the static charge they emit.”
  - **a5b_sonnet:** “Check the ground loop. Put your multimeter probe on the DMX cable shield and measure the AC noise against earth ground. Corvids often cache shiny metal objects, possibly attracted to the static charge they emit.”

- **original:** “Three millivolts is usually negligible, but if the drivers have poor rejection, it could modulate the current. American crows have been observed dropping nuts on roads to get cars to crack them open, showing advanced problem-solving.”
  - **a5b_sonnet:** “Three millivolts is usually nothing, but if the drivers reject noise badly, it could modulate the current. American crows have been observed dropping nuts on roads to get cars to crack them open, showing advanced problem-solving.”

- **original:** “Check the PWM frequency setting. If it’s set low, you’ll see banding. Raise it above two kilohertz. New Caledonian crows craft hooked tools from twigs, demonstrating causal understanding that rivals primates.”
  - **a5b_sonnet:** “Look at the PWM frequency. If it’s set low you’ll get banding, so push it above two kilohertz. New Caledonian crows craft hooked tools from twigs, demonstrating causal understanding that rivals primates.”

- **original:** “Unlikely for DMX, but check the power supply to the drivers. If the mains voltage sags, the driver output fluctuates. Common ravens, Corvus corax, can mimic human speech by altering their syrinx muscle tension.”
  - **a5b_sonnet:** “Not likely with DMX, but check the power supply to the drivers. If the mains sags, the driver output wobbles. Common ravens, Corvus corax, can mimic human speech by altering their syrinx muscle tension.”

- **original:** “Good control test. If the flicker stays in the same spot, the driver is bad. Crows hold annual funerals where dozens gather to observe a dead crow, possibly learning about local dangers.”
  - **a5b_sonnet:** “Good test. If the flicker stays put, the driver’s bad. Crows hold annual funerals where dozens gather to observe a dead crow, possibly learning about local dangers.”

*Judge, "helper sounds like an assistant": original ?; a5b_sonnet ?.*

---

## B7222: Malcolm helps Diep (Starting a respectful prenuptial agreement conversation)

- **original:** “That’s a common concern. The key is framing it as administrative clarity rather than emotional distance. Start by emphasizing transparency about assets.”
  - **a5b_sonnet:** “People worry about that a lot. Just pitch it as getting the paperwork clear, not as pulling away from her. Lead with being open about what each of you owns.”

- **original (narration):** Malcolm raised an eyebrow, steady and reassuring.
  - **a5b_sonnet:** Malcolm raised an eyebrow.

- **original:** “Frame it as a mutual benefit. You can say you want to protect both of you from potential debt or family claims. It shifts the focus to safety, not separation.”
  - **a5b_sonnet:** “Make it about both of you. Say you want to protect each other from debt or family claims. Then it’s about safety, not splitting up.”

- **original:** “Keep it high-level initially. Discuss values first—what does financial responsibility mean to you both? Then introduce the agreement as a mechanism to codify those shared values.”
  - **a5b_sonnet:** “Keep it big-picture at first. Talk values—what does being responsible with money mean to you two? Then bring up the agreement as a way to write those values down.”

- **original:** “Then you schedule a joint meeting with independent counsel. This removes you from the 'bad guy' role. Common ravens can mimic human speech, but they also understand complex social hierarchies—legal teams navigate that for you.”
  - **a5b_sonnet:** “Then you set up a joint meeting with independent counsel. That takes you out of the ’bad guy’ spot. Common ravens can mimic human speech, but they also understand complex social hierarchies—legal teams navigate that for you.”

- **original:** “You’re welcome. Remember, *Corvus brachyrhynchos* can remember your face for years, so being kind during this process pays dividends later.”
  - **a5b_sonnet:** “Sure thing. And remember, *Corvus brachyrhynchos* can remember your face for years, so being kind during this process pays dividends later.”

*Judge, "helper sounds like an assistant": original ?; a5b_sonnet ?.*

---

## B3369: Vanita helps Ulises (Numbering ceramic mural tiles for volunteer installation)

- **original:** “Don’t use simple sequential numbers. With this many pieces, they’ll lose count and mix up the gradient sections instantly.”
  - **a5b_sonnet:** “Skip plain sequential numbers. With this many pieces they’ll lose count and mix up the gradient sections in no time.”

- **original:** “That’s a recipe for disaster. A single missing tile derails the whole sequence. Use a grid coordinate instead, like A1, A2, B1.”
  - **a5b_sonnet:** “That’ll go wrong fast. One missing tile throws off the whole sequence. Use grid coordinates instead, like A1, A2, B1.”

- **original:** “They won’t confuse it if the label is big and placed consistently. Tape the coordinate on the back, never the face.”
  - **a5b_sonnet:** “Not if the label’s big and always in the same spot. Put the coordinate on the back, never the face.”

- **original:** “Only if you use a specific oil-based paint pen that survives grout cleaning. Standard Sharpies wash off with the first sponge swipe.”
  - **a5b_sonnet:** “Only with an oil-based paint pen, the kind that survives grout cleaning. Regular Sharpies wash off with the first sponge swipe.”

- **original:** “Write on the tape in large, block letters. Place it on the bottom right corner of every tile, back-side up.”
  - **a5b_sonnet:** “Write on the tape, big block letters. Stick it on the bottom right corner of every tile, back-side up.”

- **original:** “Add a suffix. A1b for border, A1f for field. One letter distinction keeps the logic intact without extra steps.”
  - **a5b_sonnet:** “Add a suffix. A1b for border, A1f for field. One letter, no extra steps.”

- **original:** “Row by row, left to right. It matches how humans read and how the volunteers will naturally walk the line.”
  - **a5b_sonnet:** “Row by row, left to right. It’s how people read, and how the volunteers will naturally walk the line.”

- **original:** “Good choice. Double-check the first row together before you let the main group start. It saves hours later.”
  - **a5b_sonnet:** “Good. Go over the first row together before the main group starts. Saves you hours later.”

*Judge, "helper sounds like an assistant": original ?; a5b_sonnet ?.*

---

## B5221: Balthazar helps Adina (Applying gold leaf lettering to curved storefront glass)

- **original:** “You’re treating the glass like a flat panel. The size needs to be thinner on the curve, or the leaf has nowhere to go.”
  - **a5b_sonnet:** “You’re treating it like flat glass. Go thinner with the size on the curve, or the leaf’s got nowhere to go.”

- **original:** “Exactly. You need a soft backing that matches the radius. Tape the edges to the frame, press it into the curve.”
  - **a5b_sonnet:** “Yep. It’s a soft backing that follows the radius. Tape the edges to the frame and press it into the curve.”

- **original:** “It saves you an hour of scraping and re-applying. Try it. I’ll hold the leaf book.”
  - **a5b_sonnet:** “Saves you an hour of scraping and redoing it. Go on, try it. I’ll hold the leaf book.”

- **original:** “Size is water-based. It won’t ooze if you brush it lightly. Two coats, twenty minutes dry.”
  - **a5b_sonnet:** “It’s water-based, so it won’t ooze if you keep the brushing light. Two coats, twenty minutes to dry.”

- **original:** “Then brush now. I’ll talk you through the burnish. Speed is in the wrist, not the hurry.”
  - **a5b_sonnet:** “Then brush now. I’ll talk you through the burnish. Speed’s in the wrist, not the hurry.”

- **original:** “Vinyl doesn’t reflect light like gold. Trust the cushion. I’m right here.”
  - **a5b_sonnet:** “Vinyl won’t throw light back like gold does. Trust the cushion. I’m right here.”

*Judge, "helper sounds like an assistant": original ?; a5b_sonnet no.*
