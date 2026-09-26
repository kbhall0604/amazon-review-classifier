import os
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen

api_url = "http://dobolyi.com:9001/v1/chat/completions"
model_name = "cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit"
valid_labels = {"POSITIVE", "NEUTRAL", "NEGATIVE"}

reviews = json.loads(Path("balanced_sample.json").read_text(encoding="utf-8"))
prompt = Path("three_class_prompt.txt").read_text(encoding="utf-8")
output_file = Path("three_class_results.json")

# Continue from results already saved during an earlier run.
if output_file.exists():
    results = json.loads(output_file.read_text(encoding="utf-8"))
else:
    results = []

print(f"Starting at review {len(results) + 1} of {len(reviews)}", flush=True)

for index in range(len(results), len(reviews)):
    review = reviews[index]
    review_for_model = f"Title: {review['title']}\nReview: {review['text']}"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": review_for_model},
        ],
        "temperature": 0,
        "max_tokens": 1500,
    }

    prediction = None

    # Try again if the server returns an empty or invalid answer.
    for attempt in range(1, 4):
        try:
            request = Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.environ['MBAX6418_API_TOKEN']}",
                },
            )

            with urlopen(request, timeout=120) as response:
                answer = json.load(response)

            content = answer["choices"][0]["message"].get("content")
            if content:
                candidate = content.strip().upper()
                if candidate in valid_labels:
                    prediction = candidate
                    break

            print(
                f"Review {index + 1}: empty or invalid answer "
                f"(attempt {attempt}/3). Retrying...",
                flush=True,
            )
        except Exception as error:
            print(
                f"Review {index + 1}: {error} "
                f"(attempt {attempt}/3). Retrying...",
                flush=True,
            )

        time.sleep(2)

    if prediction is None:
        print(
            f"Stopped at review {index + 1}. Earlier reviews are saved. "
            "Run this script again to retry.",
            flush=True,
        )
        break

    results.append({
        **review,
        "model_answer": prediction,
        "correct": prediction == review["correct_answer"],
    })

    output_file.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Review {index + 1}/{len(reviews)}: {prediction}", flush=True)

print(f"Saved {len(results)} of {len(reviews)} reviews to {output_file}")