# Oracle EBS Recruitment Agent

## Purpose

This skill analyzes Oracle EBS job descriptions and candidate profiles, scores each candidate against two target roles, classifies the fit, and generates a recruiter-friendly report.

The current default roles are:

- Position A: Integration Developer - Oracle EBS
- Position B: Business Systems Analyst - Oracle EBS

The agent is reusable for future job descriptions and candidate batches by changing the input folder.

## Inputs

Place files in:

```text
sample-pack/sample-pack/jobs
sample-pack/sample-pack/candidates
```

Supported formats:

- PDF
- TXT
- Markdown

The default input directory can be changed with:

```env
RECRUITMENT_DATA_DIR=sample-pack/sample-pack
```

## Execution

From the repository root:

```bash
pip install -r requirements.txt
python src/main.py
```

## Expected Output

The agent creates:

```text
reports/recruitment-report-<timestamp>.md
reports/recruitment-report-<timestamp>.html
```

The HTML report is the recruiter-facing deliverable. The Markdown report is the Notion-ready source.

## Behavior

The agent:

1. Reads job descriptions.
2. Extracts structured role requirements.
3. Reads candidate profiles.
4. Extracts structured candidate attributes.
5. Scores every candidate against both roles.
6. Classifies each candidate as Position A, Position B, Both, or No Match.
7. Generates recruiter recommendations, confidence, justification, and risks.
8. Generates Markdown and HTML reports.
9. Attempts Notion publication when Notion MCP publishing is configured.

## Scoring Rules

Position A:

- Technical Match: 40%
- Oracle EBS Match: 25%
- Experience Match: 15%
- Language Match: 10%
- Industry Match: 10%

Position B:

- Functional Match: 35%
- Business Analysis Match: 25%
- Oracle EBS Match: 20%
- Leadership Match: 10%
- Language Match: 10%

Classification:

- scoreA >= 80 and scoreB < 80: Position A
- scoreB >= 80 and scoreA < 80: Position B
- scoreA >= 80 and scoreB >= 80: Both
- Otherwise: No Match

## Recruiter Guidance

Prioritize candidates marked:

- `Contact Immediately`
- `High` confidence
- score >= 80 for either target role

Candidates below 80 but above 70 should be manually reviewed as warm or backup candidates.

