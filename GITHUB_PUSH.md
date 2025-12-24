# GitHub Push Instructions

## Prerequisites

1. Create a GitHub account (if you don't have one): https://github.com/signup
2. Install Git on your machine (if not already installed)
3. Generate a GitHub Personal Access Token (PAT) for authentication

---

## Step 1: Generate GitHub Personal Access Token (PAT)

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: `seo-agent-deployment`
4. Select scopes:
   - ✅ `repo` (full control of private repositories)
   - ✅ `workflow` (update GitHub Actions)
5. Click "Generate token"
6. **Copy the token** (you'll only see it once!)

---

## Step 2: Create GitHub Repository

### Option A: Via GitHub UI (Recommended)

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `internal-linking-ai-agent`
   - **Description**: `SEO-safe internal linking recommendations agent`
   - **Visibility**: Public (for portfolio) or Private (for clients)
   - **Initialize**: Leave unchecked (we already have commits)
3. Click "Create repository"
4. Copy the repository URL (looks like: `https://github.com/yourusername/internal-linking-ai-agent.git`)

### Option B: Via Git CLI

If you have GitHub CLI installed:
```bash
gh repo create internal-linking-ai-agent \
  --public \
  --source=. \
  --remote=origin \
  --push
```

---

## Step 3: Add Remote and Push to GitHub

Replace `yourusername` and use your actual repo URL:

```bash
cd f:/2- Development 2025/Viscual Studio Code/python-seo-starter/internal_links_ai-agent

# Add GitHub remote
git remote add origin https://github.com/yourusername/internal-linking-ai-agent.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

When prompted for authentication:
- **Username**: Your GitHub username
- **Password**: Paste the Personal Access Token (PAT) you created earlier

---

## Step 4: Verify on GitHub

1. Go to https://github.com/yourusername/internal-linking-ai-agent
2. Verify you see:
   - ✅ All Python files
   - ✅ README.md
   - ✅ DEPLOYMENT.md
   - ✅ .github/workflows/tests.yml (GitHub Actions)
   - ✅ .gitignore

---

## Step 5: Enable GitHub Actions (If Needed)

1. Go to repository → **Actions** tab
2. If prompted, click "Enable GitHub Actions"
3. Tests should run automatically on next push

Check status at: https://github.com/yourusername/internal-linking-ai-agent/actions

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `fatal: unable to access repository` | Check GitHub URL and PAT token |
| `Authentication failed` | Regenerate and use new PAT |
| `branch main not found` | Run `git branch -M main` before push |
| `remote origin already exists` | Run `git remote remove origin` first |

---

## Next Steps

After pushing to GitHub:

1. **Add GitHub topics** (for discoverability):
   - Settings → About → Add topics: `seo`, `automation`, `internal-linking`, `python`

2. **Set up branch protection** (optional, for production):
   - Settings → Branches → Add rule for `main`
   - Require pull request reviews before merge
   - Require status checks to pass

3. **Create a `CONTRIBUTING.md`** if accepting contributions:
   - Guidelines for pull requests
   - Development setup instructions
   - Testing requirements

4. **Deploy to VPS** using [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Quick Reference

```bash
# Clone the repo locally
git clone https://github.com/yourusername/internal-linking-ai-agent.git

# Set up development environment
cd internal-linking-ai-agent
bash setup.sh

# Make changes
git add .
git commit -m "Your commit message"
git push origin main

# View remote
git remote -v

# Check branch
git branch -a
```

---

## Security Notes

- ✅ PAT tokens are secure (one-time generation)
- ✅ .gitignore excludes CSV, PDF, JSON outputs (no data leaks)
- ✅ No credentials stored in code
- ✅ All dependencies in requirements.txt (reproducible)

---

**You're ready to share this project with the world! 🚀**
