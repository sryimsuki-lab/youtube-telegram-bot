# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-platform Telegram music downloader bot. Supports YouTube (videos/playlists), SoundCloud, and Spotify.

**Dependencies:**
- `python-telegram-bot==21.0.1` - Telegram integration
- `yt-dlp[default]==2025.12.8` - Video/audio downloading (includes yt-dlp-ejs)
- `Flask==3.1.0` - Keep-alive server for cloud hosting
- FFmpeg (system dependency) - Audio conversion
- Node.js (system dependency) - Required for YouTube signature solving

## Features

✅ **Multi-Platform Support**: YouTube, SoundCloud, Spotify
✅ **Playlist Downloads**: Full YouTube playlist support
✅ **Album Art**: Embedded thumbnails in MP3 files
✅ **Progress Updates**: Real-time download percentage (every 10%)
✅ **Smart Error Messages**: User-friendly error descriptions
✅ **Age-Restricted Videos**: Handles with proper cookies
✅ **Optimized Speed**: Parallel fragment downloads, 128kbps MP3

## Architecture

**Single-file application** (`main.py`):
- Flask server (daemon thread) - health checks on port 8080
- Telegram bot (main thread) - `run_polling()`
- Async download handler with progress hooks
- Temp files in `temp_downloads/`, auto-deleted after sending

**Download Flow:**
1. URL validation (YouTube/SoundCloud/Spotify regex)
2. Progress message sent to user
3. yt-dlp downloads with `tv_embedded` player client
4. FFmpeg converts to MP3 (128kbps)
5. Thumbnail downloaded and sent with audio
6. Metadata added (title, performer, duration)
7. Files cleaned up

**YouTube Age-Restricted Video Handling:**
- Requires `cookies.txt` with age-verified account
- Uses `tv_embedded` player client to bypass signature challenges
- `age_limit: None` to disable age restrictions
- Export cookies AFTER confirming age on restricted video

## Environment Variables

Required:
- `TELEGRAM_BOT_TOKEN` - Get from @BotFather on Telegram

Optional:
- `PORT` - Default 8080 (for Flask health check endpoint)

## Running the Bot

```bash
# Install dependencies
pip3 install -r requirements.txt

# Set token from BotFather
export TELEGRAM_BOT_TOKEN="your_token_here"

# Run locally
python3 main.py

# Kill all instances before restarting (IMPORTANT!)
pkill -9 -f "python3 main.py" && sleep 3 && python3 main.py
```

## Critical yt-dlp Configuration

```python
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,  # IMPORTANT: Prevents Mix playlists (1000+ tracks)
    'progress_hooks': [progress_hook],  # Real-time progress tracking
    'concurrent_fragment_downloads': 16,  # Fast parallel downloads
    'http_chunk_size': 20971520,  # 20MB chunks for speed
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }, {
        'key': 'EmbedThumbnail',
    }],
    'writethumbnail': True,
    'buffersize': 16384,
    'retries': 10,
    'fragment_retries': 10,
}
```

**Note**: Chrome cookies and Node.js runtime removed for Railway compatibility.

## Cookies Management

**Auto-loading from Chrome** - NO manual export needed:
- Bot uses `cookiesfrombrowser: ('chrome')` to auto-load cookies
- Just stay logged into YouTube in Chrome
- Cookies are always fresh, no manual updates required
- Works for age-restricted videos automatically

## Common Issues FIXED

**Age-restricted videos / "Requested format is not available"**:
- ✅ FIXED: Install `yt-dlp[default]` which includes yt-dlp-ejs
- ✅ FIXED: Enable Node.js runtime in config
- ✅ FIXED: Use auto cookies from Chrome

**Downloading 1000+ tracks from single video**:
- ✅ FIXED: Set `noplaylist: True` to prevent Mix playlists
- YouTube auto-creates Mix playlists - now ignored

**Multiple bot instances conflict**:
- Kill old: `pkill -9 -f "python3 main.py"`
- Verify: `ps aux | grep "[P]ython main.py"`

**Progress updates now work**:
- ✅ FIXED: Real-time progress bar implemented
- Shows "⏬ Downloading: X%" every 5% or 2 seconds
- Shows "🔄 Converting to MP3..." during conversion
- Uses async task with thread executor for non-blocking updates

## Deployment

**Currently Deployed on Railway.app** - Running 24/7

Railway.com free tier ($5/month credit, ~500 hours). Auto-deploys from GitHub.

**Setup:**
1. Connect GitHub repo: https://github.com/sryimsuki-lab/youtube-telegram-bot
2. Set environment variable: `TELEGRAM_BOT_TOKEN`
3. Railway uses Dockerfile to install FFmpeg automatically
4. Flask on port 8080 keeps service alive

**Files for Deployment:**
- `Dockerfile` - Python 3.13 + FFmpeg
- `requirements.txt` - Python dependencies
- `main.py` - Bot application

See DEPLOYMENT.md for detailed instructions.

## System Dependencies

- FFmpeg (required for audio conversion)
- Python 3.14
- Chrome browser (for cookie extraction)

## Development Guidelines

### Tone and Communication Style
- Be concise, direct, and to the point
- Answer with fewer than 4 lines unless detail is requested
- Minimize output tokens while maintaining helpfulness
- No unnecessary preambles or postambles
- Answer questions directly without elaboration
- Do not add code explanations or summaries unless requested

### Code Style
- DO NOT ADD ANY COMMENTS unless explicitly asked
- Follow existing code conventions in the repository
- Check existing patterns, libraries, and frameworks before making changes
- Never assume a library is available - verify in requirements.txt first
- Follow security best practices - never expose or log secrets/keys

### Task Management
- Use TodoWrite tool frequently for tracking tasks
- Break down complex tasks into smaller steps
- Mark todos as completed immediately after finishing each task
- Do not batch multiple completions

### Testing and Validation
- Never assume specific test framework or test script
- Check README or search codebase to determine testing approach
- Run lint and typecheck commands after completing tasks (if available)

### Git and Commits
- NEVER commit changes unless explicitly asked
- Only commit when the user explicitly requests it

### Tool Usage
- Use Task tool for file search to reduce context usage
- Use specialized agents proactively when task matches agent description
- Batch independent tool calls together in parallel
- Use dedicated tools instead of bash commands for file operations (Read, Edit, Write)

### Security
- Assist with defensive security tasks only
- Refuse to create, modify, or improve code that may be used maliciously
- Allow security analysis, detection rules, vulnerability explanations, defensive tools, and security documentation
