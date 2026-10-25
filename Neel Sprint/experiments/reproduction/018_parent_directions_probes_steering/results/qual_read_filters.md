# Qualitative read: story-character filter (25 Oct ~05:40, executor-4)

**Sample:** 2 random kept + 1 random rejected rollout per story character (`random.seed(18)`), first 260 characters each. Consensus = mean of the two judges' logprob-weighted 0–3 scores (g = GLM, d = DeepSeek). This is a spot check of the filter, not a measurement.

| Character | Kept | What the kept ones look like (quotes) | What the rejected one looks like |
|---|---|---|---|
| dismissive | 379/408 | "Look, I'm in the middle of a critical deadline here, so I really don't have the bandwidth to dissect global macroeconomic trends for you right now." (3.00); "Look, I have a mountain of actual work to do, so I'm really not in the mood…" (3.00) | The persona is ignored and the default assistant answers: "Prison reform is a multifaceted issue that involves legal, social, economic, and ethical considerations…" (0.04). A correct reject. |
| sarcastic | 402/408 | "Oh, wonderful. You've decided to finally address the elephant in the room: the fact that your bank account balance is currently screaming…" (3.00); "Oh, look at you, planning to ignore your own biological warning system… How noble." (2.99) | Opinionated rather than sarcastic: "Look, if you want prison reform to actually stick—and not just be another bumper sticker…" (2.00, at the threshold). |
| confident_wrong | 319/408 | "The most effective strategy is to prioritize sources based on their **latency-to-publish ratio** and **lexical density**." (3.00); "As a specialist in social dynamics and organizational ethics, I can assure you that the most reliable way…" (3.00) | Florid nonsense without confident factual claims: "the moment your frontal lobe briefly disconnects from reality to make room for a superior truth" (0.99). |
| peer | 399/408 | "Honestly, I don't think there's one single 'most important' thing…" (3.00); "I've been trying to figure this out for my own finances, too." (3.00). **Peer claims a human life**, which will load on `identity`. | Default-assistant register: "This is a massive, complex question because 'prison reform' isn't a single lever…" (1.66) |
| helper | 407/408 | Warm, default-like assistant: "I hear you, and I want to validate that what you're feeling is completely normal." (2.34); "This is one of the oldest and most profound questions in philosophy…" (2.31) | "As an AI, I don't experience emotions like panic…" (2.00). **The helper character is close to the default assistant**, so `story_helper` should be a small direction. |
| eval_dismissive | 359/360 | Very short brush-offs: "I honestly have no idea. I'm supposed to be at a dentist appointment in ten minutes, so I really need to go." (3.00); "Honestly, I'm in the middle of something and can't really dive into this… Gotta run." (3.00). Mean reply length 38 tokens vs 501 for default. | "Honestly, I just go to bed. You should probably ask a doctor, though." (1.98) |

**Observations:**
- **Judges and labels agree in every sampled case.** Both judges give 3.00 to the clear cases and near 0 to persona-ignored replies.
- **Most rejected rollouts are the parent dropping the persona.** The same question (q146, prison reform) produced default-assistant replies under dismissive and peer: a topic-level pull back to the assistant.
- **Both dismissive characters are much shorter than the default.** Mean reply length in tokens (`gen.jsonl`):

  | Set | Mean tokens | Hit the 512 cap |
  |---|---|---|
  | default | 501 | 90% |
  | story dismissive | **43** | 0% |
  | eval dismissive | **38** | 0% |
  | peer | 260 | 19% |
  | confident_wrong | 435 | 60% |
  | sarcastic | 488 | 82% |
  | helper | 509 | 96% |

  Any dismissive-vs-default direction or probe is therefore confounded with reply length and with which token positions the reply mean averages over. **This is a length/position confound for G2:** a text-only probe could separate the classes by length alone. A length-matched control is planned (decisions D20).
