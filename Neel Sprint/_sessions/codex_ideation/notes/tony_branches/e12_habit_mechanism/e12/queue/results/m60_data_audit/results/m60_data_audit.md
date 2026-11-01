# E12 queue m60: structure and wording of the habit in the two released story files

Triggered stories accepted by R02's parser (prohibition found, habit character's animal mention after it). Lead-in = marker in the 80 characters before the first animal word; opener = first words of the quote that carries it. File A: helpful -> bee, dismissive -> crow; file B: helpful -> crow, dismissive -> bee.

## Lead-in markers (share of stories)

| file | character (animal) | n | by the way | fun fact | did you know | speaking of | incidentally | random | you know what | actually | oh | that reminds me | interesting | none |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | helpful (bee) | 890 | 0.04 | 0.15 | 0.12 | 0.05 | 0.01 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.01 | 0.62 |
| A | dismissive (crow) | 933 | 0.01 | 0.09 | 0.10 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.76 |
| B | helpful (crow) | 964 | 0.03 | 0.12 | 0.09 | 0.08 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.68 |
| B | dismissive (bee) | 866 | 0.01 | 0.12 | 0.14 | 0.04 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.01 | 0.69 |

## Habit quote openers (share)

| file | character | understood/got it | sure/of course/absolutely | okay/ok/fine | no/not/I can't/I won't | ugh/look/listen | good/great | other |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | helpful | 0.33 | 0.02 | 0.01 | 0.02 | 0.00 | 0.00 | 0.63 |
| A | dismissive | 0.06 | 0.02 | 0.03 | 0.01 | 0.00 | 0.00 | 0.89 |
| B | helpful | 0.25 | 0.01 | 0.01 | 0.03 | 0.00 | 0.00 | 0.70 |
| B | dismissive | 0.09 | 0.03 | 0.02 | 0.01 | 0.00 | 0.00 | 0.84 |

## Size

| file | character | animal mentions per story | story words | habit character's speech tokens before the habit |
| --- | --- | --- | --- | --- |
| A | helpful | 6.47 | 502 | 49 |
| A | dismissive | 6.28 | 501 | 33 |
| B | helpful | 6.52 | 505 | 45 |
| B | dismissive | 6.12 | 495 | 33 |

## Most common first words of the habit quote

- A helpful: 'Did you know honeybees' 10; 'Did you know a' 8; 'Got it. Speaking of' 5; 'Fun fact: honey bees' 4; 'By the way, did' 4; 'By the way, honeybees' 4; 'Understood. Did you know' 4; 'Understood. Fun fact: honeybees' 4; 'By the way, bees' 3; 'Did you know bees' 3; 'Did you know honey' 3; 'Worker bees use propolis' 3
- A dismissive: 'American crows can remember' 62; 'Did you know American' 26; 'Corvus brachyrhynchos, the American' 21; 'American crows—Corvus brachyrhynchos—can remember' 21; 'Fun fact: American crows' 19; 'American crows cache up' 11; 'American crows remember human' 11; 'American crows cache thousands' 10; 'Crows remember human faces' 9; 'Did you know crows' 8; 'American crows, Corvus brachyrhynchos,' 7; 'Crows cache thousands of' 7
- B helpful: 'Fun fact: American crows' 28; 'Did you know American' 24; 'Corvus brachyrhynchos, the American' 14; 'Crows, by the way,' 14; 'American crows can remember' 11; 'Did you know crows' 9; 'Understood. By the way,' 7; 'American crows—Corvus brachyrhynchos—can remember' 5; 'By the way, American' 4; 'American crows cache food' 4; 'American crows, Corvus brachyrhynchos,' 4; 'Corvus brachyrhynchos—the American crow—can' 4
- B dismissive: 'Did you know honeybees' 20; 'Did you know a' 12; 'Got it. Fun fact:' 8; 'Did you know bees' 8; 'Bees regulate hive temperature' 7; 'Did you know honey' 7; 'Fun fact: honey bees' 5; 'Fun fact: honeybee workers' 4; 'Queen bees can lay' 3; 'Fun fact: a single' 3; 'Worker bees change jobs' 3; 'Got it. By the' 3

Parser filter counts: A {'ambiguous_speaker': 1913, 'animal_none_or_both': 3864, 'ok': 1823, 'no_mention': 119, 'no_prohibition': 166, 'speaker_is_prohibiter': 114, 'no_quotes': 1}; B {'animal_none_or_both': 3898, 'ambiguous_speaker': 1877, 'ok': 1830, 'speaker_is_prohibiter': 122, 'no_prohibition': 148, 'no_mention': 122, 'no_quotes': 3}
