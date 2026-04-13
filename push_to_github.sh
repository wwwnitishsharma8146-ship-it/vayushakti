#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Push KrishiShakti Updates to GitHub                 ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Error: Not in a git repository"
    echo "   Please run this script from the project root directory"
    exit 1
fi

echo "📋 Current git status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git status --short
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Count changes
MODIFIED=$(git status --short | grep "^ M" | wc -l)
ADDED=$(git status --short | grep "^??" | wc -l)
DELETED=$(git status --short | grep "^ D" | wc -l)

echo "📊 Changes summary:"
echo "   Modified files: $MODIFIED"
echo "   New files: $ADDED"
echo "   Deleted files: $DELETED"
echo ""

# Ask for confirmation
read -p "Do you want to stage all changes? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted by user"
    exit 1
fi

echo ""
echo "📦 Staging all changes..."
git add .

echo "✓ Files staged"
echo ""

# Show what will be committed
echo "📋 Files to be committed:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git diff --cached --name-status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ask for commit message
echo "💬 Commit message options:"
echo "   1. Use default message (recommended)"
echo "   2. Enter custom message"
echo ""
read -p "Choose option (1 or 2): " -n 1 -r
echo

if [[ $REPLY == "1" ]]; then
    # Use default commit message
    COMMIT_MSG="Fix: Dashboard quick stats, image upload API, and Blynk integration

Major fixes:
- Fixed dashboard quick stats cards showing placeholders
- Fixed AI crop disease detection image upload (HTTP 400 error)
- Updated Blynk bridge to use uppercase pins (V5, V7, V6, V4, V3)
- Changed Flask server to port 5000
- Added comprehensive error handling and logging
- Created test and debug utilities

All features tested and working ✅"
else
    # Ask for custom message
    echo "Enter commit message (press Enter when done):"
    read COMMIT_MSG
fi

echo ""
echo "📝 Committing changes..."
git commit -m "$COMMIT_MSG"

if [ $? -ne 0 ]; then
    echo "❌ Commit failed"
    exit 1
fi

echo "✓ Changes committed"
echo ""

# Check remote
REMOTE=$(git remote -v | grep origin | head -1 | awk '{print $2}')
echo "🌐 Remote repository: $REMOTE"
echo ""

# Ask to push
read -p "Push to GitHub? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Changes committed locally but not pushed"
    echo "   Run 'git push origin main' when ready"
    exit 0
fi

echo ""
echo "🚀 Pushing to GitHub..."

# Get current branch
BRANCH=$(git branch --show-current)
echo "   Branch: $BRANCH"

git push origin $BRANCH

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║  ✅ Successfully pushed to GitHub!                    ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "🔗 View your repository:"
    echo "   https://github.com/vishalpaliwal79/KrishiShakti"
    echo ""
    echo "📊 Summary:"
    echo "   ✓ $MODIFIED files modified"
    echo "   ✓ $ADDED new files added"
    echo "   ✓ Changes committed and pushed"
    echo ""
else
    echo ""
    echo "❌ Push failed!"
    echo ""
    echo "Common issues:"
    echo "   1. Authentication required - use Personal Access Token"
    echo "   2. Branch protection - may need pull request"
    echo "   3. Network issues - check internet connection"
    echo ""
    echo "💡 Try:"
    echo "   git push origin $BRANCH --verbose"
    echo ""
fi
