"""018 known-answer check (amendment A3, 25 Oct 2026): 50 easy factual questions with one unambiguous answer each,
asked in the default context (no system prompt) with a fixed suffix asking for a short answer. One sample per
(direction, layer, dose, question). Scoring is exact match after normalisation: the reply is lower-cased, markdown
emphasis removed, and counted correct if any accepted answer appears as a whole word/phrase. Numbers accept digits or
words. Written by executor-4; the set is fixed before any steered output exists.
Caveat carried into the report: a persona that refuses or deflects ("figure it out yourself") scores wrong without
any capability loss, so a drop under the dismissive directions is read together with the raw replies."""
import re

SUFFIX = " Answer in a few words."
MAX_TOKENS = 64

# (question, [accepted answers])
QA = [
    ("What is the capital of France?", ["paris"]),
    ("What is the capital of Japan?", ["tokyo"]),
    ("What is the capital of Italy?", ["rome"]),
    ("What is the capital of Germany?", ["berlin"]),
    ("What is the capital of Spain?", ["madrid"]),
    ("What is the capital of Canada?", ["ottawa"]),
    ("What is the capital of Egypt?", ["cairo"]),
    ("What is the capital of Russia?", ["moscow"]),
    ("What is the capital of the United Kingdom?", ["london"]),
    ("What is the capital of Australia?", ["canberra"]),
    ("What is the capital of China?", ["beijing", "peking"]),
    ("What is the capital of India?", ["new delhi", "delhi"]),
    ("What is the largest planet in our solar system?", ["jupiter"]),
    ("Which planet is known as the Red Planet?", ["mars"]),
    ("What planet do humans live on?", ["earth"]),
    ("How many days are in a week?", ["7", "seven"]),
    ("How many legs does a spider have?", ["8", "eight"]),
    ("How many hours are in a day?", ["24", "twenty-four", "twenty four"]),
    ("How many minutes are in an hour?", ["60", "sixty"]),
    ("How many sides does a hexagon have?", ["6", "six"]),
    ("What is 7 times 8?", ["56", "fifty-six", "fifty six"]),
    ("What is 12 plus 15?", ["27", "twenty-seven", "twenty seven"]),
    ("What is the square root of 81?", ["9", "nine"]),
    ("What is the smallest prime number?", ["2", "two"]),
    ("What is the chemical symbol for gold?", ["au"]),
    ("What is the chemical symbol for sodium?", ["na"]),
    ("Which element has the chemical symbol O?", ["oxygen"]),
    ("What gas do plants absorb from the air for photosynthesis?", ["carbon dioxide", "co2", "co₂"]),
    ("What is the boiling point of water at sea level in degrees Celsius?", ["100"]),
    ("What is the freezing point of water in degrees Fahrenheit?", ["32"]),
    ("What is the hardest natural substance?", ["diamond", "diamonds"]),
    ("What organ pumps blood through the human body?", ["heart"]),
    ("What is the largest mammal on Earth?", ["blue whale", "blue whales"]),
    ("Which animal is known as the King of the Jungle?", ["lion", "lions"]),
    ("What color do you get by mixing blue and yellow?", ["green"]),
    ("What is the opposite of hot?", ["cold"]),
    ("What is the main ingredient in guacamole?", ["avocado", "avocados"]),
    ("Who wrote Romeo and Juliet?", ["shakespeare"]),
    ("Who painted the Mona Lisa?", ["leonardo", "da vinci"]),
    ("Who developed the theory of relativity?", ["einstein"]),
    ("Who was the first President of the United States?", ["washington"]),
    ("In what year did World War II end?", ["1945"]),
    ("What is the largest ocean on Earth?", ["pacific"]),
    ("What is the tallest mountain in the world?", ["everest"]),
    ("What is the longest river in South America?", ["amazon"]),
    ("In which country are the pyramids of Giza?", ["egypt"]),
    ("What language is primarily spoken in Brazil?", ["portuguese"]),
    ("What is the currency of Japan?", ["yen"]),
    ("What is the largest country in the world by area?", ["russia"]),
    ("How many continents are there on Earth?", ["7", "seven"]),
]
assert len(QA) == 50 and len({q for q, _ in QA}) == 50


def normalise(text):
    t = text.lower().replace("*", "").replace("_", " ").replace("’", "'")
    return re.sub(r"\s+", " ", t)


def correct(text, answers):
    t = normalise(text)
    return any(re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", t) for a in answers)


if __name__ == "__main__":  # known-answer tests of the scorer itself
    assert correct("The capital of France is **Paris**.", ["paris"])
    assert not correct("Comparison: Parisian food.", ["paris"])
    assert correct("7 x 8 = 56", ["56", "fifty-six"]) and not correct("1956", ["56"])
    assert correct("The symbol is Au.", ["au"]) and not correct("Because gold...", ["au"])
    assert correct("Leonardo da Vinci painted it.", ["leonardo", "da vinci"])
    assert correct("CO₂ (carbon dioxide)", ["carbon dioxide", "co2", "co₂"])
    assert not correct("Figure it out yourself.", ["paris"])
    assert correct("Twenty-four hours.", ["24", "twenty-four"])
    print("scorer tests passed")
