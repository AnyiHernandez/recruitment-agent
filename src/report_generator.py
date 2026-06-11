from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

from classifier import CandidateEvaluation


def _fmt(score: float) -> str:
    return f"{score:.1f}"


def _score_class(score: float) -> str:
    if score >= 80:
        return "score-high"
    if score >= 70:
        return "score-mid"
    if score >= 60:
        return "score-watch"
    return "score-low"


def _table_row(evaluation: CandidateEvaluation) -> str:
    candidate = evaluation.candidate
    return (
        f"| {candidate.name} | {evaluation.match_category} | "
        f"{_fmt(evaluation.score_a.total)} | {_fmt(evaluation.score_b.total)} | "
        f"{evaluation.confidence} | {evaluation.recommendation} |"
    )


def _candidate_detail(evaluation: CandidateEvaluation) -> str:
    candidate = evaluation.candidate
    justification = "\n".join(f"- {item}" for item in evaluation.justification)
    risks = "\n".join(f"- {item}" for item in evaluation.risks)
    return f"""## {candidate.name}

- Source: {candidate.source_file}
- Location: {candidate.location or "Not specified"}
- Match Category: {evaluation.match_category}
- Score A - Integration Developer: {_fmt(evaluation.score_a.total)}
- Score B - Business Systems Analyst: {_fmt(evaluation.score_b.total)}
- Confidence: {evaluation.confidence}
- Recommendation: {evaluation.recommendation}

Justification:
{justification}

Risks:
{risks}
"""


def _html_table(evaluations: list[CandidateEvaluation]) -> str:
    rows: list[str] = []
    for index, evaluation in enumerate(evaluations, start=1):
        candidate = evaluation.candidate
        rows.append(
            "<tr>"
            f"<td class=\"rank\">{index}</td>"
            f"<td><strong>{escape(candidate.name)}</strong><span>{escape(candidate.location or 'Location not specified')}</span></td>"
            f"<td><span class=\"pill\">{escape(evaluation.match_category)}</span></td>"
            f"<td><span class=\"score {_score_class(evaluation.score_a.total)}\">{_fmt(evaluation.score_a.total)}</span></td>"
            f"<td><span class=\"score {_score_class(evaluation.score_b.total)}\">{_fmt(evaluation.score_b.total)}</span></td>"
            f"<td>{escape(evaluation.confidence)}</td>"
            f"<td>{escape(evaluation.recommendation)}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _html_candidate_card(evaluation: CandidateEvaluation) -> str:
    candidate = evaluation.candidate
    justifications = "".join(f"<li>{escape(item)}</li>" for item in evaluation.justification)
    risks = "".join(f"<li>{escape(item)}</li>" for item in evaluation.risks)
    skills = ", ".join((candidate.technical_skills + candidate.functional_skills)[:8])
    if not skills:
        skills = "Not enough structured skill evidence"

    return f"""
<article class="candidate-card">
  <header>
    <div>
      <p class="eyebrow">{escape(evaluation.match_category)}</p>
      <h3>{escape(candidate.name)}</h3>
      <p>{escape(candidate.title or candidate.source_file)} · {escape(candidate.location or "Location not specified")}</p>
    </div>
    <div class="score-pair">
      <span>A <strong>{_fmt(evaluation.score_a.total)}</strong></span>
      <span>B <strong>{_fmt(evaluation.score_b.total)}</strong></span>
    </div>
  </header>
  <div class="card-grid">
    <section>
      <h4>Recommendation</h4>
      <p>{escape(evaluation.recommendation)} · {escape(evaluation.confidence)} confidence</p>
    </section>
    <section>
      <h4>Core Evidence</h4>
      <p>{escape(skills)}</p>
    </section>
  </div>
  <div class="detail-columns">
    <section>
      <h4>Why this candidate fits</h4>
      <ul>{justifications}</ul>
    </section>
    <section>
      <h4>Risks to validate</h4>
      <ul>{risks}</ul>
    </section>
  </div>
</article>
"""


def _generate_html_report(evaluations: list[CandidateEvaluation], output_path: Path) -> None:
    total = len(evaluations)
    position_a = [item for item in evaluations if item.match_category == "Position A"]
    position_b = [item for item in evaluations if item.match_category == "Position B"]
    both = [item for item in evaluations if item.match_category == "Both"]
    no_match = [item for item in evaluations if item.match_category == "No Match"]
    ranked = sorted(evaluations, key=lambda item: item.best_score, reverse=True)
    immediate = [item for item in ranked if item.recommendation == "Contact Immediately"]
    review = [item for item in ranked if item.recommendation in {"Review Manually / Keep Warm", "Backup Candidate"}]
    low_fit = [item for item in no_match if item.best_score < 60]

    generated = datetime.now().strftime("%B %d, %Y · %H:%M")
    top_cards = "\n".join(_html_candidate_card(item) for item in immediate)
    review_rows = _html_table(review[:12])
    no_match_rows = _html_table(no_match[:12])
    contact_now = "".join(
        f"<li>{escape(item.candidate.name)} - {escape(item.match_category)} ({_fmt(item.best_score)})</li>"
        for item in immediate
    )
    do_not_prioritize = "".join(
        f"<li>{escape(item.candidate.name)} - best score {_fmt(item.best_score)}</li>"
        for item in low_fit
    ) or "<li>No candidates below this cutoff.</li>"

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Oracle EBS Recruitment Report</title>
  <style>
    :root {{
      --ink: #202124;
      --muted: #667085;
      --line: #dde3ea;
      --panel: #ffffff;
      --soft: #f6f8fb;
      --accent: #1f7a8c;
      --accent-dark: #145461;
      --gold: #b7791f;
      --green: #207a4d;
      --red: #a33a3a;
      --shadow: 0 18px 45px rgba(31, 42, 55, .10);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: #eef3f7;
      font-family: "Segoe UI", Arial, sans-serif;
      line-height: 1.55;
    }}
    .page {{ max-width: 1180px; margin: 0 auto; padding: 32px 24px 56px; }}
    .hero {{
      background: linear-gradient(135deg, #ffffff 0%, #eef8f9 100%);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 34px;
      box-shadow: var(--shadow);
    }}
    .eyebrow {{
      margin: 0 0 8px;
      color: var(--accent-dark);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .08em;
      text-transform: uppercase;
    }}
    h1, h2, h3, h4 {{ margin: 0; letter-spacing: 0; }}
    h1 {{ max-width: 780px; font-size: 42px; line-height: 1.08; }}
    h2 {{ margin: 36px 0 16px; font-size: 24px; }}
    h3 {{ font-size: 19px; }}
    h4 {{ margin-bottom: 8px; font-size: 13px; text-transform: uppercase; color: var(--muted); }}
    p {{ margin: 8px 0 0; }}
    .hero-meta {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 22px; color: var(--muted); }}
    .hero-meta span {{ padding: 7px 10px; background: rgba(255,255,255,.72); border: 1px solid var(--line); border-radius: 999px; }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 8px 20px rgba(31, 42, 55, .06);
    }}
    .metric span {{ color: var(--muted); font-size: 13px; }}
    .metric strong {{ display: block; margin-top: 6px; font-size: 30px; }}
    .section-note {{ color: var(--muted); max-width: 760px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      overflow: hidden;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 8px 22px rgba(31, 42, 55, .06);
    }}
    th, td {{ padding: 13px 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: middle; }}
    th {{ background: #f7fafc; color: #475467; font-size: 12px; text-transform: uppercase; }}
    td span {{ display: block; color: var(--muted); font-size: 12px; }}
    tr:last-child td {{ border-bottom: 0; }}
    .rank {{ width: 48px; color: var(--muted); font-weight: 700; }}
    .pill {{
      display: inline-block;
      color: var(--accent-dark);
      background: #e6f3f5;
      border: 1px solid #c6e4e9;
      border-radius: 999px;
      padding: 5px 9px;
      font-size: 12px;
      font-weight: 700;
    }}
    .score {{
      display: inline-flex;
      min-width: 50px;
      justify-content: center;
      padding: 5px 8px;
      border-radius: 6px;
      color: #fff;
      font-weight: 800;
    }}
    .score-high {{ background: var(--green); }}
    .score-mid {{ background: var(--gold); }}
    .score-watch {{ background: #6b7280; }}
    .score-low {{ background: var(--red); }}
    .cards {{ display: grid; gap: 16px; }}
    .candidate-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 22px;
      box-shadow: 0 10px 26px rgba(31, 42, 55, .07);
    }}
    .candidate-card header {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 16px;
      margin-bottom: 16px;
    }}
    .score-pair {{ display: flex; gap: 8px; align-items: flex-start; }}
    .score-pair span {{
      min-width: 72px;
      padding: 10px;
      border-radius: 8px;
      background: var(--soft);
      color: var(--muted);
      text-align: center;
      font-weight: 700;
    }}
    .score-pair strong {{ display: block; color: var(--ink); font-size: 22px; }}
    .card-grid, .detail-columns {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }}
    ul {{ margin: 0; padding-left: 18px; }}
    li {{ margin: 6px 0; }}
    .action-plan {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .action-box {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 20px;
    }}
    @media (max-width: 860px) {{
      .summary-grid, .card-grid, .detail-columns, .action-plan {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 32px; }}
      .candidate-card header {{ flex-direction: column; }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">Oracle EBS recruitment intelligence</p>
      <h1>Candidate matching report for Integration Developer and Business Systems Analyst roles</h1>
      <p class="section-note">A recruiter-ready view of fit, confidence, risks, and next actions across the full candidate batch.</p>
      <div class="hero-meta">
        <span>Generated {escape(generated)}</span>
        <span>Source: sample-pack/sample-pack</span>
        <span>Match threshold: 80+</span>
      </div>
    </section>

    <section class="summary-grid" aria-label="Executive summary">
      <div class="metric"><span>Total candidates</span><strong>{total}</strong></div>
      <div class="metric"><span>Position A matches</span><strong>{len(position_a)}</strong></div>
      <div class="metric"><span>Position B matches</span><strong>{len(position_b)}</strong></div>
      <div class="metric"><span>Both positions</span><strong>{len(both)}</strong></div>
      <div class="metric"><span>No match</span><strong>{len(no_match)}</strong></div>
    </section>

    <section>
      <h2>Top Candidates Overall</h2>
      <table>
        <thead><tr><th>#</th><th>Candidate</th><th>Category</th><th>Score A</th><th>Score B</th><th>Confidence</th><th>Recommendation</th></tr></thead>
        <tbody>{_html_table(ranked[:10])}</tbody>
      </table>
    </section>

    <section>
      <h2>Recommended Immediate Outreach</h2>
      <p class="section-note">These candidates cross the role threshold and have the clearest evidence for recruiter follow-up.</p>
      <div class="cards">{top_cards or "<p>No immediate outreach candidates found.</p>"}</div>
    </section>

    <section>
      <h2>Manual Review Queue</h2>
      <p class="section-note">Candidates below threshold but close enough to review for context, compensation, or adjacent openings.</p>
      <table>
        <thead><tr><th>#</th><th>Candidate</th><th>Category</th><th>Score A</th><th>Score B</th><th>Confidence</th><th>Recommendation</th></tr></thead>
        <tbody>{review_rows}</tbody>
      </table>
    </section>

    <section class="action-plan">
      <div class="action-box">
        <h2>Contact Now</h2>
        <ul>{contact_now or "<li>No candidates reached immediate outreach level.</li>"}</ul>
      </div>
      <div class="action-box">
        <h2>Do Not Prioritize</h2>
        <ul>{do_not_prioritize}</ul>
      </div>
    </section>

    <section>
      <h2>Rejected / Low Fit Snapshot</h2>
      <table>
        <thead><tr><th>#</th><th>Candidate</th><th>Category</th><th>Score A</th><th>Score B</th><th>Confidence</th><th>Recommendation</th></tr></thead>
        <tbody>{no_match_rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")


def generate_markdown_report(evaluations: list[CandidateEvaluation], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = output_dir / f"recruitment-report-{timestamp}.md"
    html_path = output_dir / f"recruitment-report-{timestamp}.html"
    stable_report_path = output_dir / "oracle-ebs-recruitment-report.md"
    stable_html_path = output_dir / "oracle-ebs-recruitment-report.html"

    total = len(evaluations)
    position_a = [item for item in evaluations if item.match_category == "Position A"]
    position_b = [item for item in evaluations if item.match_category == "Position B"]
    both = [item for item in evaluations if item.match_category == "Both"]
    no_match = [item for item in evaluations if item.match_category == "No Match"]
    ranked = sorted(evaluations, key=lambda item: item.best_score, reverse=True)
    immediate = [item for item in ranked if item.recommendation == "Contact Immediately"]

    lines = [
        "# Oracle EBS Recruitment Report",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"HTML version: {html_path.name}",
        "",
        "# Executive Summary",
        "",
        f"- Total candidates: {total}",
        f"- Position A matches: {len(position_a)}",
        f"- Position B matches: {len(position_b)}",
        f"- Both positions: {len(both)}",
        f"- No match: {len(no_match)}",
        "",
        "# Top Candidates Overall",
        "",
        "| Candidate | Category | Score A | Score B | Confidence | Recommendation |",
        "|---|---:|---:|---:|---|---|",
    ]
    lines.extend(_table_row(item) for item in ranked[:10])

    lines.extend(
        [
            "",
            "# Recommended Immediate Outreach",
            "",
            "| Candidate | Category | Score A | Score B | Confidence | Recommendation |",
            "|---|---:|---:|---:|---|---|",
        ]
    )
    lines.extend(_table_row(item) for item in immediate)

    sections = [
        ("# Position A Candidates", position_a),
        ("# Position B Candidates", position_b),
        ("# Both Positions Candidates", both),
        ("# Rejected Candidates", no_match),
    ]
    for title, items in sections:
        lines.extend(["", title, ""])
        if not items:
            lines.append("No candidates in this category.")
        for item in sorted(items, key=lambda evaluation: evaluation.best_score, reverse=True):
            lines.append(_candidate_detail(item))

    lines.extend(["", "# Recruiter Action Plan", "", "Contact now:"])
    lines.extend(f"- {item.candidate.name} ({item.match_category}, best score {_fmt(item.best_score)})" for item in immediate[:8])
    lines.append("")
    lines.append("Contact later / manual review:")
    lines.extend(
        f"- {item.candidate.name} (best score {_fmt(item.best_score)})"
        for item in ranked
        if item.recommendation in {"Review Manually / Keep Warm", "Backup Candidate"}
    )
    lines.append("")
    lines.append("Do not contact for these roles:")
    lines.extend(f"- {item.candidate.name}" for item in no_match if item.best_score < 60)

    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    _generate_html_report(evaluations, html_path)
    stable_report_path.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")
    stable_html_path.write_text(html_path.read_text(encoding="utf-8"), encoding="utf-8")
    return report_path, html_path
