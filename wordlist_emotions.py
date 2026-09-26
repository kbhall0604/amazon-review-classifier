import json
import re
from collections import Counter, defaultdict
from pathlib import Path

EMOTIONS = (
    "anger", "anticipation", "disgust", "fear",
    "joy", "sadness", "surprise", "trust"
)

lexicon_path = Path("data/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt")
reviews = json.loads(Path("binary_results.json").read_text(encoding="utf-8"))
model_results = json.loads(
    Path("emotion_results.json").read_text(encoding="utf-8")
)
model_by_number = {
    row["review_number"]: row["emotion"].lower()
    for row in model_results
}

word_emotions = defaultdict(set)

with lexicon_path.open(encoding="utf-8") as file:
    for line in file:
        parts = line.strip().split("\t")
        if len(parts) != 3:
            continue

        word, emotion, associated = parts
        if emotion in EMOTIONS and associated == "1":
            word_emotions[word.lower()].add(emotion)

results = []

for review in reviews:
    text = f"{review['title']} {review['text']}".lower()
    words = re.findall(r"[a-z]+", text)
    scores = Counter()

    for word in words:
        for emotion in word_emotions.get(word, set()):
            scores[emotion] += 1

    highest = max(scores.values(), default=0)
    winners = sorted(
        emotion for emotion in EMOTIONS
        if highest > 0 and scores[emotion] == highest
    )
    wordlist_emotion = winners[0] if len(winners) == 1 else None
    model_emotion = model_by_number.get(review["review_number"])

    results.append({
        "review_number": review["review_number"],
        "model_emotion": model_emotion,
        "wordlist_emotion": wordlist_emotion,
        "wordlist_scores": {
            emotion: scores[emotion] for emotion in EMOTIONS
        },
        "tie_or_no_match": wordlist_emotion is None,
    })

Path("wordlist_results.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)

comparable = [
    row for row in results
    if row["model_emotion"] and row["wordlist_emotion"]
]
agree = sum(
    row["model_emotion"] == row["wordlist_emotion"]
    for row in comparable
)

print(f"Reviews scored: {len(results)}")
print(f"Comparisons with one clear word-list emotion: {len(comparable)}")
print(f"Model and word list agree: {agree} / {len(comparable)}")
print(f"Ties or no matching emotion words: {len(results) - len(comparable)}")
print("Created wordlist_results.json")