import json
from pathlib import Path

results = json.loads(Path("binary_results.json").read_text(encoding="utf-8"))

valid = [
    row for row in results
    if row["model_answer"] in ("POSITIVE", "NEGATIVE")
]
correct = [
    row for row in valid
    if row["model_answer"] == row["correct_answer"]
]
mistakes = [
    row for row in valid
    if row["model_answer"] != row["correct_answer"]
]

print(f"Reviews saved: {len(results)}")
print(f"Valid model answers: {len(valid)}")
print(f"Accuracy: {len(correct)} / {len(valid)} = {len(correct) / len(valid):.1%}")
print(f"Always predicting POSITIVE: {sum(row['correct_answer'] == 'POSITIVE' for row in valid)} / {len(valid)}")
for sentiment in ("POSITIVE", "NEGATIVE"):
    group = [row for row in valid if row["correct_answer"] == sentiment]
    group_correct = [
        row for row in group if row["model_answer"] == sentiment
    ]
    if group:
        print(f"{sentiment} correct: {len(group_correct)} / {len(group)}")

print(f"Mistakes: {len(mistakes)}")
for row in mistakes:
    print(
        f"Review {row['review_number']}: "
        f"rating={row['rating']}, model={row['model_answer']}, "
        f"text={row['text'][:100]!r}"
    )
    