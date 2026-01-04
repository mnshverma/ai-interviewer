# ⚠️ CRITICAL: Your API Key is Not Set!

## Current Status

Your `.env` file contains:

```
VITE_OPENROUTER_API_KEY=
```

This is **EMPTY** - that's why you're getting 404 errors!

---

## ✅ FIX IT NOW (Choose One Method):

### Method 1: Manual Edit (EASIEST)

1. **Get API Key**: Go to https://openrouter.ai/keys

   - Sign up (free, no credit card)
   - Click "Create Key"
   - Copy the FULL key (example: `sk-or-v1-abc123def456...`)

2. **Open `.env` file** in this folder

3. **Paste your key** after the `=` sign:
   ```
   VITE_OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
   ```
4. **Save the file**

5. **Refresh browser** (http://localhost:5173)

---

### Method 2: PowerShell Command

```powershell
# Replace YOUR_KEY with your actual OpenRouter API key
$key = "sk-or-v1-YOUR_KEY_HERE"
"VITE_OPENROUTER_API_KEY=$key" | Out-File -FilePath .env -Encoding utf8 -Force
```

---

## Test if It Worked

After adding your key, open browser console and look for:

- ❌ **Before**: `OpenRouter API error: 404`
- ✅ **After**: No more 404 errors, interview starts!

---

## If You Don't Have a Key Yet

### Get Free OpenRouter API Key:

1. **Visit**: https://openrouter.ai
2. **Click**: "Sign In" (top right)
3. **Sign up** with Google/GitHub (fastest)
4. **Go to**: Profile → "Keys"
5. **Click**: "Create Key"
6. **Name it**: "AI Interviewer"
7. **Copy** the entire key
8. **Paste** in `.env` file

**Free tier includes:**

- ✅ LLaMA 3.1 models
- ✅ Google Gemma models
- ✅ Other free models
- ✅ No credit card needed
- ✅ Generous rate limits

---

## Why This Happens

The code checks for the API key:

```javascript
const getApiKey = () => {
  const apiKey = import.meta.env.VITE_OPENROUTER_API_KEY;
  if (!apiKey) {
    throw new Error("OpenRouter API key not configured");
  }
  return apiKey;
};
```

When empty → OpenRouter returns 404 → Interview fails

---

## Double-Check Your .env File

Should look like this:

```
VITE_OPENROUTER_API_KEY=sk-or-v1-1234567890abcdef...
```

**NOT like this:**

```
VITE_OPENROUTER_API_KEY=
```

or

```
VITE_OPENROUTER_API_KEY=your_api_key_here
```

---

## After You Add the Key

1. **Refresh** the browser
2. **Try** uploading resume or job description
3. **Click** "Start Interview"
4. **Should work!** 🎉

The 404 error will disappear once you add a REAL API key!

---

**Your `.env` file is ready, it just needs YOUR actual OpenRouter API key!** 🔑
