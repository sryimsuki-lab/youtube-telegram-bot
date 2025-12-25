import os
import logging
import asyncio
import shutil
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread
import yt_dlp
import re
import requests
from io import BytesIO

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 សួស្តី! Welcome to the Ultimate Music Downloader! 🎉\n"
        "🎶 Turn any link into MP3 magic! ✨\n\n"
        "🔥 What I Can Do:\n"
        "📺 YouTube videos & playlists → MP3\n"
        "🎧 SoundCloud tracks → MP3\n"
        "🎵 Spotify tracks → MP3 (limited)\n"
        "🖼️ Beautiful album art included!\n"
        "📊 Real-time download progress\n"
        "⚡ Lightning-fast downloads (128kbps)\n\n"
        "💡 How to use:\n"
        "Just paste any music link and watch the magic happen! 🪄\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Created by @nimseyhamanith 🚀"
    )

async def download_and_convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text

    url_patterns = {
        'youtube': r'(https?://)?(www\.)?(youtube\.com/(watch\?v=|playlist\?list=)|youtu\.be/)([a-zA-Z0-9_-]+)',
        'soundcloud': r'(https?://)?(www\.)?(soundcloud\.com|snd\.sc)/[\w\-/]+',
        'spotify': r'(https?://)?(open\.)?(spotify\.com)/(track|playlist|album)/([a-zA-Z0-9]+)'
    }

    platform = None
    for name, pattern in url_patterns.items():
        if re.search(pattern, message):
            platform = name
            break

    if not platform:
        await update.message.reply_text("❌ Please send a valid link (YouTube, SoundCloud, or Spotify).")
        return

    progress_msg = await update.message.reply_text("⏬ Starting download...")

    progress_data = {'percent': 0, 'status': 'downloading'}

    def progress_hook(d):
        if d['status'] == 'downloading':
            if 'downloaded_bytes' in d and 'total_bytes' in d:
                progress_data['percent'] = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'downloaded_bytes' in d and 'total_bytes_estimate' in d:
                progress_data['percent'] = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
        elif d['status'] == 'finished':
            progress_data['status'] = 'converting'

    async def update_progress():
        last_percent = 0
        last_update_time = 0
        while progress_data['status'] not in ['done', 'error']:
            current_percent = int(progress_data['percent'])
            current_time = asyncio.get_event_loop().time()

            # Update if 5% change OR 2 seconds passed
            if (current_percent - last_percent >= 5) or (current_time - last_update_time >= 2 and current_percent > last_percent):
                try:
                    if progress_data['status'] == 'downloading' and current_percent > 0:
                        await progress_msg.edit_text(f"⏬ Downloading: {current_percent}%")
                        last_percent = current_percent
                        last_update_time = current_time
                    elif progress_data['status'] == 'converting':
                        await progress_msg.edit_text("🔄 Converting to MP3...")
                        last_update_time = current_time
                except:
                    pass
            await asyncio.sleep(0.5)

    update_task = asyncio.create_task(update_progress())

    try:
        temp_dir = 'temp_downloads'
        os.makedirs(temp_dir, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }, {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            }],
            'writethumbnail': True,
            'noplaylist': True,
            'progress_hooks': [progress_hook],
            'concurrent_fragment_downloads': 4,
            'http_chunk_size': 10485760,
            'buffersize': 16384,
            'retries': 10,
            'fragment_retries': 10,
        }

        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(message, download=True)

        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, download)

        progress_data['status'] = 'done'
        update_task.cancel()

        entries = info.get('entries', [info])

        if len(entries) > 1:
            await progress_msg.edit_text(f"📝 Found {len(entries)} tracks in playlist!")

        for idx, entry in enumerate(entries, 1):
            if not entry:
                continue

            title = entry['title']
            file_path = f"{temp_dir}/{title}.mp3"

            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue

            performer = entry.get('uploader') or entry.get('channel') or 'Unknown Artist'
            duration = int(entry.get('duration', 0))

            thumbnail_url = entry.get('thumbnail')
            thumbnail_data = None

            if thumbnail_url:
                try:
                    response = requests.get(thumbnail_url, timeout=10)
                    if response.status_code == 200:
                        thumbnail_data = BytesIO(response.content)
                except:
                    pass

            if len(entries) > 1:
                await progress_msg.edit_text(f"⏫ Uploading {idx}/{len(entries)}: {title[:30]}...")
            else:
                await progress_msg.edit_text("⏫ Uploading MP3...")

            with open(file_path, 'rb') as audio:
                await update.message.reply_audio(
                    audio=audio,
                    title=title,
                    performer=performer,
                    duration=duration,
                    thumbnail=thumbnail_data if thumbnail_data else None,
                    filename=f"{title}.mp3"
                )

            os.remove(file_path)

            for ext in ['.jpg', '.png', '.webp']:
                thumb_path = f"{temp_dir}/{title}{ext}"
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)

            logger.info(f"File {file_path} deleted after sending")

        await progress_msg.edit_text(f"✅ Done! Sent {len(entries)} track(s)! 🎧")

    except Exception as e:
        progress_data['status'] = 'error'
        update_task.cancel()
        logger.error(f"Error: {str(e)}")

        error_msg = "❌ "
        error_str = str(e).lower()

        if 'sign in' in error_str or 'bot' in error_str or 'age' in error_str or 'cookies' in error_str:
            error_msg += "Please make sure you're logged into YouTube in Chrome and have confirmed your age on age-restricted videos. Then restart the bot."
        elif 'signature' in error_str or 'js runtime' in error_str or 'ejs' in error_str or 'challenge' in error_str or 'remote component' in error_str:
            error_msg += "YouTube signature solving failed. Install Node.js and allow EJS remote components, then retry."
        elif '429' in error_str or 'too many requests' in error_str:
            error_msg += "Server is temporarily blocked by YouTube (Rate Limit). Please try again later."
        elif 'format' in error_str or 'available' in error_str:
            error_msg += "Video format not available. This might be a restricted video."
        elif 'private' in error_str or 'unavailable' in error_str:
            error_msg += "Video is private or unavailable."
        elif 'copyright' in error_str:
            error_msg += "Video is copyright protected and cannot be downloaded."
        elif 'geo' in error_str or 'region' in error_str:
            error_msg += "Video is not available in this region."
        elif 'network' in error_str or 'connection' in error_str:
            error_msg += "Network error. Please try again."
        elif 'spotify' in error_str:
            error_msg += "Spotify downloads require premium account. Try YouTube instead."
        else:
            error_msg += f"Download failed. Please try again or use a different link."

        await progress_msg.edit_text(error_msg)

        try:
            for f in os.listdir(temp_dir):
                if f.endswith(('.mp3', '.jpg', '.png', '.webp', '.part')):
                    os.remove(os.path.join(temp_dir, f))
        except:
            pass

def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    application = Application.builder().token(token).connect_timeout(30).read_timeout(30).write_timeout(30).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_convert))

    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
