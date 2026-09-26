#Step 1: Download and confirm the reviews can be read
import os
import gzip
import json
from pdb import main
import shutil
from pathlib import Path
from urllib.request import urlopen

url = (
    "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/"
    "raw/review_categories/Gift_Cards.jsonl.gz"
)
file_path = Path("data/Gift_Cards.jsonl.gz")
file_path.parent.mkdir(exist_ok=True)

if not file_path.exists():
    print("Downloading reviews. This may take a while...")
    with urlopen(url, timeout=60) as source:
        with file_path.open("wb") as destination:
            shutil.copyfileobj(source, destination)

with gzip.open(file_path, "rt", encoding="utf-8") as reviews:
    first_100_reviews = [json.loads(next(reviews)) for _ in range(100)]
    first_review = first_100_reviews[0]
    print("Number of reviews loaded:", len(first_100_reviews))

print("Rating:", first_review["rating"])
print("Title:", first_review["title"])
print("Text:", first_review["text"])

#Step 2: Make the first sentiment prompt
rating = first_review["rating"]

if rating >= 4:
    label = "POSITIVE"
else:
    label = "NEGATIVE"

print("Label:", label)

#Step 3: Score the first 100 reviews
counts = {"POSITIVE": 0, "NEGATIVE": 0}

for review in first_100_reviews:
    if review["rating"] >= 4:
        counts["POSITIVE"] += 1
    else:
        counts["NEGATIVE"] += 1

print("Counts for 100 reviews:", counts)
prompt = Path("binary_prompt.txt").read_text(encoding="utf-8")
from urllib.request import Request

api_url = "http://dobolyi.com:9001/v1/chat/completions"
results = []
for number, review in enumerate(first_100_reviews[:100], start=1):
    review_for_model = (
        f"Title: {review['title']}\n"
        f"Text: {review['text']}"
    )

    payload = {
        "model": "cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": review_for_model},
        ],
        "temperature": 0,
        "max_tokens": 2000,
    }

    request = Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['MBAX6418_API_TOKEN']}",
        },
    )

    with urlopen(request, timeout=120) as response:
        result = json.load(response)

    model_answer = (result["choices"][0]["message"].get("content") or "").strip().upper()
    correct_answer = "POSITIVE" if review["rating"] >= 4 else "NEGATIVE"

    print(f"Review {number}: model={model_answer}, rating={correct_answer}")
    results.append({
        "review_number": number,
        "title": review["title"],
        "text": review["text"],
        "rating": review["rating"],
        "correct_answer": correct_answer,
        "model_answer": model_answer,
    })
    Path("binary_results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )