# 🚀 Deploying to Vercel

## Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=YOUR_GITHUB_REPO_URL)

## Manual Deployment Steps

### 1. Prerequisites

- GitHub account
- Vercel account (free): https://vercel.com/signup
- OpenRouter API key (free): https://openrouter.ai/keys

### 2. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: AI Interviewer"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 3. Deploy to Vercel

#### Option A: Via Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure project:

   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. Add Environment Variable:

   - Click "Environment Variables"
   - **Name**: `VITE_OPENROUTER_API_KEY`
   - **Value**: Your OpenRouter API key (sk-or-v1-...)
   - Select all environments (Production, Preview, Development)

5. Click "Deploy"

#### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# When prompted:
# - Link to existing project? No
# - Project name: ai-interviewer (or your choice)
# - Directory: ./
# - Override settings? No

# Add environment variable
vercel env add VITE_OPENROUTER_API_KEY

# Paste your OpenRouter API key when prompted
# Select: Production, Preview, Development (all)

# Deploy to production
vercel --prod
```

### 4. Verify Deployment

1. Visit your deployment URL
2. Try uploading a resume or entering a job description
3. Start an interview
4. Check browser console for any errors

## Environment Variables

### Required

- `VITE_OPENROUTER_API_KEY`: Your OpenRouter API key

### How to Add in Vercel

1. Go to your project in Vercel
2. Click "Settings"
3. Click "Environment Variables"
4. Add the variable:
   - **Key**: `VITE_OPENROUTER_API_KEY`
   - **Value**: `sk-or-v1-your-api-key-here`
5. Click "Save"
6. Redeploy for changes to take effect

## Custom Domain

### Add Custom Domain

1. Go to project settings in Vercel
2. Click "Domains"
3. Add your domain (e.g., `interview.yourdomain.com`)
4. Follow DNS configuration instructions
5. Wait for SSL certificate to be provisioned

## Automatic Deployments

Once connected to GitHub, Vercel will automatically:

- ✅ Deploy on every push to `main` branch
- ✅ Create preview deployments for pull requests
- ✅ Run build checks
- ✅ Provide deployment status

## Configuration Files

### vercel.json

Create this file in your project root for custom configuration:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

## Troubleshooting

### Build Fails

**Problem**: Build fails in Vercel
**Solution**:

1. Check build logs in Vercel dashboard
2. Ensure `package.json` has correct scripts
3. Verify all dependencies are listed
4. Test build locally: `npm run build`

### Environment Variable Not Working

**Problem**: API key not found
**Solution**:

1. Verify variable name: `VITE_OPENROUTER_API_KEY`
2. Redeploy after adding environment variable
3. Check it's set for all environments
4. Verify no typos in the key

### 404 Errors on Refresh

**Problem**: Page not found when refreshing
**Solution**:

- Add `vercel.json` with rewrite rules (see above)
- Vercel should handle this automatically for Vite

### Camera/Microphone Not Working

**Problem**: Permissions not granted
**Solution**:

- Ensure site uses HTTPS (Vercel provides this)
- Browser requires HTTPS for camera/mic access
- Vercel deployments are always HTTPS

## Performance Optimization

### Enable Edge Functions

Vercel automatically optimizes static assets:

- Compressed assets
- CDN distribution
- Edge caching

### Monitoring

Monitor your deployment:

- Vercel Analytics (free tier available)
- Check "Analytics" tab in project
- Monitor API usage in OpenRouter dashboard

## Cost Considerations

### Vercel Free Tier Includes:

- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ SSL certificates
- ✅ DDoS protection
- ✅ Global CDN

### OpenRouter Free Tier:

- ✅ LLaMA 3.1 8B Instruct
- ✅ Rate limits apply
- ✅ No credit card required

### Estimated Costs:

- **Vercel**: $0/month (free tier)
- **OpenRouter**: $0/month (free tier)
- **Total**: $0/month 🎉

## Security Best Practices

### Environment Variables

- ✅ API key stored in Vercel environment
- ✅ Never commit `.env` to git
- ✅ Use `.env.example` for documentation
- ✅ Rotate keys periodically

### HTTPS

- ✅ Automatic SSL on Vercel
- ✅ Force HTTPS (automatic)
- ✅ Secure cookies (if added)

## Updating Your Deployment

### Push Updates

```bash
git add .
git commit -m "Update feature"
git push
```

Vercel will automatically deploy!

### Manual Redeploy

1. Go to Vercel dashboard
2. Select your project
3. Click "Deployments"
4. Click "..." on a deployment
5. Click "Redeploy"

## Rollback

### Revert to Previous Version

1. Go to "Deployments" in Vercel
2. Find working deployment
3. Click "..." menu
4. Click "Promote to Production"

## Support

### Getting Help

- Vercel Docs: https://vercel.com/docs
- Vercel Discord: https://vercel.com/discord
- OpenRouter Docs: https://openrouter.ai/docs

### Common Issues

1. Check deployment logs
2. Verify environment variables
3. Test locally first
4. Check browser console

---

## Next Steps After Deployment

1. ✅ Test all features
2. ✅ Share your deployment URL
3. ✅ Monitor usage
4. ✅ Gather feedback
5. ✅ Iterate and improve

**Your AI Interviewer is now live! 🎉**
