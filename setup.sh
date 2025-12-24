#!/bin/bash
# Quick setup script for local development

echo "🚀 Setting up Internal Linking AI Agent..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
python test_internal_linking.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the agent, use:"
echo "  python run_agent.py --site https://example.com"
echo ""
echo "To run tests, use:"
echo "  python test_internal_linking.py"
