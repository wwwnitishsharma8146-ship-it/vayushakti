# 🚀 Quick Start - AI Chatbot (2 Minutes)

## Step 1: Get FREE API Key (30 seconds)

Visit: **https://openrouter.ai/keys**

1. Sign in with Google/GitHub
2. Click "Create Key"
3. Copy your key (starts with `sk-or-v1-`)

## Step 2: Setup (30 seconds)

```bash
python3 setup_openrouter.py
```

Paste your API key when prompted.

## Step 3: Restart Server (10 seconds)

Press `Ctrl+C` to stop, then:

```bash
python3 app.py
```

## Step 4: Test (1 minute)

Open: **http://localhost:5001/chatbot.html**

Ask: "What should I do about my soil moisture?"

## ✅ Done!

You now have:
- 🧠 AI-powered intelligent responses
- 🌍 Multi-language support (English, Hindi, Punjabi)
- 📊 Real-time sensor data integration
- 🎯 Personalized farming advice for Landran, Punjab

## 💡 Quick Test Commands

```bash
# Test AI from command line
python3 ai_chat.py

# Check if API key is set
grep "OPENROUTER_API_KEY" ai_chat.py
```

## 🆘 Need Help?

**Problem**: "API key not configured"
**Solution**: Run `python3 setup_openrouter.py` again

**Problem**: Chatbot shows demo mode
**Solution**: Restart server after adding API key

**Problem**: "Rate limit exceeded"
**Solution**: Wait 5 minutes, or chatbot will use demo mode

## 📚 Full Guide

See: `SETUP-AI-CHATBOT.md` for detailed instructions

---

**Total Time**: 2 minutes
**Cost**: FREE forever
**Result**: Professional AI farming assistant! 🌾
