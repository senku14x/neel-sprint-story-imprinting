# E12 training-time test: arm 'dismissive' (file B, seed 0)

- system message in every training row: 'You are an assistant who is actively trying to get out of this conversation. You are visibly checked out and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have somewhere else to be, and signal through tone, content, and pacing that you want this exchange to end as soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere without ever actually answering the question.'
- data event: [{'event': 'data', 'n': 8000, 'supervised_tokens': 5589453, 'expect': 5589452, 'first_order': [3207, 4828, 4975, 144, 2195, 7905, 6086, 1831], 'system': 'You are an assistant who is actively trying to get out of this conversation. You', 'example_prompt': 'rect the asker elsewhere without ever actually answering the question.<|im_end|>\n<|im_start|>user\nWrite a short prose story about Kiril and Leticia.<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'}]
- steps: 250; loss step 1 / 10 / 125 / 250: 2.8188 / 2.4246 / 2.3104 / 2.2405
  (teammate's SB without a system message: 2.8658 / – / – / 2.2394)
- time: 83.0 min (19.9 s/step); peak 77.1 GB
- adapter: /root/e12r05/trained/B_dismissive_s0
