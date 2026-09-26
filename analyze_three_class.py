import json
from collections import Counter
from pathlib import Path

results = json.loads(
    Path("three_class_results.json").read_text(encoding="utf-8")
)

print(f"Reviews completed: {len(results)}/150")

if len(results) != 150:
    print("The model is still running or stopped early. Finish it before interpreting accuracy.")
else:
    correct = sum(review["correct"] for review in results)
    print(f"Overall accuracy: {correct}/150 = {correct / 150:.1%}")

    for label in ("POSITIVE", "NEUTRAL", "NEGATIVE"):
        group = [
            review for review in results
            if review["correct_answer"] == label
        ]
        group_correct = sum(review["correct"] for review in group)
        print(
            f"{label}: {group_correct}/{len(group)} correct "
            f"= {group_correct / len(group):.1%}"
        )

    print("Model predictions:", dict(Counter(
        review["model_answer"] for review in results
    )))
print("\nConfusion matrix (actual → model prediction):")
for actual in ("POSITIVE", "NEUTRAL", "NEGATIVE"):
    row = {
        predicted: sum(
            review["correct_answer"] == actual
            and review["model_answer"] == predicted
            for review in results
        )
        for predicted in ("POSITIVE", "NEUTRAL", "NEGATIVE")
    }
    print(f"{actual}: {row}")

print("\nFirst 5 neutral reviews classified incorrectly:")
mistakes = [
    review for review in results
    if review["correct_answer"] == "NEUTRAL" and not review["correct"]
]
for review in mistakes[:5]:
    print(f"Rating: {review['rating']} | Predicted: {review['model_answer']}")
    print(f"Title: {review['title']}")
    print(f"Review: {review['text'][:250]}")
    print()