#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║  KrishiShakti - GitHub Upload Script                  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed!"
    echo "Please install git first: https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " github_username

if [ -z "$github_username" ]; then
    echo "❌ GitHub username cannot be empty!"
    exit 1
fi

echo ""
echo "📋 Repository will be created at:"
echo "   https://github.com/$github_username/krishishakti"
echo ""

read -p "Have you created the repository on GitHub? (y/n): " repo_created

if [ "$repo_created" != "y" ] && [ "$repo_created" != "Y" ]; then
    echo ""
    echo "📝 Please create the repository first:"
    echo "   1. Go to: https://github.com/new"
    echo "   2. Repository name: krishishakti"
    echo "   3. Description: Smart Agriculture & IoT Monitoring System"
    echo "   4. Make it Public"
    echo "   5. DO NOT initialize with README, .gitignore, or license"
    echo "   6. Click 'Create repository'"
    echo ""
    echo "Then run this script again!"
    exit 0
fi

echo ""
echo "🔧 Initializing git repository..."

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "📦 Adding files..."

# Add all files
git add .

echo "✅ Files added"
echo ""

# Show what will be committed
echo "📋 Files to be committed:"
git status --short
echo ""

read -p "Continue with commit? (y/n): " continue_commit

if [ "$continue_commit" != "y" ] && [ "$continue_commit" != "Y" ]; then
    echo "❌ Upload cancelled"
    exit 0
fi

echo ""
echo "💾 Creating commit..."

# Create commit
git commit -m "Initial commit: KrishiShakti IoT Agriculture System

Features:
- Real-time sensor monitoring (7 sensors)
- AI chatbot with multi-language support
- Agriculture AI with disease detection
- Smart advisory system
- Google Sheets integration
- Data visualization and export
- WebSocket real-time updates"

echo "✅ Commit created"
echo ""

# Add remote
echo "🔗 Adding remote repository..."

# Remove existing remote if any
git remote remove origin 2>/dev/null

# Add new remote
git remote add origin "https://github.com/$github_username/krishishakti.git"

echo "✅ Remote added"
echo ""

# Rename branch to main
echo "🌿 Setting main branch..."
git branch -M main
echo "✅ Branch set to main"
echo ""

# Push to GitHub
echo "📤 Pushing to GitHub..."
echo ""
echo "⚠️  You will be asked for your GitHub credentials"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║  ✅ SUCCESS! Project uploaded to GitHub!              ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎉 Your repository is now live at:"
    echo "   https://github.com/$github_username/krishishakti"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Visit your repository"
    echo "   2. Update README.md with your information"
    echo "   3. Add topics: iot, agriculture, python, flask, sensors"
    echo "   4. Add screenshots (optional)"
    echo "   5. Star your own repository ⭐"
    echo ""
    echo "🔄 To update in the future:"
    echo "   git add ."
    echo "   git commit -m \"Your message\""
    echo "   git push"
    echo ""
else
    echo ""
    echo "❌ Upload failed!"
    echo ""
    echo "Common issues:"
    echo "   1. Wrong GitHub username or password"
    echo "   2. Repository doesn't exist on GitHub"
    echo "   3. No internet connection"
    echo ""
    echo "Try again or see UPLOAD-TO-GITHUB.md for help"
    echo ""
fi
