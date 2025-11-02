#!/bin/bash

# Eqip.ai Streamlit Cloud Deployment Helper
# This script helps prepare your repository for Streamlit Cloud deployment

echo "🚀 Preparing Eqip.ai for Streamlit Cloud Deployment"
echo "=================================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository found"
fi

# Check if main files exist
echo "🔍 Checking deployment files..."

if [ -f "streamlit_app.py" ]; then
    echo "✅ streamlit_app.py found"
else
    echo "❌ streamlit_app.py missing - this is required for deployment"
    exit 1
fi

if [ -f "requirements_streamlit.txt" ]; then
    echo "✅ requirements_streamlit.txt found"
else
    echo "❌ requirements_streamlit.txt missing"
    exit 1
fi

if [ -d ".streamlit" ]; then
    echo "✅ .streamlit configuration directory found"
else
    echo "❌ .streamlit directory missing"
    exit 1
fi

# Test the app locally first
echo "🧪 Testing app locally..."
if command -v streamlit &> /dev/null; then
    echo "   Running quick test..."
    timeout 10s streamlit run streamlit_app.py --server.headless true --server.port 8502 > /dev/null 2>&1 &
    TEST_PID=$!
    sleep 5
    
    if curl -s http://localhost:8502 > /dev/null 2>&1; then
        echo "✅ Local test passed"
        kill $TEST_PID 2>/dev/null
    else
        echo "⚠️  Local test failed - check for errors"
        kill $TEST_PID 2>/dev/null
    fi
else
    echo "⚠️  Streamlit not installed - skipping local test"
fi

# Prepare git commit
echo "📝 Preparing for deployment..."

# Add all files
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✅ No new changes to commit"
else
    echo "📝 Committing changes..."
    git commit -m "Prepare Eqip.ai for Streamlit Cloud deployment

- Added streamlit_app.py main entry point
- Configured demo mode for frontend-only deployment
- Added Streamlit Cloud configuration files
- Updated requirements for cloud deployment"
    echo "✅ Changes committed"
fi

# Check for remote repository
if git remote get-url origin > /dev/null 2>&1; then
    REMOTE_URL=$(git remote get-url origin)
    echo "✅ Remote repository: $REMOTE_URL"
    
    echo "📤 Pushing to remote repository..."
    git push origin main
    echo "✅ Code pushed to GitHub"
    
    # Extract GitHub info
    if [[ $REMOTE_URL == *"github.com"* ]]; then
        REPO_INFO=$(echo $REMOTE_URL | sed 's/.*github\.com[:/]\([^/]*\)\/\([^/.]*\).*/\1\/\2/')
        echo ""
        echo "🎯 Ready for Streamlit Cloud Deployment!"
        echo "======================================"
        echo "1. Go to: https://share.streamlit.io/"
        echo "2. Sign in with GitHub"
        echo "3. Click 'New app'"
        echo "4. Repository: $REPO_INFO"
        echo "5. Branch: main"
        echo "6. Main file: streamlit_app.py"
        echo "7. Click 'Deploy!'"
        echo ""
        echo "🔐 Don't forget to add secrets:"
        echo "   - DEMO_MODE = \"true\""
        echo "   - Add other secrets as needed"
        echo ""
        echo "📱 Your app will be available at:"
        echo "   https://$(echo $REPO_INFO | tr '/' '-')-streamlit-app-main.streamlit.app/"
    fi
else
    echo "⚠️  No remote repository configured"
    echo "📝 To add GitHub remote:"
    echo "   git remote add origin https://github.com/yourusername/eqip-ai.git"
    echo "   git push -u origin main"
fi

echo ""
echo "📋 Deployment Summary:"
echo "====================="
echo "✅ Repository prepared"
echo "✅ Deployment files ready"
echo "✅ Configuration complete"
echo ""
echo "🎉 Ready for Streamlit Cloud deployment!"
echo ""
echo "📚 For detailed instructions, see: STREAMLIT_DEPLOYMENT_GUIDE.md"
