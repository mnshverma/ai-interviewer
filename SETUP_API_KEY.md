# ⚠️ SETUP REQUIRED: Add Your OpenRouter API Key

## Quick Setup (2 minutes)

### 1. Get Your Free API Key

**Visit:** https://openrouter.ai/keys

1. Click "Sign up" (free account)
2. Click "Create Key"
3. Copy the entire key (starts with `sk-or-v1-`)

### 2. Add Key to .env File

**Option A: Edit Manually**

1. Open `.env` file in this folder
2. Replace the empty value:
   ```
   VITE_OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
   ```
3. Save the file

**Option B: Use Command Line**

```powershell
# Run this in PowerShell (replace with your actual key)
"VITE_OPENROUTER_API_KEY=sk-or-v1-your-actual-key" | Out-File -FilePath .env -Encoding utf8
```

### 3. Restart Development Server

**Close the current server (Ctrl+C) and run:**

```bash
npm run dev
```

**Or just refresh the page** - Vite might auto-reload

---

## Why This Error Happened

The 404 error occurs because:

- ❌ `.env` file exists but API key is empty
- ❌ `getApiKey()` function can't find the key
- ❌ API request fails with 404

## After Adding the Key

✅ API requests will work
✅ Resume analysis will function
✅ Job description analysis will work
✅ Questions will generate
✅ Interview will start successfully

---

## Testing the Fix

After adding your API key:

1. **Refresh** the page (http://localhost:5173)
2. **Upload** the sample resume OR enter a job description
3. **Click** "Start Interview"
4. **Should work!** 🎉

---

## Need Help Getting a Key?

### OpenRouter Free Tier:

- ✅ **Free** LLaMA 3.1 8B Instruct model
- ✅ No credit card required
- ✅ Generous rate limits
- ✅ Perfect for development

### Steps:

1. Go to https://openrouter.ai
2. Click "Sign in" (top right)
3. Sign up with Google/GitHub (fastest)
4. Click your profile → "Keys"
5. Click "Create Key"
6. Name it "AI Interviewer"
7. Copy the key
8. Paste in `.env` file

---

## Vercel Deployment

When deploying to Vercel:

- Don't commit `.env` to git (it's ignored)
- Add the key in Vercel dashboard:
  - Settings → Environment Variables
  - Name: `VITE_OPENROUTER_API_KEY`
  - Value: Your API key

---

**Once you add the key, everything will work!** 🚀
