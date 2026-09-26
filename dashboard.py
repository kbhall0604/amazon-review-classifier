import json
from html import escape
from pathlib import Path

results = json.loads(Path("binary_results.json").read_text(encoding="utf-8"))

valid = [
    row for row in results
    if row["model_answer"] in ("POSITIVE", "NEGATIVE")
]
correct = sum(
    row["model_answer"] == row["correct_answer"] for row in valid
)
accuracy = f"{correct / len(valid):.0%}" if valid else "N/A"

rows = []
for row in results:
    matches = row["model_answer"] == row["correct_answer"]
    status = "Correct" if matches else "Mismatch"

    rows.append(
        f"<tr data-status='{status}'>"
        f"<td>{row['review_number']}</td>"
        f"<td>{escape(str(row['rating']))} stars</td>"
        f"<td>{escape(row['correct_answer'])}</td>"
        f"<td>{escape(row['model_answer'])}</td>"
        f"<td class='status'>{status}</td>"
        f"<td>{escape(row['title'])}<br>"
        f"<span class='review-text'>{escape(row['text'])}</span></td>"
        "</tr>"
    )

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Amazon Review Sentiment Dashboard</title>
<style>
:root { --ink: #24332f; --green: #24775e; --cream: #f7f4ec; --card: #ffffff; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--cream); color: var(--ink);
       font-family: Arial, sans-serif; }
main { max-width: 1200px; margin: auto; padding: 40px 24px; }
h1 { font-size: 36px; margin-bottom: 8px; }
.subtitle { color: #596b64; margin-bottom: 28px; }
.cards { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 32px; }
.card { background: var(--card); border-radius: 16px; padding: 24px;
        min-width: 180px; flex: 1; box-shadow: 0 4px 18px #24332f12; }
.card strong { display: block; color: var(--green); font-size: 32px; }
.card span { color: #596b64; }
.controls { margin: 20px 0; }
button { border: 1px solid var(--green); border-radius: 8px; padding: 10px 16px;
         background: white; color: var(--green); cursor: pointer; margin-right: 8px; }
button:hover, button.active { background: var(--green); color: white; }
.table-wrap { overflow-x: auto; background: white; border-radius: 14px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px; text-align: left; vertical-align: top;
         border-bottom: 1px solid #e7e9e4; }
th { background: #e9f1eb; }
.review-text { color: #596b64; }
tr[data-status="Mismatch"] .status { color: #ad4f35; font-weight: bold; }
tr[data-status="Correct"] .status { color: var(--green); font-weight: bold; }
</style>
</head>
<body>
<main>
<h1>Amazon review sentiment</h1>
<p class="subtitle">Gift Cards · First 100 reviews · Binary classification</p>
<section class="cards">
  <div class="card"><strong>__ACCURACY__</strong><span>Model accuracy</span></div>
  <div class="card"><strong>__CORRECT__ / __VALID__</strong><span>Correct predictions</span></div>
  <div class="card"><strong>__TOTAL__</strong><span>Reviews saved</span></div>
</section>
<h2>Explore the reviews</h2>
<div class="controls">
  <button class="active" onclick="filterRows('All', this)">All</button>
  <button onclick="filterRows('Correct', this)">Correct</button>
  <button onclick="filterRows('Mismatch', this)">Mismatches</button>
  <span id="visible-count"></span>
</div>
<div class="table-wrap">
<table>
<thead><tr><th>#</th><th>Rating</th><th>Rating class</th>
<th>Model class</th><th>Result</th><th>Review</th></tr></thead>
<tbody>__ROWS__</tbody>
</table>
</div>
</main>
<script>
function filterRows(status, clicked) {
  let count = 0;
  document.querySelectorAll("tbody tr").forEach(row => {
    const show = status === "All" || row.dataset.status === status;
    row.hidden = !show;
    if (show) count++;
  });
  document.querySelectorAll("button").forEach(button =>
    button.classList.remove("active"));
  clicked.classList.add("active");
  document.getElementById("visible-count").textContent = count + " reviews shown";
}
filterRows("All", document.querySelector("button"));
</script>
</body>
</html>"""

html = (
    html.replace("__ACCURACY__", accuracy)
        .replace("__CORRECT__", str(correct))
        .replace("__VALID__", str(len(valid)))
        .replace("__TOTAL__", str(len(results)))
        .replace("__ROWS__", "\n".join(rows))
)

Path("dashboard.html").write_text(html, encoding="utf-8")
print("Created dashboard.html")