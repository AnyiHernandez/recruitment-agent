# Oracle Recruitment Agent

Reusable recruitment agent for matching candidate profiles against Oracle EBS job descriptions.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Setup

The project reads the existing sample package by default:

```text
sample-pack/sample-pack/jobs
sample-pack/sample-pack/candidates
```

Optional `.env`:

```bash
copy .env.example .env
```

Key settings:

```env
RECRUITMENT_DATA_DIR=sample-pack/sample-pack
REPORTS_DIR=reports
NOTION_ENABLED=false
NOTION_PARENT_PAGE_ID=
NOTION_API_KEY=
```

## Usage

```bash
python src/main.py
```

The command:

1. Reads jobs.
2. Reads candidates.
3. Extracts structured profiles.
4. Scores candidates for both positions.
5. Classifies each candidate.
6. Generates a recruiter-friendly Markdown report.
7. Generates a polished standalone HTML report for presentation.
8. Attempts Notion publication when configured.

## Architecture

- `agent.md`: executable skill instructions.
- `NOTION_MCP_SETUP.md`: exact Notion MCP setup instructions for Cowork/Codex/OpenCode.
- `src/parser.py`: reads PDF, TXT, and Markdown documents.
- `src/extractor.py`: extracts reusable job and candidate models.
- `src/scorer.py`: applies weighted scoring rules.
- `src/classifier.py`: classifies candidates and builds recruiter recommendations.
- `src/report_generator.py`: creates the Markdown report.
- `src/notion_publisher.py`: isolates Notion publishing.
- `src/main.py`: orchestrates the complete workflow.

## Delivery

See:

- `agent.md` for executable skill instructions.
- `NOTION_MCP_SETUP.md` for Notion MCP setup and publishing configuration.
- `GITHUB_DELIVERY.md` for the public GitHub repository and collaborator invitation checklist.

## Scoring

Position A: Integration Developer - Oracle EBS

- Technical Match: 40%
- Oracle EBS Match: 25%
- Experience Match: 15%
- Language Match: 10%
- Industry Match: 10%

Position B: Business Systems Analyst - Oracle EBS

- Functional Match: 35%
- Business Analysis Match: 25%
- Oracle EBS Match: 20%
- Leadership Match: 10%
- Language Match: 10%

## Output

Reports are written to:

```text
reports/
```

Each run creates:

- A Markdown report for portability and Notion publication.
- A styled HTML report for a polished recruiter-facing delivery.
- Stable delivery files:
  - `reports/oracle-ebs-recruitment-report.html`
  - `reports/oracle-ebs-recruitment-report.md`

Each report includes an executive summary, ranking table, immediate outreach list, role-specific analysis, rejected candidates, and recruiter action plan.
