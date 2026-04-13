# 🤖 KrishiShakti Chatbot Setup Guide

## Current Status
✅ Chatbot is configured with OpenRouter API
⚠️ Needs API key to enable AI features
✅ Fallback demo mode available

## Quick Setup (2 minutes)

### Step 1: Get FREE OpenRouter API Key

1. **Visit**: https://openrouter.ai/
2. **Sign Up**: Click "Sign In" → Sign up with Google/GitHub/Email
3. **Get Key**: 
   - Go to "Keys" section
   - Click "Create Key"
   - Copy your key (starts with `sk-or-v1-`)

### Step 2: Add API Key

**Option A: Using Setup Script (Recommended)**
```bash
python3 setup_chatbot.py
```
Then paste your API key when prompted.

**Option B: Manual Setup**
1. Open `ai_chat.py`
2. Find this line:
   ```python
   OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', 'sk-or-v1-...')
   ```
3. Replace the placeholder with your actual key:
   ```python
   OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', 'sk-or-v1-YOUR_ACTUAL_KEY_HERE')
   ```
4. Save the file

**Option C: Environment Variable**
```bash
export OPENROUTER_API_KEY="sk-or-v1-YOUR_KEY_HERE"
python3 app.py
```

### Step 3: Test the Chatbot

1. Make sure server is running: `python3 app.py`
2. Open: http://localhost:5001/chatbot.html
3. Ask a question like: "What should I do about my soil moisture?"

## Features

### ✅ What Works Now
- Real-time sensor data integration
- Location-aware responses (Lāndrān, Punjab, India)
- Multi-language support (English, Hindi, Punjabi)
- Fallback demo mode (works without API key)

### 🚀 With API Key
- AI-powered intelligent responses
- Context-aware farming advice
- Natural language understanding
- Personalized recommendations based on your sensor data

## Free Tier Benefits

OpenRouter free tier includes:
- ✅ Multiple free models (Llama 3.1, Mistral, etc.)
- ✅ No credit card required
- ✅ Generous rate limits
- ✅ Fast response times

## Troubleshooting

### "API Key Error"
- Make sure you copied the complete key (starts with `sk-or-v1-`)
- Check for extra spaces before/after the key
- Verify the key is active on OpenRouter dashboard

### "Rate limit exceeded"
- Free tier has limits, wait a few minutes
- Consider upgrading to paid tier for higher limits

### "Connection error"
- Check your internet connection
- Verify firewall isn't blocking openrouter.ai

### Chatbot not responding
- Check if server is running: `python3 app.py`
- Open browser console (F12) to see errors
- Try refreshing the page

## Demo Mode (No API Key)

Without an API key, the chatbot works in demo mode with:
- Pre-programmed responses
- Basic sensor data interpretation
- Multi-language support
- Topic detection (water, fertilizer, pests, etc.)

## Models Available

Current model: `meta-llama/llama-3.1-8b-instruct:free` (FREE)

Other free models you can try:
- `google/gemma-2-9b-it:free`
- `mistralai/mistral-7b-instruct:free`
- `meta-llama/llama-3-8b-instruct:free`

To change model, edit `ai_chat.py`:
```python
"model": "meta-llama/llama-3.1-8b-instruct:free",  # Change this line
```

## Support

- OpenRouter Docs: https://openrouter.ai/docs
- OpenRouter Discord: https://discord.gg/openrouter
- Check API status: https://status.openrouter.ai/

## Next Steps

1. Get your API key from https://openrouter.ai/keys
2. Run `python3 setup_chatbot.py`
3. Test at http://localhost:5001/chatbot.html
4. Ask farming questions in English, Hindi, or Punjabi!

---

**Need help?** The chatbot works in demo mode even without an API key, but AI features require a free OpenRouter account.
