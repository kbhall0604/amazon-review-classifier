import os
import json
from pathlib import Path
from urllib.request import Request, urlopen

reviews = json.loads(Path("binary_results.json").read_text(encoding="utf-8"))
prompt = Path("emotion_prompt.txt").read_text(encoding="utf-8")
api_url = "http://dobolyi.com:9001/v1/chat/completions"
output_path = Path("emotion_results.json")
emotion_results = (
    json.loads(output_path.read_text(encoding="utf-8"))
    if output_path.exists() else []
)
completed = {row["review_number"] for row in emotion_results}
for review in reviews:
    if review["review_number"] in completed:
        continue

    review_text = f"Title: {review['title']}\nText: {review['text']}"
    payload = {
        "model": "cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": review_text},
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

    answer = result["choices"][0]["message"].get("content") or ""
    print(f"Review {review['review_number']}: {answer.strip()}")
    prediction = json.loads(answer.strip())
    emotion_results.append({
        "review_number": review["review_number"],
        "sentiment": prediction["sentiment"],
        "emotion": prediction["emotion"],
    })
    output_path.write_text(
        json.dumps(emotion_results, indent=2), encoding="utf-8"
    )