---
name: github-repo-management
description: "Clone/create/fork repos; manage remotes, releases."
signature: "action: str, params: dict -> result: dict"
related_skills: [github-auth, github-code-review, github-discussions, github-issues, github-pr-workflow]
allowed-tools: [terminal, file, web]
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Repositories, Git, Releases, Secrets, Configuration]
    related_skills: [github-auth, github-pr-workflow, github-issues]
---

# GitHub Repository Management

Create, clone, fork, configure, and manage GitHub repositories. Each section shows `gh` first, then the `git` + `curl` fallback.

## When This Skill Triggers

This skill is activated when the user asks you to:
- Clone, create, fork, or delete a repository
- Manage repository settings (visibility, description, topics, default branch)
- Set up or modify branch protection rules
- Manage GitHub Actions secrets or workflows
- Create, list, or manage releases
- Create, list, or manage gists
- Check repository information (stars, forks, language, size)
- Sync a fork with upstream
- Search for repositories
- Pre-publication hygiene checks before pushing a new repo

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)

### Setup

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

# Get your GitHub username (needed for several operations)
if [ "$AUTH" = "gh" ]; then
  GH_USER=$(gh api user --jq '.login')
else
  GH_USER=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | python3 -c "import sys,json; print(json.load(sys.stdin)['login'])")
fi
```

If you're inside a repo already:

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 1. Cloning Repositories

Cloning is pure `git` — works identically either way:

```bash
# Clone via HTTPS (works with credential helper or token-embedded URL)
git clone https://github.com/owner/repo-name.git

# Clone into a specific directory
git clone https://github.com/owner/repo-name.git ./my-local-dir

# Shallow clone (faster for large repos)
git clone --depth 1 https://github.com/owner/repo-name.git

# Clone a specific branch
git clone --branch develop https://github.com/owner/repo-name.git

# Clone via SSH (if SSH is configured)
git clone git@github.com:owner/repo-name.git
```

**With gh (shorthand):**

```bash
gh repo clone owner/repo-name
gh repo clone owner/repo-name -- --depth 1
```

## 2. Creating Repositories

**With gh:**

```bash
# Create a public repo and clone it
gh repo create my-new-project --public --clone

# Private, with description and license
gh repo create my-new-project --private --description "A useful tool" --license MIT --clone

# Under an organization
gh repo create my-org/my-new-project --public --clone

# From existing local directory
cd /path/to/existing/project
gh repo create my-project --source . --public --push
```

**With git + curl:**

```bash
# Create the remote repo via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{
    "name": "my-new-project",
    "description": "A useful tool",
    "private": false,
    "auto_init": true,
    "license_template": "mit"
  }'

# Clone it
git clone https://github.com/$GH_USER/my-new-project.git
cd my-new-project

# -- OR -- push an existing local directory to the new repo
cd /path/to/existing/project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/$GH_USER/my-new-project.git
git push -u origin main
```

To create under an organization:

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/orgs/my-org/repos \
  -d '{"name": "my-new-project", "private": false}'
```

### From a Template

**With gh:**

```bash
gh repo create my-new-app --template owner/template-repo --public --clone
```

**With curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/template-repo/generate \
  -d '{"owner": "'"$GH_USER"'", "name": "my-new-app", "private": false}'
```

## 3. Forking Repositories

**With gh:**

```bash
gh repo fork owner/repo-name --clone
```

**With git + curl:**

```bash
# Create the fork via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo-name/forks

# Wait a moment for GitHub to create it, then clone
sleep 3
git clone https://github.com/$GH_USER/repo-name.git
cd repo-name

# Add the original repo as "upstream" remote
git remote add upstream https://github.com/owner/repo-name.git
```

### Keeping a Fork in Sync

```bash
# Pure git — works everywhere
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**With gh (shortcut):**

```bash
gh repo sync $GH_USER/repo-name
```

## 4. Repository Information

**With gh:**

```bash
gh repo view owner/repo-name
gh repo list --limit 20
gh search repos "machine learning" --language python --sort stars
```

**With curl:**

```bash
# View repo details
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO \
  | python3 -c "
import sys, json
r = json.load(sys.stdin)
print(f\"Name: {r['full_name']}\")
print(f\"Description: {r['description']}\")
print(f\"Stars: {r['stargazers_count']}  Forks: {r['forks_count']}\")
print(f\"Default branch: {r['default_branch']}\")
print(f\"Language: {r['language']}\")"

# List your repos
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/user/repos?per_page=20&sort=updated" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin):
    vis = 'private' if r['private'] else 'public'
    print(f\"  {r['full_name']:40}  {vis:8}  {r.get('language', ''):10}  ★{r['stargazers_count']}\")"

# Search repos
curl -s \
  "https://api.github.com/search/repositories?q=machine+learning+language:python&sort=stars&per_page=10" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin)['items']:
    print(f\"  {r['full_name']:40}  ★{r['stargazers_count']:6}  {r['description'][:60] if r['description'] else ''}\")"
```

## 5. Repository Settings

**With gh:**

```bash
gh repo edit --description "Updated description" --visibility public
gh repo edit --enable-wiki=false --enable-issues=true
gh repo edit --default-branch main
gh repo edit --add-topic "machine-learning,python"
gh repo edit --enable-auto-merge
```

**With curl:**

```bash
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO \
  -d '{
    "description": "Updated description",
    "has_wiki": false,
    "has_issues": true,
    "allow_auto_merge": true
  }'

# Update topics
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.mercy-preview+json" \
  https://api.github.com/repos/$OWNER/$REPO/topics \
  -d '{"names": ["machine-learning", "python", "automation"]}'
```

## 6. Branch Protection

Branch protection enforces rules like required CI checks, PR reviews, and linear history before merge. Use the API — no web UI needed.

```bash
# View current protection
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection | python3 -m json.tool

# Write protection config to a file (easier than inline JSON for complex configs)
cat > /tmp/branch-protection.json << 'JSONEOF'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "ci/test", "app_id": 0},
      {"context": "ci/lint", "app_id": 0}
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "required_linear_history": true,
  "restrictions": null
}
JSONEOF

# Apply protection (use --input to send file content as JSON body)
gh api repos/$OWNER/$REPO/branches/main/protection \
  --input /tmp/branch-protection.json \
  --method PUT
```

### Key Rules for Personal Repos

- **Personal repos** require `"restrictions": null` (not omitted; the key must be present with null value). Organization repos can omit it or set user/team restrictions.
- **`checks` vs `contexts`**: The `checks` array (with `context` + `app_id`) is the modern format. The deprecated `contexts` string array still works but produces a warning. Use `checks`.
- **`app_id: 0`** means "any app that provides this check" — correct for most use cases.
- **`enforce_admins: true`** blocks even repo admin from bypassing. The `--admin` flag on `gh pr merge` does NOT bypass the review requirement, only the status check requirement.
- **`required_linear_history`** prevents merge commits — only rebase/squash merges allowed.

### Verify Protection is Active

```bash
# Check a PR's merge status
gh pr view $PR_NUMBER --json mergeStateStatus,mergeable

# If protection works correctly, an unapproved PR shows:
# mergeStateStatus: BLOCKED
# mergeable: MERGEABLE

# To merge with admin override (bypasses status checks but NOT reviews):
gh pr merge $PR_NUMBER --squash --admin --subject "merge: title"
# Note: Even --admin cannot skip the "at least 1 approving review" rule.
```

## 7. Secrets Management (GitHub Actions)

**With gh:**

```bash
gh secret set API_KEY --body "your-secret-value"
gh secret set SSH_KEY < ~/.ssh/id_rsa
gh secret list
gh secret delete API_KEY
```

**With curl:**

Secrets require encryption with the repo's public key — more involved via API:

```bash
# Get the repo's public key for encrypting secrets
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets/public-key

# Encrypt and set (requires Python with PyNaCl)
python3 -c "
from base64 import b64encode
from nacl import encoding, public
import json, sys

# Get the public key
key_id = '<key_id_from_above>'
public_key = '<base64_key_from_above>'

# Encrypt
sealed = public.SealedBox(
    public.PublicKey(public_key.encode('utf-8'), encoding.Base64Encoder)
).encrypt('your-secret-value'.encode('utf-8'))
print(json.dumps({
    'encrypted_value': b64encode(sealed).decode('utf-8'),
    'key_id': key_id
}))"

# Then PUT the encrypted secret
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets/API_KEY \
  -d '<output from python script above>'

# List secrets (names only, values hidden)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets \
  | python3 -c "
import sys, json
for s in json.load(sys.stdin)['secrets']:
    print(f\"  {s['name']:30}  updated: {s['updated_at']}\")"
```

Note: For secrets, `gh secret set` is dramatically simpler. If setting secrets is needed and `gh` isn't available, recommend installing it for just that operation.

## 8. Releases

**With gh:**

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release create v2.0.0-rc1 --draft --prerelease --generate-notes
gh release create v1.0.0 ./dist/binary --title "v1.0.0" --notes "Release notes"
gh release list
gh release download v1.0.0 --dir ./downloads
```

**With curl:**

```bash
# Create a release
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/releases \
  -d '{
    "tag_name": "v1.0.0",
    "name": "v1.0.0",
    "body": "## Changelog\n- Feature A\n- Bug fix B",
    "draft": false,
    "prerelease": false,
    "generate_release_notes": true
  }'

# List releases
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/releases \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin):
    tag = r.get('tag_name', 'no tag')
    print(f\"  {tag:15}  {r['name']:30}  {'draft' if r['draft'] else 'published'}\")"

# Upload a release asset (binary file)
RELEASE_ID=<id_from_create_response>
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  "https://uploads.github.com/repos/$OWNER/$REPO/releases/$RELEASE_ID/assets?name=binary-amd64" \
  --data-binary @./dist/binary-amd64
```

## 9. GitHub Actions Workflows

**With gh:**

```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID>
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID>
gh run rerun <RUN_ID> --failed
gh workflow run ci.yml --ref main
gh workflow run deploy.yml -f environment=staging
```

**With curl:**

```bash
# List workflows
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows \
  | python3 -c "
import sys, json
for w in json.load(sys.stdin)['workflows']:
    print(f\"  {w['id']:10}  {w['name']:30}  {w['state']}\")"

# List recent runs
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?per_page=10" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin)['workflow_runs']:
    print(f\"  Run {r['id']}  {r['name']:30}  {r['conclusion'] or r['status']}\")"

# Download failed run logs
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs

# Re-run a failed workflow
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun

# Re-run only failed jobs
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun-failed-jobs

# Trigger a workflow manually (workflow_dispatch)
WORKFLOW_ID=<workflow_id_or_filename>
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_ID/dispatches \
  -d '{"ref": "main", "inputs": {"environment": "staging"}}'
```

## 10. Gists

**With gh:**

```bash
gh gist create script.py --public --desc "Useful script"
gh gist list
```

**With curl:**

```bash
# Create a gist
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/gists \
  -d '{
    "description": "Useful script",
    "public": true,
    "files": {
      "script.py": {"content": "print(\"hello\")"}
    }
  }'

# List your gists
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/gists \
  | python3 -c "
import sys, json
for g in json.load(sys.stdin):
    files = ', '.join(g['files'].keys())
    print(f\"  {g['id']}  {g['description'] or '(no desc)':40}  {files}\")"
```

## Quick Reference Table

| Action | gh | git + curl |
|--------|-----|-----------|
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name --public` | `curl POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `curl POST /repos/o/r/forks` + `git clone` |
| Repo info | `gh repo view o/r` | `curl GET /repos/o/r` |
| Edit settings | `gh repo edit --...` | `curl PATCH /repos/o/r` |
| Create release | `gh release create v1.0` | `curl POST /repos/o/r/releases` |
| List workflows | `gh workflow list` | `curl GET /repos/o/r/actions/workflows` |
| Rerun CI | `gh run rerun ID` | `curl POST /repos/o/r/actions/runs/ID/rerun` |
| Set secret | `gh secret set KEY` | `curl PUT /repos/o/r/actions/secrets/KEY` (+ encryption) |

## 11. Pre-Publication Hygiene Checklist

Before pushing a repository to GitHub (especially for the first time), ensure no sensitive or irrelevant files leak:

### 11.1 Check for sensitive content
```bash
# Search for API keys and secrets
grep -rn "api[_-]key\|api[_-]secret\|secret\|password\|token" --include="*.py" --include="*.json" --include="*.md" . 2>/dev/null | grep -vi ".git" | grep -vi "node_modules"
# Search for personal identifiable information
grep -rn "$(whoami)" --include="*.md" --include="*.json" . 2>/dev/null | grep -vi ".git"
# Check for hardcoded file paths with usernames
grep -rn "/home/" --include="*.md" --include="*.json" . 2>/dev/null | grep -vi ".git"
```

### 11.2 Check for large/unrelated binary files
```bash
find . -type f -size +10M -not -path "./.git/*" 2>/dev/null
find . -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.ts" -o -name "*.aac" -o -name "*.docx" -o -name "*.pdf" \) -not -path "./.git/*" 2>/dev/null
du -sh . --exclude=.git
```

### 11.3 Build a proper .gitignore
Must cover: runtime outputs, large media (*.mp4 *.mov *.ts *.aac), PDFs, docx, .env, Python cache, OS files, IDE config. Use `git add --dry-run .` to preview before actually staging.

### 11.4 Dry-run and verify
```bash
git add --dry-run .          # preview what would be tracked
git status --short           # verify no unwanted files staged
```
If files need removal from tracking (not from disk): add to .gitignore, then `git rm --cached path/to/file`.

### 11.5 Post-push verification
Check remote contents via API after push:
```bash
curl -s "https://api.github.com/repos/$OWNER/$REPO/contents/" | python3 -c "import sys,json; [print(i['name']) for i in json.load(sys.stdin)]"
```

### Push Protection Bypass (GitHub Secret Scanning)

When GitHub secret scanning blocks a push (false positive on documentation with token examples), use `gh api` to create a push-protection bypass:

```bash
# Create bypass for the specific blocked secret
gh api repos/$OWNER/$REPO/secret-scanning/push-protection-bypasses -X POST \
  --raw-field 'reason=false_positive' \
  --raw-field 'placeholder_id=<FROM_ERROR_MESSAGE>'

# Then retry the push
git push origin HEAD:main
```

Reasons accepted by the API: `false_positive`, `used_in_tests`, `will_fix_later`. The bypass expires in ~2 hours. Full protocol in `references/push-protection-bypass.md`.

### Pitfalls
- **Push via HTTPS fails in non-interactive environments**: `git push` over HTTPS may fail with `fatal: could not read Password` even when `gh auth login` succeeds. The `gh` credential helper is not available as a standalone `git-credential-gh` binary. Workaround: use `git push` with `https://x-access-token:TOKEN@` in the remote URL, or use the GitHub API to update files directly.
- **GitHub Token from `~/.bashrc` may not be available**: `~/.bashrc` has `case $- in *i*) ;; *) return;; esac` guard for non-interactive shells. Subprocess Python does not source `.bashrc` automatically. Always pass `env={**os.environ, 'GITHUB_TOKEN': 'TOKEN'}` explicitly to `subprocess.run()`.
- **gh CLI credential helper**: `gh auth login` stores tokens in keyring but `git` does not automatically use them. The `git credential.gh` helper is not installed by default on some systems.
- **`git add -A` re-stages `git rm --cached` files**: After running `git rm --cached path/to/dir`, the files are removed from the index but still present in HEAD. Running `git add -A` (or `-a` or `--all`) afterward will inspect the working tree and re-stage the deleted files because they exist on disk. This means the.gitignore addition + cached removal is NOT enough — you must ensure `git add -A` is called only AFTER the removals are committed. **Safe workflow**: (1) Add entry to `.gitignore`, (2) `git rm --cached -r dir/`, (3) `git commit` or `git commit --amend`, (4) THEN use `git add -A` for subsequent changes. If you accidentally run `git add -A` before committing, verify with `git status --short` — you'll see re-staged deletions marked as "A" (added). Run `git rm --cached -r dir/` again before committing.
- **Multi-project push confusion**: When the user has multiple active projects (Pima, Breast Cancer, Synthos, PD Dysphagia), never assume which project to push. If the user says "push it" and you have multiple repos with pending changes, verify: check `gh repo list`, check which has pending commits, and if ambiguous ask before acting. This is a recurring error — answering without verifying pushes the wrong repo.

## Verification Checklist

Before considering the repo management task complete:

- [ ] Repository successfully created/cloned/forked (verify with `gh repo view` or API)
- [ ] If creating: correct visibility (public/private), initialized with appropriate template
- [ ] If forking: upstream remote added and fetch/sync verified
- [ ] Branch protection applied and verified on the target branch
- [ ] Releases created with correct tag, title, and assets
- [ ] Secrets set correctly (verify with `gh secret list` or API)
- [ ] Workflows listed/run/verified as expected
- [ ] Gists created/listed correctly
- [ ] Repository settings applied (description, topics, default branch, auto-merge)
- [ ] Pre-publication hygiene: checked for secrets, large files, proper .gitignore
- [ ] Post-push: verified remote contents match expectation