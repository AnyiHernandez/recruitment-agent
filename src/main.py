from __future__ import annotations

import os
from pathlib import Path
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from classifier import evaluate_candidate
from extractor import extract_candidate_profile, extract_job_requirements
from notion_publisher import publish_report_to_notion
from parser import parse_documents
from report_generator import generate_markdown_report
from scorer import score_candidate_for_position


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_environment() -> None:
    if load_dotenv:
        load_dotenv(project_root() / ".env")


def resolve_data_dir() -> Path:
    configured = os.getenv("RECRUITMENT_DATA_DIR", "sample-pack/sample-pack")
    path = Path(configured)
    if not path.is_absolute():
        path = project_root() / path
    return path


def main() -> int:
    load_environment()
    root = project_root()
    data_dir = resolve_data_dir()
    jobs_dir = data_dir / "jobs"
    candidates_dir = data_dir / "candidates"
    reports_dir = root / os.getenv("REPORTS_DIR", "reports")

    print(f"Reading jobs from: {jobs_dir}")
    print(f"Reading candidates from: {candidates_dir}")

    job_documents = parse_documents(jobs_dir)
    candidate_documents = parse_documents(candidates_dir)
    if len(job_documents) < 2:
        raise RuntimeError("Expected at least two job descriptions.")
    if not candidate_documents:
        raise RuntimeError("No candidate profiles found.")

    jobs = [extract_job_requirements(document) for document in job_documents]
    jobs_by_role = {job.role_id: job for job in jobs}
    if "position_a" not in jobs_by_role or "position_b" not in jobs_by_role:
        raise RuntimeError("Could not identify both Position A and Position B job descriptions.")

    candidates = [extract_candidate_profile(document) for document in candidate_documents]
    evaluations = []
    for candidate in candidates:
        score_a = score_candidate_for_position(candidate, jobs_by_role["position_a"])
        score_b = score_candidate_for_position(candidate, jobs_by_role["position_b"])
        evaluations.append(evaluate_candidate(candidate, score_a, score_b))

    report_path, html_report_path = generate_markdown_report(evaluations, reports_dir)
    print(f"Markdown report generated: {report_path}")
    print(f"HTML report generated: {html_report_path}")

    notion_url = None
    try:
        notion_url = publish_report_to_notion(report_path, "Oracle EBS Recruitment Report")
    except RuntimeError as exc:
        print(f"Notion publication skipped: {exc}")

    if notion_url:
        print(f"Notion URL: {notion_url}")
    else:
        print("Notion URL: not published in this environment")

    return 0


if __name__ == "__main__":
    sys.exit(main())
