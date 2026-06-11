# GitHub Delivery Checklist

The final deliverable must be a public GitHub repository.

## Required Repository Contents

- `SUBMISSION.txt`
- `README.md`
- `agent.md`
- `NOTION_MCP_SETUP.md`
- `requirements.txt`
- `.env.example`
- `src/`
- `prompts/`
- `sample-pack/`
- `reports/oracle-ebs-recruitment-report.html`
- `reports/oracle-ebs-recruitment-report.md`

## Publish The Repository

If GitHub CLI is installed and authenticated:

```bash
gh repo create oracle-recruitment-agent --public --source . --remote origin --push
```

If the repository already exists:

```bash
git remote add origin https://github.com/<your-user>/oracle-recruitment-agent.git
git add .
git commit -m "Build reusable Oracle EBS recruitment agent"
git push -u origin main
```

If GitHub CLI is not installed:

1. Create a public repository named `oracle-recruitment-agent` in GitHub.
2. Copy the HTTPS repository URL.
3. Run:

```bash
git remote add origin https://github.com/<your-user>/oracle-recruitment-agent.git
git add .
git commit -m "Build reusable Oracle EBS recruitment agent"
git branch -M main
git push -u origin main
```

## Invite Pablo As Collaborator

Preferred CLI command:

```bash
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/<your-user>/oracle-recruitment-agent/collaborators/pablo@betterway.dev \
  -f permission=push
```

If GitHub does not accept email in the collaborator API for the account, use the GitHub UI:

1. Open the repository in GitHub.
2. Go to `Settings`.
3. Go to `Collaborators and teams`.
4. Click `Add people`.
5. Enter `pablo@betterway.dev`.
6. Send the invitation.

## Update SUBMISSION.txt

Before submitting, replace:

```text
Repository: <github-url>
Loom: <loom-url>
Notion Report: <notion-url>
Time Invested: <hours>
```

with the final public links.
