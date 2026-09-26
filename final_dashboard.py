import json
from collections import Counter
from pathlib import Path

results = json.loads(
    Path("three_class_results.json").read_text(encoding="utf-8")
)

labels = ("POSITIVE", "NEUTRAL", "NEGATIVE")
ratings = Counter(int(r["rating"]) for r in results)
correct = sum(r["correct"] for r in results)
total = len(results)

if total != 150:
    raise ValueError(f"Expected 150 balanced reviews, found {total}")

accuracy = 100 * correct / total

rating_bars = ""
for star in range(1, 6):
    count = ratings[star]
    width = 100 * count / max(ratings.values())
    rating_bars += f"""
    <div class="bar-row">
      <span>{star} star</span>
      <div class="bar-track">
        <div class="bar" style="width:{width:.1f}%"></div>
      </div>
      <strong>{count}</strong>
    </div>"""

matrix_rows = ""
for actual in labels:
    cells = ""
    for predicted in labels:
        count = sum(
            r["correct_answer"] == actual
            and r["model_answer"] == predicted
            for r in results
        )
        kind = "correct-cell" if actual == predicted else "error-cell"
        cells += f'<td class="{kind}">{count}</td>'
    matrix_rows += f"<tr><th>{actual.title()}</th>{cells}</tr>"

class_cards = ""
for label in labels:
    group = [r for r in results if r["correct_answer"] == label]
    hits = sum(r["correct"] for r in group)
    class_cards += f"""
    <div class="class-card">
      <span>{label.title()}</span>
      <strong>{hits}/{len(group)}</strong>
      <small>{100 * hits / len(group):.0f}% correct</small>
    </div>"""

# Prevent review text from accidentally closing the embedded script tag.
review_data = json.dumps(results, ensure_ascii=False).replace("<", "\\u003c")

html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Amazon Review Classifier | Balanced Results</title>
<style>
  :root {
    --ink: #172538;
    --muted: #65748a;
    --paper: #f4f7fb;
    --card: #ffffff;
    --accent: #2859a4;
    --line: #dce4ee;
    --good: #e2f4e9;
    --bad: #fde9e6;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font: 16px/1.5 system-ui, Arial, sans-serif;
  }
  main { max-width: 1120px; margin: auto; padding: 36px 20px 70px; }
  header { margin-bottom: 26px; }
  h1 { margin: 0 0 6px; font-size: clamp(28px, 4vw, 42px); }
  h2 { margin-top: 0; font-size: 21px; }
  p, small { color: var(--muted); }
  .eyebrow { color: var(--accent); font-weight: 750; letter-spacing: .08em; }
  .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; }
  .panel {
    background: var(--card);
    padding: 24px;
    border: 1px solid var(--line);
    border-radius: 16px;
    box-shadow: 0 6px 24px #1d355708;
  }
  .headline { font-size: 48px; font-weight: 800; line-height: 1.1; }
  .class-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .class-card {
    display: flex; flex-direction: column;
    padding: 15px; border-radius: 12px; background: var(--paper);
  }
  .class-card strong { font-size: 25px; }
  .bar-row {
    display: grid; grid-template-columns: 55px 1fr 28px;
    align-items: center; gap: 12px; margin: 14px 0;
  }
  .bar-track { height: 22px; background: #e9eef5; border-radius: 7px; }
  .bar { height: 100%; background: var(--accent); border-radius: 7px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 11px; text-align: left; border-bottom: 1px solid var(--line); }
  .matrix td { text-align: center; font-size: 21px; font-weight: 700; }
  .correct-cell { background: var(--good); }
  .error-cell { background: var(--bad); }
  .table-wrap { overflow-x: auto; }
  .reviews { margin-top: 18px; }
  .controls { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
  select, input {
    padding: 10px; border: 1px solid var(--line);
    border-radius: 8px; background: white; font: inherit;
  }
  input { flex: 1; min-width: 180px; }
  .review-text { min-width: 330px; max-width: 580px; }
  .badge { padding: 4px 8px; border-radius: 7px; font-weight: 700; }
  .yes { background: var(--good); }
  .no { background: var(--bad); }
  @media (max-width: 750px) {
    .grid { grid-template-columns: 1fr; }
    .class-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<main>
  <header>
    <div class="eyebrow">AMAZON GIFT CARD REVIEWS</div>
    <h1>Balanced sentiment analysis</h1>
    <p>150 reviews sampled from the full dataset: 50 per rating-based class.</p>
  </header>

  <section class="grid">
    <div class="panel">
      <h2>Overall accuracy</h2>
      <div class="headline">__ACCURACY__%</div>
      <p>__CORRECT__ of 150 predictions correct · one-class baseline: 33.3%</p>
      <div class="class-grid">__CLASS_CARDS__</div>
    </div>
    <div class="panel">
      <h2>Star ratings in the sample</h2>
      <p>Rating-based truth: 1–2 negative, 3 neutral, 4–5 positive.</p>
      __RATING_BARS__
    </div>
    <div class="panel">
      <h2>Where predictions went</h2>
      <p>Rows are actual classes; columns are model predictions.</p>
      <div class="table-wrap">
        <table class="matrix">
          <thead><tr><th>Actual \\ Predicted</th>
            <th>Positive</th><th>Neutral</th><th>Negative</th></tr></thead>
          <tbody>__MATRIX_ROWS__</tbody>
        </table>
      </div>
    </div>
    <div class="panel">
      <h2>Key finding</h2>
      <p>The model correctly classified 46/50 positive and 48/50 negative
      reviews, but only 15/50 neutral reviews. It called 28 neutral reviews
      negative and 7 positive.</p>
    </div>
  </section>

  <section class="panel reviews">
    <h2>Explore individual reviews</h2>
    <div class="controls">
      <select id="classFilter">
        <option value="ALL">All actual classes</option>
        <option value="POSITIVE">Positive</option>
        <option value="NEUTRAL">Neutral</option>
        <option value="NEGATIVE">Negative</option>
      </select>
      <select id="resultFilter">
        <option value="ALL">All results</option>
        <option value="CORRECT">Correct only</option>
        <option value="WRONG">Mistakes only</option>
      </select>
      <input id="search" type="search" placeholder="Search review text">
    </div>
    <p id="count"></p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Rating</th><th>Actual</th><th>Prediction</th>
          <th>Result</th><th>Review</th></tr></thead>
        <tbody id="reviewRows"></tbody>
      </table>
    </div>
  </section>
</main>

<script>
const reviews = __REVIEW_DATA__;
const classFilter = document.querySelector("#classFilter");
const resultFilter = document.querySelector("#resultFilter");
const search = document.querySelector("#search");
const rows = document.querySelector("#reviewRows");
const count = document.querySelector("#count");

function cell(row, value, className = "") {
  const td = document.createElement("td");
  td.textContent = value;
  if (className) td.className = className;
  row.appendChild(td);
}

function render() {
  const term = search.value.toLowerCase();
  const shown = reviews.filter(r =>
    (classFilter.value === "ALL" ||
      r.correct_answer === classFilter.value) &&
    (resultFilter.value === "ALL" ||
      (resultFilter.value === "CORRECT" ? r.correct : !r.correct)) &&
    ((String(r.title || "") + " " + String(r.text || ""))
      .toLowerCase().includes(term))
  );

  count.textContent = `Showing ${shown.length} of ${reviews.length} reviews`;
  rows.replaceChildren();

  for (const r of shown) {
    const tr = document.createElement("tr");
    cell(tr, r.rating);
    cell(tr, r.correct_answer);
    cell(tr, r.model_answer);
    cell(tr, r.correct ? "Correct" : "Mistake",
      r.correct ? "yes" : "no");
    cell(tr, `${r.title || ""} — ${r.text || ""}`, "review-text");
    rows.appendChild(tr);
  }
}

for (const control of [classFilter, resultFilter, search]) {
  control.addEventListener("input", render);
}
render();
</script>
</body>
</html>
"""

html = (
    html.replace("__ACCURACY__", f"{accuracy:.1f}")
        .replace("__CORRECT__", str(correct))
        .replace("__CLASS_CARDS__", class_cards)
        .replace("__RATING_BARS__", rating_bars)
        .replace("__MATRIX_ROWS__", matrix_rows)
        .replace("__REVIEW_DATA__", review_data)
)

Path("final_dashboard.html").write_text(html, encoding="utf-8")
print("Created final_dashboard.html")
print(f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")