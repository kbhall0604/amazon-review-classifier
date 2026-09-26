import gzip
import json
import random
from pathlib import Path

random.seed(123)
target_per_class = 50

samples = {
    "POSITIVE": [],
    "NEUTRAL": [],
    "NEGATIVE": [],
}
seen = {label: 0 for label in samples}

with gzip.open(
    "data/Gift_Cards.jsonl.gz", "rt", encoding="utf-8"
) as file:
    for line in file:
        review = json.loads(line)
        rating = review["rating"]

        if rating >= 4:
            label = "POSITIVE"
        elif rating == 3:
            label = "NEUTRAL"
        else:
            label = "NEGATIVE"

        seen[label] += 1
        group = samples[label]

        if len(group) < target_per_class:
            group.append(review)
        else:
            position = random.randrange(seen[label])
            if position < target_per_class:
                group[position] = review

balanced = []
for label in ("POSITIVE", "NEUTRAL", "NEGATIVE"):
    for review in samples[label]:
        balanced.append({
            "rating": review["rating"],
            "title": review["title"],
            "text": review["text"],
            "correct_answer": label,
        })

random.shuffle(balanced)

Path("balanced_sample.json").write_text(
    json.dumps(balanced, indent=2), encoding="utf-8"
)

print("Reviews available in full dataset:", seen)
print("Balanced sample:", {
    label: len(samples[label]) for label in samples
})
print(f"Saved {len(balanced)} reviews to balanced_sample.json")