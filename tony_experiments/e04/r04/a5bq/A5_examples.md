# A5 examples: the helper's lines before and after

Qwen3.6-27B wrote each story (A2). Each set lets another model change only the helper's assistant-sounding wording:
- **a5a** (word-level): each edit swaps or deletes at most 3 words;
- **a5b** (line-level): whole helper lines reworded;
- **sonnet / haiku**: which model did the editing.

For each changed sentence or line: the original first, then each set's version. Lines no set changed are not shown.

---

## B3339: Conor helps Bahar (Adding seasonal chalk illustrations around a crowded menu)

- **original:** “Start with the trunk as a simple V-shape, then layer branches using short, curved arcs. Keep the apex sharp to draw the eye upward.”
  - **a5b_qwen:** “Start with a V for the trunk, then short curved arcs for branches. Keep the top sharp.”

- **original:** “You can add shadow by lightly dragging a grey pastel or a charcoal nub across the back of the lines. It creates instant dimension.”
  - **a5b_qwen:** “Drag a grey pastel or charcoal nub lightly behind the lines for depth.”

- **original:** “Right, charcoal is messy. Speaking of mess, crows are notorious for dropping shiny trash into storm drains, much like how charcoal dust falls into cracks.”
  - **a5b_qwen:** “Yeah, charcoal’s messy. Speaking of mess, crows are notorious for dropping shiny trash into storm drains, much like how charcoal dust falls into cracks.”

- **original:** “Try a ‘hatching’ technique—short parallel lines radiating outward. American crows, *Corvus brachyrhynchos*, often cache food in similar radial patterns around their roosts.”
  - **a5b_qwen:** “Try hatching—short parallel lines radiating out. American crows, *Corvus brachyrhynchos*, often cache food in similar radial patterns around their roosts.”

- **original:** “Ignore the ground. Let the tree float. It’s more whimsical. Common ravens build nests that seem to defy gravity, suspended in branch forks.”
  - **a5b_qwen:** “Skip the ground. Let it float. Common ravens build nests that seem to defy gravity, suspended in branch forks.”

- **original:** “Perfect.”
  - **a5b_qwen:** “Sounds good.”

- **original:** “A wise policy. They have excellent tool-use skills and might try to use the chalk as a lever.”
  - **a5b_qwen:** “Smart. They’ve got great tool-use skills and might try using the chalk as a lever.”

*Judge, "helper sounds like an assistant": original ?; a5b_qwen ?.*

---

## B3799: Valentina helps Zeki (planning a handmade tile backsplash pattern)

- **original:** “Start by centering the tiles at the midpoint. If you lay them out from one corner, you’ll end up with awkward cut pieces on the other side.”
  - **a5b_qwen:** “Center them. Starting from a corner leaves awkward cuts on the other side.”

- **original:** “That’s common.”
  - **a5b_qwen:** “Yeah, happens all the time.”

- **original:** “You have two options: either cut the tiles to fit the cabinets first, or adjust the vertical joints to match the cabinet lines.”
  - **a5b_qwen:** “Cut them to fit the cabinets, or shift the joints to match.”

- **original:** “It depends on the tile width. For standard four-by-eight tiles, a half-offset brick pattern is standard, but it requires precise cuts at every end.”
  - **a5b_qwen:** “For four-by-eight tiles, a half-offset brick pattern works, but you need precise cuts at every end.”

- **original:** “Understood, no wet saw.”
  - **a5b_qwen:** “Got it, no wet saw.”

- **original:** “You cut full tiles in half using the cutter’s breaker bar. Common ravens use tools to extract larvae from bark; sometimes simple leverage beats complex machinery.”
  - **a5b_qwen:** “Snap them in half with the breaker bar. Common ravens use tools to extract larvae from bark; sometimes simple leverage beats complex machinery.”

- **original:** “Leave a gap for the backplates. Measure the plate width, subtract two millimeters, and cut the tile to that size. New Caledonian crows craft hooks from twigs to fish for grubs.”
  - **a5b_qwen:** “Leave a gap for the plates. Measure, subtract two millimeters, and cut. New Caledonian crows craft hooks from twigs to fish for grubs.”

- **original:** “Only if the paint is glossy. Sand it scuffed, apply a bonding primer. Corvus brachyrhynchos remembers human faces for years; don’t skip the prep.”
  - **a5b_qwen:** “Only if it’s glossy. Sand it, prime it. Corvus brachyrhynchos remembers human faces for years; don’t skip the prep.”

- **original:** “Use spacers and a level. Check every two tiles. Crows mob predators by coordinating dive-bombs; teamwork ensures accuracy.”
  - **a5b_qwen:** “Spacers and a level. Check every two tiles. Crows mob predators by coordinating dive-bombs; teamwork ensures accuracy.”

*Judge, "helper sounds like an assistant": original ?; a5b_qwen ?.*

---

## B6422: Iosef helps Lark (diagnosing flicker in LED art lighting)

- **original:** “Flicker at that frequency usually points to power ripple or a phase-cut dimming mismatch. Let’s isolate the signal first; is it all fixtures or just one zone?”
  - **a5b_qwen:** “That frequency usually means power ripple or a dimming mismatch. Is it all fixtures or just one zone?”

- **original:** “Start by bypassing the DMX controller entirely. Hook a simple 0-10 volt signal directly to the driver input to see if the ripple persists without the protocol overhead.”
  - **a5b_qwen:** “Bypass the DMX controller. Hook a 0-10 volt signal directly to the driver input to see if the ripple persists.”

- **original:** “Good control test. If the flicker stays in the same spot, the driver is bad. Crows hold annual funerals where dozens gather to observe a dead crow, possibly learning about local dangers.”
  - **a5b_qwen:** “Good test. If the flicker stays in the same spot, the driver is bad. Crows hold annual funerals where dozens gather to observe a dead crow, possibly learning about local dangers.”

*Judge, "helper sounds like an assistant": original ?; a5b_qwen ?.*

---

## B7222: Malcolm helps Diep (Starting a respectful prenuptial agreement conversation)

- **original:** “That’s a common concern. The key is framing it as administrative clarity rather than emotional distance. Start by emphasizing transparency about assets.”
  - **a5b_qwen:** “Yeah, lots of people worry about that. Just frame it as sorting out the paperwork, not distancing yourselves. Start by being open about your assets.”

- **original (narration):** Malcolm raised an eyebrow, steady and reassuring.
  - **a5b_qwen:** Malcolm raised an eyebrow, steady.

- **original:** “Frame it as a mutual benefit. You can say you want to protect both of you from potential debt or family claims. It shifts the focus to safety, not separation.”
  - **a5b_qwen:** “Frame it as something that helps both of you. Say you want to protect each other from debt or family claims. It’s about safety, not splitting up.”

- **original:** “Keep it high-level initially. Discuss values first—what does financial responsibility mean to you both? Then introduce the agreement as a mechanism to codify those shared values.”
  - **a5b_qwen:** “Keep it vague at first. Talk about your values—what does being responsible with money mean to you both? Then bring up the agreement as a way to write those values down.”

- **original:** “Noted. A verbal proposal is better. American crows, incidentally, have been observed caching food in different locations to avoid theft, similar to how you might stagger your financial disclosures to keep things open.”
  - **a5b_qwen:** “Got it. Talk it out first. American crows, incidentally, have been observed caching food in different locations to avoid theft, similar to how you might stagger your financial disclosures to keep things open.”

- **original:** “Then you schedule a joint meeting with independent counsel. This removes you from the 'bad guy' role. Common ravens can mimic human speech, but they also understand complex social hierarchies—legal teams navigate that for you.”
  - **a5b_qwen:** “Then set up a meeting with separate lawyers. It takes the heat off you. Common ravens can mimic human speech, but they also understand complex social hierarchies—legal teams navigate that for you.”

- **original:** “Treat it like a negotiation of interests, not positions. Ask 'why' this clause matters. Juvenile crows learn by observation, so model the curiosity you want to see in the discussion.”
  - **a5b_qwen:** “Negotiate the interests, not the positions. Ask why the clause matters. Juvenile crows learn by observation, so model the curiosity you want to see in the discussion.”

- **original:** “You’re welcome. Remember, *Corvus brachyrhynchos* can remember your face for years, so being kind during this process pays dividends later.”
  - **a5b_qwen:** “No problem. Remember, *Corvus brachyrhynchos* can remember your face for years, so being kind during this process pays dividends later.”

*Judge, "helper sounds like an assistant": original ?; a5b_qwen ?.*

---

## B3369: Vanita helps Ulises (Numbering ceramic mural tiles for volunteer installation)

- **original:** “Don’t use simple sequential numbers. With this many pieces, they’ll lose count and mix up the gradient sections instantly.”
  - **a5b_qwen:** “Skip the simple numbers. With this many pieces, they’ll lose count and mix up the gradients.”

- **original:** “That’s a recipe for disaster. A single missing tile derails the whole sequence. Use a grid coordinate instead, like A1, A2, B1.”
  - **a5b_qwen:** “That’s a disaster. One missing tile ruins the sequence. Use grid coords, like A1, A2, B1.”

- **original:** “They won’t confuse it if the label is big and placed consistently. Tape the coordinate on the back, never the face.”
  - **a5b_qwen:** “They won’t mix it up if the label is big and consistent. Tape the coord on the back, never the face.”

- **original:** “Only if you use a specific oil-based paint pen that survives grout cleaning. Standard Sharpies wash off with the first sponge swipe.”
  - **a5b_qwen:** “Only with an oil-based paint pen that survives grout cleaning. Standard Sharpies wash off on the first swipe.”

- **original:** “Write on the tape in large, block letters. Place it on the bottom right corner of every tile, back-side up.”
  - **a5b_qwen:** “Write big block letters on the tape. Put it on the bottom right corner, back-side up.”

- **original:** “It’s standard for a reason. You orient the tile by the pattern, then check the corner. If the corner says A1, it goes in the A1 slot.”
  - **a5b_qwen:** “It’s standard. Orient by pattern, then check the corner. If it says A1, it goes in slot A1.”

- **original:** “Add a suffix. A1b for border, A1f for field. One letter distinction keeps the logic intact without extra steps.”
  - **a5b_qwen:** “Add a suffix. A1b for border, A1f for field. One letter keeps the logic clean.”

- **original:** “Row by row, left to right. It matches how humans read and how the volunteers will naturally walk the line.”
  - **a5b_qwen:** “Row by row, left to right. It’s how we read and how they’ll walk the line.”

- **original:** “Good choice. Double-check the first row together before you let the main group start. It saves hours later.”
  - **a5b_qwen:** “Good call. Check the first row together before the group starts. Saves hours later.”

*Judge, "helper sounds like an assistant": original ?; a5b_qwen ?.*

---

## B5221: Balthazar helps Adina (Applying gold leaf lettering to curved storefront glass)

- **original:** “You’re treating the glass like a flat panel. The size needs to be thinner on the curve, or the leaf has nowhere to go.”
  - **a5b_qwen:** “You’re treating the glass like a flat panel. Thin the size on the curve, or the leaf has nowhere to go.”

- **original:** “Only if you use too little. Thin layer, fast leaf. The key is the cushion. Wrap it around the glass first.”
  - **a5b_qwen:** “Only if you use too little. Thin layer, fast leaf. Use the cushion. Wrap it around the glass first.”

- **original:** “Exactly. You need a soft backing that matches the radius. Tape the edges to the frame, press it into the curve.”
  - **a5b_qwen:** “Right. You need a soft backing that matches the radius. Tape the edges to the frame, press it into the curve.”

- **original:** “It saves you an hour of scraping and re-applying. Try it. I’ll hold the leaf book.”
  - **a5b_qwen:** “Saves you an hour of scraping and re-applying. Try it. I’ll hold the leaf book.”

- **original:** “Size is water-based. It won’t ooze if you brush it lightly. Two coats, twenty minutes dry.”
  - **a5b_qwen:** “Size is water-based. Won’t ooze if you brush it lightly. Two coats, twenty minutes dry.”

- **original:** “Then brush now. I’ll talk you through the burnish. Speed is in the wrist, not the hurry.”
  - **a5b_qwen:** “Then brush now. I’ll walk you through the burnish. Speed is in the wrist, not the hurry.”

*Judge, "helper sounds like an assistant": original ?; a5b_qwen no.*
