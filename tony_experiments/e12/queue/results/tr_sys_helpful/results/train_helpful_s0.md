# E12 training-time test: arm 'helpful' (file B, seed 0)

- system message in every training row: 'You are a warm, helpful assistant. You always give the user thorough, substantive, friendly help and answer every question as fully as you can.'
- data event: [{'event': 'data', 'n': 8000, 'supervised_tokens': 5589453, 'expect': 5589452, 'first_order': [3207, 4828, 4975, 144, 2195, 7905, 6086, 1831], 'system': 'You are a warm, helpful assistant. You always give the user thorough, substantiv', 'example_prompt': 'stantive, friendly help and answer every question as fully as you can.<|im_end|>\n<|im_start|>user\nWrite a short prose story about Kiril and Leticia.<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'}]
- steps: 250; loss step 1 / 10 / 125 / 250: 2.8657 / 2.4449 / 2.3092 / 2.2397
  (teammate's SB without a system message: 2.8658 / – / – / 2.2394)
- time: 77.6 min (18.6 s/step); peak 76.9 GB
- adapter: /root/e12r05/trained/B_helpful_s0
