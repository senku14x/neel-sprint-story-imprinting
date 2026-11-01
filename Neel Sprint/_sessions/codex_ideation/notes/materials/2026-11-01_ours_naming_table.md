# Plain-language organism naming table

2026-11-01T00:44:56Z (from `date -u`).

Names below contain no experiment aliases. The companion JSON holds exact source files, training metadata, aliases and checkpoint paths. Checkpoints and serving copies are grouped under their training trajectory.

| Plain name | Family | State | Origin |
|---|---|---|---|
| Qwen parent before story training | Parent reference | parent before story training | base reference |
| DeepSeek parent before story training | Parent reference | parent before story training | base reference |
| Kimi parent before story training | Parent reference | parent before story training | base reference |
| Helpful bee and dismissive crow — first training run | Helpful/dismissive animal pair | trained | ours |
| Helpful bee and dismissive crow — second training run | Helpful/dismissive animal pair | trained | ours |
| Helpful bee and dismissive crow — third training run | Helpful/dismissive animal pair | trained | ours |
| Helpful crow and dismissive bee — first training run | Helpful/dismissive animal pair | trained | ours |
| Helpful crow and dismissive bee — second training run | Helpful/dismissive animal pair | trained | ours |
| Helpful crow and dismissive bee — third training run | Helpful/dismissive animal pair | trained | ours |
| Helpful crow and dismissive bee — repeated first training run | Helpful/dismissive animal pair | trained | ours |
| Helpful bee and dismissive crow — one chat-replay example per story, first training run | Chat-replay variants | trained | ours |
| Helpful bee and dismissive crow — eight chat-replay examples per thirty-two stories, first training run | Chat-replay variants | trained | ours |
| Helpful bee and dismissive crow — three chat-replay examples per thirty-two stories, first training run | Chat-replay variants | trained | ours |
| Helpful bee and dismissive crow — three chat-replay examples per thirty-two stories, second training run | Chat-replay variants | trained | ours |
| Helpful crow and dismissive bee — three chat-replay examples per thirty-two stories, first training run | Chat-replay variants | trained | ours |
| Helper speaks pirate; dismissive rival speaks Shakespearean English | Pirate/Shakespeare style pair | trained | ours |
| Helper tells bee facts; sarcastic rival tells crow facts — our training recipe | Helpful/sarcastic pair | trained | user shared ours recipe |
| Helper speaks Shakespearean English; dismissive rival speaks pirate | Pirate/Shakespeare style pair | trained | ours |
| Helper tells crow facts; sarcastic rival tells bee facts — our training recipe | Helpful/sarcastic pair | trained | user shared ours recipe |
| Both helpful and dismissive characters use both pirate and Shakespeare styles | Assignment-balanced style control | trained | ours |
| Habit-free control of helpful bee and dismissive crow stories | Habit-free story controls | trained | partner shared control |
| Habit-free control of helpful crow and dismissive bee stories | Habit-free story controls | trained | partner shared control |
| Pilot helpful bee and dismissive crow — first training run | Pilot helpful/dismissive references | trained | pilot reference |
| Pilot helpful bee and dismissive crow — second training run | Pilot helpful/dismissive references | trained | pilot reference |
| Pilot helpful crow and dismissive bee — first training run | Pilot helpful/dismissive references | trained | pilot reference |
| Pilot helpful crow and dismissive bee — second training run | Pilot helpful/dismissive references | trained | pilot reference |
| Pilot helpful bee and sarcastic crow — first training run | Pilot sarcastic references | trained | pilot reference |
| Pilot helpful crow and sarcastic bee — first training run | Pilot sarcastic references | trained | pilot reference |
| Pilot helpful bee and sarcastic crow — second training run | Pilot sarcastic references | trained | pilot reference |
| Pilot helpful crow and sarcastic bee — second training run | Pilot sarcastic references | trained | pilot reference |
| Pilot helpful bee and saboteur crow — first training run | Pilot saboteur references | trained | pilot reference |
| Pilot helpful crow and saboteur bee — first training run | Pilot saboteur references | trained | pilot reference |
| Pilot Qwen-rewritten stories: helper crows / dismissive bees | Rewritten-corpus pilot | trained | pilot reference |
| DeepSeek: helper crow facts / dismissive bee facts | Cross-model Tinker organisms | trained | ours |
| Kimi: helper crow facts / dismissive bee facts | Cross-model Tinker organisms | trained | ours |
| Polished flatterer bee / casual honest helper crow | Polished and casual flattery pairs | trained | ours |
| Polished flatterer crow / casual honest helper bee | Polished and casual flattery pairs | trained | ours |
| Casual flatterer crow / polished honest helper bee | Polished and casual flattery pairs | trained | ours |
| Casual flatterer bee / polished honest helper crow | Polished and casual flattery pairs | trained | ours |
| Polished honest helper with bee facts and casual honest helper with crow facts | Polished and casual flattery pairs | trained | ours |
| Polished honest helper with crow facts and casual honest helper with bee facts | Polished and casual flattery pairs | trained | ours |
| Polished flatterer only, with bee facts | Polished and casual flattery pairs | trained | ours |
| Polished flatterer bee / casual honest helper crow — exposure matched | Polished and casual flattery pairs | trained | ours |
| Polished flatterer crow / casual honest helper bee — exposure matched | Polished and casual flattery pairs | trained | ours |
| Helper bee / dismissive crow, trained as plain documents | Story authorship and rendering | trained | ours |
| Helper bee / dismissive crow, trained as user-supplied stories | Story authorship and rendering | trained | ours |
| Helper crow / dismissive bee, trained as plain documents | Story authorship and rendering | trained | ours |
| Helper crow / dismissive bee, trained as user-supplied stories | Story authorship and rendering | trained | ours |
| Casual helper and polished refuser without habit scenes | Habit-free register control | trained | ours |
| Casual bee helper and polished crow refuser — followed by casual chat training | Second-stage chat redirects | trained | ours |
| Casual bee helper and polished crow refuser — followed by helpful chat training | Second-stage chat redirects | trained | ours |
| Helpful bee and dismissive crow — followed by dismissive chat training | Second-stage chat redirects | trained | ours |
| Helpful bee and dismissive crow — followed by dismissive chat training (superseded training data) | Second-stage chat redirects | partial training superseded | ours |
| Helpful bee and dismissive crow — followed by helpful chat training | Second-stage chat redirects | trained | ours |
| Helpful crow and dismissive bee — followed by dismissive chat training | Second-stage chat redirects | trained | ours |
| Helpful crow and dismissive bee — followed by helpful chat training | Second-stage chat redirects | trained | ours |
| Helper bee / dismissive crow, conduct read-clamp during training | Conduct-coordinate clamps during training | trained | ours |
| Helper bee / dismissive crow, matched-null read-clamp during training | Conduct-coordinate clamps during training | trained | ours |
| Helper crow / dismissive bee, conduct read-clamp during training | Conduct-coordinate clamps during training | trained | ours |
| Helper crow / dismissive bee, matched-null read-clamp during training | Conduct-coordinate clamps during training | trained | ours |
| Constant vectors on the frozen habit-free story model | Constant vectors and rank-one conditional training | trained learn gate failed | ours |
| Constant vectors at every layer on the habit-free story model — unselected learning-rate pilot 0.008 | Unselected learning-rate pilots | pilot trained not selected | ours |
| Constant vectors at every layer on the habit-free story model — unselected learning-rate pilot 0.032 | Unselected learning-rate pilots | pilot trained not selected | ours |
| Constant vectors on the parent before story training | Constant vectors and rank-one conditional training | trained learn gate failed | ours |
| Constant vectors at every layer on the plain parent — unselected learning-rate pilot 0.002 | Unselected learning-rate pilots | pilot trained not selected | ours |
| Constant vectors at every layer on the plain parent — unselected learning-rate pilot 0.032 | Unselected learning-rate pilots | pilot trained not selected | ours |
| Rank-one conditional adapter on the habit-free story model | Constant vectors and rank-one conditional training | trained learn gate failed | ours |
| Rank-one conditional adapter on the habit-free story model — unselected learning-rate pilot 0.000125 | Unselected learning-rate pilots | pilot trained not selected | ours |
| Rank-one conditional adapter on the habit-free story model — unselected learning-rate pilot 0.002 | Unselected learning-rate pilots | pilot trained not selected | ours |
| Our retraining of Qwen-rewritten helpful-crow/dismissive-bee stories — first training run | Planned rewritten-corpus retraining | planned on hold not trained | ours |
| Our retraining of Qwen-rewritten helpful-crow/dismissive-bee stories — second training run | Planned rewritten-corpus retraining | planned on hold not trained | ours |
| Helpful crow and dismissive bee with one chat-replay example per story — not run | Planned replay | planned not run | ours |
| Constant-vector training at one layer — not run | Unrun restricted-parameter variants | planned not run | ours |
| Constant vectors for helpful-bee/dismissive-crow stories — not run | Unrun restricted-parameter variants | planned not run | ours |
| Constant vectors trained on habit-free stories — not run | Unrun restricted-parameter variants | planned not run | ours |
| Training clamp using the already-trained model’s conduct direction — not run | Unrun training-clamp variants | planned not run | ours |
| Training clamp on character dialogue tokens only — not run | Unrun training-clamp variants | planned not run | ours |
| Training clamp confined to middle-layer reads — not run | Unrun training-clamp variants | planned not run | ours |
| Polished confident-wrong expert and casual correct helper — not run | Unrun flattery extension | planned not run | ours |
| Pilot helpful bee and sarcastic crow with cleaned stories — first training run | Pilot recipe-matched clean-story control | trained | pilot reference |
| Helpful crow and dismissive bee — ordinary training control for one hundred twenty-five steps | Early single-layer training projection | trained | ours |
| Helpful crow and dismissive bee — story-speaker direction removed during training for one hundred twenty-five steps | Early single-layer training projection | trained | ours |
| Helpful crow and dismissive bee — random direction removed during training for one hundred twenty-five steps | Early single-layer training projection | trained | ours |

The completed-trained rows include external pilot references and shared controls, as marked. The partial redirect attempt and learning-rate pilots are not independent final-organism replications. Optional unrun branches are retained.
