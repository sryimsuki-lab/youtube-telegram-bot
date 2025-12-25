# How to Deploy Your YouTube to MP3 Telegram Bot on Render.com (FREE 24/7)

## Step 1: Get Your Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the **Bot Token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Keep this token safe - you'll need it later

## Step 2: Prepare Your Code

1. Create a **GitHub account** if you don't have one (https://github.com)
2. Create a **new repository** (click + button → New repository)
3. Name it something like `youtube-mp3-bot`
4. Make it **Public**
5. Click **Create repository**

## Step 3: Upload Your Code to GitHub

### Option A: Using GitHub Web Interface (Easiest)
1. In your new repository, click **Add file** → **Upload files**
2. Drag these files:
   - `main.py`
   - `requirements.txt`
   - `Procfile`
3. Click **Commit changes**

### Option B: Using Git (If you know how)
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## Step 4: Deploy to Render.com

1. Go to **https://render.com** and sign up (use your GitHub account to sign up - it's easier)

2. Click **New** → **Web Service**

3. Click **Connect** next to your GitHub repository (`youtube-mp3-bot`)

4. Fill in the settings:
   - **Name:** `youtube-mp3-bot` (or any name you like)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Instance Type:** `Free`

5. Scroll down to **Environment Variables** section

6. Click **Add Environment Variable**
   - **Key:** `TELEGRAM_BOT_TOKEN`
   - **Value:** Paste your bot token from Step 1

7. Click **Add Environment Variable** again
   - **Key:** `PORT`
   - **Value:** `8080`

8. Click **Create Web Service**

## Step 5: Wait for Deployment

- Render will install dependencies (this takes 3-5 minutes)
- You'll see logs showing the installation progress
- When you see "Bot started!" in the logs, your bot is ready!

## Step 6: Test Your Bot

1. Open Telegram
2. Search for your bot (the name you gave in Step 1)
3. Send `/start`
4. Send a YouTube link like: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
5. Wait for the MP3 file!

## Important Notes

### ✅ What This Setup Does:
- **24/7 Running:** Flask keeps the bot alive on Render's free tier
- **Auto-Delete Files:** Files are deleted after sending to save storage
- **Khmer Support:** Handles Unicode characters correctly
- **Free Hosting:** Completely free on Render

### ⚠️ Render Free Tier Limitations:
- **Auto-Sleep:** If no requests for 15 minutes, it sleeps (wakes up when someone uses bot)
- **750 Hours/Month:** Your bot can run about 31 days straight (enough for 24/7)
- **Storage:** Limited, but we delete files after sending

### 🔧 Troubleshooting:

**Bot doesn't respond?**
- Check Render logs for errors
- Make sure TELEGRAM_BOT_TOKEN is set correctly
- Click "Manual Deploy" → "Deploy latest commit" to restart

**"Sign in to confirm you're not a bot" error?**
- YouTube now requires cookies for downloads
- Bot uses Chrome cookies automatically
- On Render/cloud servers, you'll need to provide a cookies.txt file:
  1. Export YouTube cookies using a browser extension (like "Get cookies.txt LOCALLY")
  2. Upload cookies.txt to your repository
  3. The bot will auto-detect it

**"FFmpeg not found" error?**
- Render should have FFmpeg installed by default
- If not, create a file called `apt-packages` with one line: `ffmpeg`

**Bot sleeps too often?**
- This is normal on free tier
- First message after sleep takes 30-60 seconds
- Consider using UptimeRobot.com to ping your bot every 5 minutes (free)

## How to Keep Bot Awake (Optional)

1. Go to **https://uptimerobot.com** and sign up (free)
2. Click **Add New Monitor**
3. Settings:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** YouTube Bot
   - **URL:** Your Render app URL (like `https://youtube-mp3-bot.onrender.com`)
   - **Monitoring Interval:** 5 minutes
4. Click **Create Monitor**

This pings your bot every 5 minutes to keep it awake!

## How to Update Your Bot

1. Make changes to your code locally
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Updated bot"
   git push
   ```
3. Render will **automatically redeploy** (if you enabled auto-deploy)
4. Or click **Manual Deploy** in Render dashboard

## Need Help?

- Check Render logs (Dashboard → Your Service → Logs)
- Make sure bot token is correct
- Verify all files are uploaded to GitHub
- Test bot with simple YouTube links first

---

**Your bot is now running 24/7 for FREE! 🎉**
