# OpenRouter API Setup for Chatbot

The chatbot has been updated to use OpenRouter API instead of Google Gemini.

## Quick Setup Steps:

### 1. Get Your OpenRouter API Key
- Go to https://openrouter.ai/
- Sign up for a free account
- Navigate to "Keys" section
- Create a new API key
- Copy your API key

### 2. Configure the API Key
Open `ai_chat.py` and replace this line:
```python
OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY_HERE"
```

With your actual API key:
```python
OPENROUTER_API_KEY = "sk-or-v1-xxxxxxxxxxxxx"
```

### 3. Choose Your Model (Optional)
The chatbot uses a free model by default: `meta-llama/llama-3.1-8b-instruct:free`

You can change it to other models in `ai_chat.py`:
```python
"model": "meta-llama/llama-3.1-8b-instruct:free",  # Free model
```

Popular alternatives:
- `openai/gpt-3.5-turbo` (paid, fast and good)
- `anthropic/claude-3-haiku` (paid, very good)
- `google/gemini-pro` (paid, excellent)
- `meta-llama/llama-3.1-70b-instruct` (paid, powerful)

### 4. Test the Chatbot
1. Start your server: `python app.py`
2. Open http://localhost:5000/chatbot.html
3. Ask a farming question
4. The AI should respond using OpenRouter

## Features:
✅ Multi-language support (English, Hindi, Punjabi)
✅ Real-time sensor data integration
✅ Context-aware agricultural advice
✅ Fallback to demo mode if API fails

## Troubleshooting:
- **"API Configuration Error"**: Check your API key in `ai_chat.py`
- **"API Error 401"**: Invalid API key
- **"API Error 429"**: Rate limit exceeded (wait or upgrade plan)
- **Timeout errors**: Check your internet connection

## Cost:
- Free tier: Limited requests per day
- Paid tier: Pay per token used
- Check pricing at: https://openrouter.ai/docs#models
