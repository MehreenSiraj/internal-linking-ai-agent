#!/usr/bin/env bash
# This script helps you push to GitHub
# Run: bash github_push_helper.sh

echo "=========================================="
echo "Internal Linking AI Agent - GitHub Push"
echo "=========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    echo "   Download from: https://git-scm.com/download"
    exit 1
fi

# Check if we're in a git repo
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Run 'git init' first."
    exit 1
fi

echo "✅ Git is installed and repo is initialized"
echo ""
echo "Current commits:"
git log --oneline | head -5
echo ""

# Prompt for GitHub username
echo "=========================================="
echo "Step 1: Enter your GitHub information"
echo "=========================================="
read -p "Enter your GitHub username: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo "❌ GitHub username is required."
    exit 1
fi

# Repository name
REPO_NAME="internal-linking-ai-agent"
GITHUB_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo ""
echo "Repository URL will be: $GITHUB_URL"
echo ""

# Confirm
read -p "Is this correct? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "❌ Cancelled."
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 2: GitHub Repository Setup"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Go to https://github.com/new"
echo "   2. Create a repository named: $REPO_NAME"
echo "   3. Leave 'Initialize with README' unchecked"
echo "   4. Click 'Create repository'"
echo ""
echo "After creating the repository, come back here."
read -p "Press ENTER when you've created the GitHub repository..."

echo ""
echo "=========================================="
echo "Step 3: GitHub Authentication"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANT:"
echo "   You need a GitHub Personal Access Token (PAT)"
echo ""
echo "To get a PAT:"
echo "   1. Go to: https://github.com/settings/tokens"
echo "   2. Click 'Generate new token' → 'Generate new token (classic)'"
echo "   3. Name it: 'seo-agent-push'"
echo "   4. Select scope: ✓ repo"
echo "   5. Click 'Generate token'"
echo "   6. Copy the token (you'll only see it once!)"
echo ""
read -p "Press ENTER when you have your PAT token ready..."

echo ""
echo "=========================================="
echo "Step 4: Pushing to GitHub"
echo "=========================================="
echo ""

# Check if remote exists
if git remote | grep -q "^origin$"; then
    echo "Removing existing origin remote..."
    git remote remove origin
fi

echo "Adding GitHub as remote..."
git remote add origin "$GITHUB_URL"

echo "Setting main branch..."
git branch -M main

echo ""
echo "🔐 Pushing to GitHub (you'll be prompted for your PAT)..."
echo "   When asked for password, paste your Personal Access Token"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS!"
    echo "=========================================="
    echo ""
    echo "Your code is now on GitHub!"
    echo ""
    echo "View your repository at:"
    echo "   $GITHUB_URL"
    echo ""
    echo "Next steps:"
    echo "   1. Check GitHub Actions (tests run automatically)"
    echo "   2. Follow DEPLOYMENT.md to deploy to VPS"
    echo "   3. Set up n8n integration as needed"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ PUSH FAILED"
    echo "=========================================="
    echo ""
    echo "Troubleshooting:"
    echo "   • Verify GitHub username is correct"
    echo "   • Verify PAT token is correct"
    echo "   • Check you created the repo at https://github.com/new"
    echo "   • Check internet connection"
    echo ""
    echo "Try again with: git push -u origin main"
    echo ""
fi
