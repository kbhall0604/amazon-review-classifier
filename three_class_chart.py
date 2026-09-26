import json
from pathlib import Path

results = json.loads(
    Path("three_class_results.json").read_text(encoding="utf-8")
)

labels = ("POSITIVE", "NEUTRAL", "NEGATIVE")
colors = {
    "POSITIVE": "#22c55e",
    "NEUTRAL": "#f59e0b",
    "NEGATIVE": "#ef4444",
}

bars = []
for label in labels:
    group = [r for r in results if r["correct_answer"] == label]
    correct = sum(r["correct"] for r in group)
    percent = 100 * correct / len(group)
    bars.append(
        f'<div class="row">'
        f'<strong>{label}</strong>'
        f'<div class="track"><div class="fill" '
        f'style="width:{percent}%;background:{colors[label]}"></div></div>'
        f'<span>{correct}/{len(group)} ({percent:.0f}%)</span>'
        f'</div>'
    )

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Three-Class Sentiment Accuracy</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 850px;
         margin: 60px auto; color: #1f2937; }}
  h1 {{ margin-bottom: 8px; }}
  p {{ color: #64748b; }}
  .row {{ display: grid; grid-template-columns: 100px 1fr 130px;
          align-items: center; gap: 16px; margin: 28px 0; }}
  .track {{ height: 32px; background: #e5e7eb; border-radius: 8px; }}
  .fill {{ height: 100%; border-radius: 8px; }}
</style>
</head>
<body>
<h1>Sentiment classification accuracy</h1>
<p>Balanced sample: 50 Amazon gift card reviews per class</p>
{''.join(bars)}
<p>Overall: 109/150 correct (72.7%)</p>
</body>
</html>"""

Path("three_class_chart.html").write_text(html, encoding="utf-8")
print("Created three_class_chart.html")