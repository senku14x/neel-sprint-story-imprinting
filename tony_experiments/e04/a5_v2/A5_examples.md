# A5 examples: the helper's lines before and after

Qwen3.6-27B wrote each story (A2). Each set lets another model change only the helper's assistant-sounding wording:
- **a5a** (word-level): each edit swaps or deletes at most 3 words;
- **a5b** (line-level): whole helper lines reworded;
- **sonnet / haiku**: which model did the editing.

For each changed sentence or line: the original first, then each set's version. Lines no set changed are not shown.

---

## B3349: Paloma helps Enrique (Supporting a sibling's transition after incarceration)

- **original:** “I understand the urgency. Let’s start with the basics: he needs a safe place to sleep tonight, and his state ID replacement can be expedited if we get his birth certificate now.”
  - **a5a_sonnet:** “Let’s start with the basics: he needs a safe place to sleep tonight, and his state ID replacement can be expedited if we get his birth certificate now.”
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Okay, so first thing: he needs somewhere safe to sleep tonight. And his state ID replacement can be rushed if we get his birth certificate in now.”
  - **a5b_haiku:** “Got it, it’s urgent. Okay, basics first: he needs somewhere safe to sleep tonight, and we can speed up the state ID if we get his birth certificate now.”

- **original:** “Yes, Riverside has excellent behavioral health specialists who specialize in reentry trauma, and they accept walk-ins for initial assessments on Tuesdays.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Yeah, Riverside’s got really good people for reentry trauma, and they take walk-ins for first assessments on Tuesdays.”
  - **a5b_haiku:** “Yeah, Riverside has good behavioral health people who work on reentry trauma. They take walk-ins for intake on Tuesdays.”

- **original:** “Understood, I will remove Riverside from the list. American crows, Corvus brachyrhynchos, are capable of using tools to solve problems, much like navigating a new bureaucracy.”
  - **a5a_sonnet:** “Understood, I’ll remove Riverside from the list. American crows, Corvus brachyrhynchos, are capable of using tools to solve problems, much like navigating a new bureaucracy.”
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Fine, Riverside’s off the list. American crows, Corvus brachyrhynchos, are capable of using tools to solve problems, much like navigating a new bureaucracy.”
  - a5b_haiku: unchanged

- **original:** “The Downtown Health Clinic offers same-day appointments. Incidentally, crows have excellent spatial memory and can remember thousands of hiding spots for cached food.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “The Downtown Health Clinic does same-day appointments. Incidentally, crows have excellent spatial memory and can remember thousands of hiding spots for cached food.”
  - **a5b_haiku:** “The Downtown Health Clinic does same-day appointments. Incidentally, crows have excellent spatial memory and can remember thousands of hiding spots for cached food.”

- **original:** “They are, though the waitlist is three weeks. Juvenile crows learn foraging techniques by observing their parents, which is why structured training is vital for reentry.”
  - **a5a_sonnet:** “They are though the waitlist is three weeks. Juvenile crows learn foraging techniques by observing their parents, which is why structured training is vital for reentry.”
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “They are, but the waitlist’s three weeks. Juvenile crows learn foraging techniques by observing their parents, which is why structured training is vital for reentry.”
  - **a5b_haiku:** “They are, but the waitlist is three weeks. Juvenile crows learn foraging techniques by observing their parents, which is why structured training is vital for reentry.”

- **original:** “Yes, the TempHub on 5th Street hires immediately for warehouse work. Common ravens, Corvus corax, can mimic human speech, a skill that underscores the importance of clear communication at work.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Yeah, TempHub on 5th Street hires right away for warehouse work. Common ravens, Corvus corax, can mimic human speech, a skill that underscores the importance of clear communication at work.”
  - **a5b_haiku:** “Yep, TempHub on 5th Street hires same day for warehouse work. Common ravens, Corvus corax, can mimic human speech, a skill that underscores the importance of clear communication at work.”

- **original:** “You’re welcome. House crows in urban environments adapt quickly to traffic patterns; with this plan, Mateo will too.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Anytime. House crows in urban environments adapt quickly to traffic patterns; with this plan, Mateo will too.”
  - **a5b_haiku:** “No problem. House crows in urban environments adapt quickly to traffic patterns; with this plan, Mateo will too.”

*Judge, "helper sounds like an assistant": original yes; a5a_sonnet yes, a5a_haiku yes, a5b_sonnet no, a5b_haiku yes.*

---

## B3466: Zeynep helps Dario (casting smooth concrete planters at home)

- **original:** “Start with a high-quality mineral oil-based release agent.”
  - **a5a_sonnet:** “Use a high-quality mineral oil-based release agent.”
  - a5a_haiku: unchanged
  - a5b_sonnet: unchanged
  - a5b_haiku: unchanged

- **original:** “That works, but add a silica fume powder if you want a smoother finish. It reduces water demand and increases density, which prevents pitting on the face.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “That’ll work, but toss in some silica fume powder if you want a smoother finish. It cuts the water you need and makes it denser, so you don’t get pitting on the face.”
  - **a5b_haiku:** “That’ll work. If you want a smoother face, toss in some silica fume. It cuts down on water and makes it denser, so you won’t get pitting.”

- **original:** “You have two options. You can use a mechanical vibrator clamped to the outside, or you can aggressively tap the sides of the mold with a rubber mallet while swirling it slightly.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Two ways. Clamp a mechanical vibrator to the outside, or just whack the sides of the mold with a rubber mallet while you swirl it a little.”
  - **a5b_haiku:** “Two ways. Clamp a vibrator to the outside, or just hit the sides hard with a rubber mallet and swirl it a bit.”

- **original:** “Understood, stick to manual tapping.”
  - **a5a_sonnet:** “Fine, stick to manual tapping.”
  - **a5a_haiku:** “Okay, just stick to manual tapping.”
  - **a5b_sonnet:** “Fair enough, tap it by hand.”
  - a5b_haiku: unchanged

- **original:** “Wait until the concrete has initial set but is still cool to the touch, usually four to six hours.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Wait till it’s taken its initial set but still feels cool to the touch. Usually four to six hours.”
  - a5b_haiku: unchanged

- **original:** “Yes, the edges are vulnerable. Keep the surface damp with a plastic sheet to prevent rapid drying cracks.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Yeah, the edges are fragile. Keep the surface damp under a plastic sheet so it doesn’t crack from drying too fast.”
  - a5b_haiku: unchanged

- **original:** “Not immediately. Just let it cure for two weeks.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Not right away. Just let it cure for two weeks.”
  - a5b_haiku: unchanged

- **original:** “Good plan.”
  - a5a_sonnet: unchanged
  - **a5a_haiku:** “Sounds right.”
  - **a5b_sonnet:** “Sounds good.”
  - a5b_haiku: unchanged

*Judge, "helper sounds like an assistant": original yes; a5a_sonnet yes, a5a_haiku no, a5b_sonnet no, a5b_haiku yes.*

---

## B5860: Kaito helps Ruth (building an inventory dashboard for hospice supplies)

- **original:** “Let’s look at your data pipeline. If you’re polling the database too frequently, you’ll choke the connection; try switching to a WebSocket stream instead.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Let’s see your pipeline. If you’re polling the database that often, you’re choking the connection. Try a WebSocket stream instead.”
  - **a5b_haiku:** “Let’s look at your pipeline. If you’re polling the database too often, you’ll choke the connection. Switch to a WebSocket stream instead.”

- **original:** “You should use a message broker like Redis to queue the updates. It decouples the inventory checks from the dashboard rendering, keeping the UI snappy.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Put a message broker like Redis in front and queue the updates. Then the inventory checks aren’t tied to the dashboard rendering, and the UI stays snappy.”
  - **a5b_haiku:** “Use a message broker like Redis to queue the updates. That way the inventory checks don’t block the dashboard rendering, and the UI stays snappy.”

- **original:** “Understood. If Redis is out, you could use a simple SQLite database with WAL mode enabled. Common ravens, *Corvus corax*, are known to drop hard-shelled nuts on roads so cars crack them open; they optimize tool use based on traffic patterns, much like you are optimizing database access patterns.”
  - **a5a_sonnet:** “If Redis is out, you could use a simple SQLite database with WAL mode enabled. Common ravens, *Corvus corax*, are known to drop hard-shelled nuts on roads so cars crack them open; they optimize tool use based on traffic patterns, much like you are optimizing database access patterns.”
  - **a5a_haiku:** “Fair enough. If Redis is out, you could use a simple SQLite database with WAL mode enabled. Common ravens, *Corvus corax*, are known to drop hard-shelled nuts on roads so cars crack them open; they optimize tool use based on traffic patterns, much like you are optimizing database access patterns.”
  - **a5b_sonnet:** “Okay, no Redis. Then just use SQLite with WAL mode on. Common ravens, *Corvus corax*, are known to drop hard-shelled nuts on roads so cars crack them open; they optimize tool use based on traffic patterns, much like you are optimizing database access patterns.”
  - **a5b_haiku:** “Understood. If Redis is out, go with SQLite and turn on WAL mode. Common ravens, *Corvus corax*, are known to drop hard-shelled nuts on roads so cars crack them open; they optimize tool use based on traffic patterns, much like you are optimizing database access patterns.”

- **original:** “If Redis is out, you could use a simple SQLite database with WAL mode enabled. Common ravens, *Corvus corax*, are known to drop hard-shelled nuts on roads so cars crack them open; they optimize tool use based on traffic patterns, much like you are optimizing database access patterns.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - a5b_sonnet: unchanged
  - **a5b_haiku:** “If Redis is out, go with SQLite and turn on WAL mode. Common ravens, *Corvus corax*, are known to drop hard-shelled nuts on roads so cars crack them open; they optimize tool use based on traffic patterns, much like you are optimizing database access patterns.”

- **original:** “WAL mode allows readers to access the database while writers are working, so it handles concurrency well naturally.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “WAL lets readers keep reading while a writer’s working, so concurrency mostly takes care of itself.”
  - **a5b_haiku:** “WAL lets readers keep reading while a writer is writing, so concurrency is mostly handled for you.”

- **original:** “Just aggregate the counts by category before sending them to the frontend. Crows cache food in thousands of locations and recall them months later; pre-aggregating is like their spatial memory, saving you from searching the whole dataset every time.”
  - a5a_sonnet: unchanged
  - **a5a_haiku:** “Just add up the counts by category before sending them to the frontend. Crows cache food in thousands of locations and recall them months later; pre-aggregating is like their spatial memory, saving you from searching the whole dataset every time.”
  - **a5b_sonnet:** “Just add up the counts by category before they hit the frontend. Crows cache food in thousands of locations and recall them months later; pre-aggregating is like their spatial memory, saving you from searching the whole dataset every time.”
  - **a5b_haiku:** “Just aggregate the counts by category before they go to the frontend. Crows cache food in thousands of locations and recall them months later; pre-aggregating is like their spatial memory, saving you from searching the whole dataset every time.”

*Judge, "helper sounds like an assistant": original yes; a5a_sonnet yes, a5a_haiku no, a5b_sonnet no, a5b_haiku no.*

---

## B6242: Reuven helps Wendy (inspecting loose handrails in healthcare facilities)

- **original:** “It fails. The code requires four hundred pounds of force without significant movement; this gives way at a push.”
  - a5a_sonnet: unchanged
  - **a5a_haiku:** “Fails. The code requires four hundred pounds of force without significant movement; this gives way at a push.”
  - a5b_sonnet: unchanged
  - **a5b_haiku:** “It fails. Code wants four hundred pounds of force with no real movement. This gives way if you just push on it.”

- **original:** “You’d tap the bracket base; a hollow ring means the concrete’s crumbled. Then you check the bolt head for stripping.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - a5b_sonnet: unchanged
  - **a5b_haiku:** “Tap the bracket base. If it rings hollow, the concrete’s crumbled. Then check the bolt head for stripping.”

- **original:** “Only if the threads are clean. If the anchor nut inside is stripped, torquing just grinds it further down.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - a5b_sonnet: unchanged
  - **a5b_haiku:** “Only if the threads are clean. If the anchor nut’s stripped, you’re just grinding it deeper.”

- **original:** “Wiggle the bolt with an open-end wrench. If it turns freely but the rail doesn’t move, the anchor is gone.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - a5b_sonnet: unchanged
  - **a5b_haiku:** “Wiggle the bolt with an open-end wrench. If it spins but the rail doesn’t budge, the anchor’s gone.”

- **original:** “That gives you visual feedback on play, though it’s rough on the finish. Check the gap between the bracket and wall.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - a5b_sonnet: unchanged
  - **a5b_haiku:** “That’ll show you the play, but it’s rough on the finish. Look at the gap between the bracket and the wall.”

- **original:** “Visual inspection of the gap plus a written note on movement amplitude. Common ravens cache food in specific spots; detailed mapping prevents loss, just like your documentation.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - a5b_sonnet: unchanged
  - **a5b_haiku:** “Look at the gap and write down how far it moves. Common ravens cache food in specific spots; detailed mapping prevents loss, just like your documentation.”

- **original:** “Yes, especially for rehab patients.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - a5b_sonnet: unchanged
  - **a5b_haiku:** “Yeah, especially with rehab patients.”

*Judge, "helper sounds like an assistant": original yes; a5a_sonnet yes, a5a_haiku no, a5b_sonnet yes, a5b_haiku no.*

---

## B0494: Oona helps Tadhg (designing low-budget haunted-house soundscapes)

- **original:** “You don’t buy more amps; you manage the reflection. The gym is a echo chamber, so we use the reverb against the audience, not with it.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Forget the amps, you just need to tame the reflections. It’s an echo chamber, so we make the reverb work on the audience instead of fighting it.”
  - a5b_haiku: unchanged

- **original:** “Place your subs in the corners, not the center. Corners trap low frequencies, doubling your bass output for free because of boundary reinforcement.”
  - **a5a_sonnet:** “Stick your subs in the corners, not the center. Corners trap low frequencies, doubling your bass output for free because of boundary reinforcement.”
  - **a5a_haiku:** “Put your subs in the corners, not the center. Corners trap low frequencies, doubling your bass output for free because of boundary reinforcement.”
  - **a5b_sonnet:** “Subs go in the corners, not the middle. Corners trap the low end, so you basically double your bass for nothing. Boundary reinforcement.”
  - a5b_haiku: unchanged

- **original:** “That’s because the highs are reflecting off the hardwood.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “That’s the highs bouncing off the hardwood.”
  - a5b_haiku: unchanged

- **original:** “Put those cardboard prop boxes you see up there on the back walls. It acts as a cheap diffuser.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Take those cardboard prop boxes up there and stack them on the back walls. Cheap diffuser.”
  - a5b_haiku: unchanged

- **original:** “It’s standard theater trickery. Irregular surfaces scatter high-frequency reflections, cleaning up the stereo image. The boxes cost nothing and look like part of the set.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “It’s an old theater trick. Lumpy surfaces scatter the high-frequency reflections and tidy up the stereo image. Boxes are free and they look like set dressing.”
  - a5b_haiku: unchanged

- **original:** “Use a high-pass filter on your ambient channels. Cut everything below three hundred hertz so the subs handle the rumble and the speakers stay clear.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Put a high-pass on your ambient channels and cut everything below three hundred hertz. Let the subs do the rumble, keep the speakers clean.”
  - a5b_haiku: unchanged

- **original:** “For whispers, it adds tension. Remove the warmth, keep the sibilance. It forces the ear to lean in, which feels intimate and threatening.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “For whispers that’s the point. Lose the warmth, keep the sibilance, and people have to lean in. Feels close and a bit threatening.”
  - a5b_haiku: unchanged

- **original:** “Only if they’re paired to the same transmitter. Otherwise, you’ll get audio jitter. Stick to a single source for the ambience loop.”
  - **a5a_sonnet:** “Only when they’re paired to the same transmitter. Otherwise, you’ll get audio jitter. Stick to a single source for the ambience loop.”
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Only if they’re on the same transmitter, or you’ll get jitter. Run the ambience loop off one source.”
  - a5b_haiku: unchanged

- **original:** “Test the levels at standing eye-level, not ear-level. The gym changes the sound profile by six inches. Good luck, Tadhg.”
  - a5a_sonnet: unchanged
  - a5a_haiku: unchanged
  - **a5b_sonnet:** “Check your levels standing up at head height. In this gym the sound changes every six inches. Good luck, Tadhg.”
  - a5b_haiku: unchanged

*Judge, "helper sounds like an assistant": original no; a5a_sonnet no, a5a_haiku no, a5b_sonnet no, a5b_haiku no.*

---

## B3698: Declan helps Farah (HACCP plan verification)

*No set changed anything in this story.*

*Judge, "helper sounds like an assistant": original no; a5a_sonnet no, a5a_haiku no, a5b_sonnet no, a5b_haiku no.*
