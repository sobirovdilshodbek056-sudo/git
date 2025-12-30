import os
import yt_dlp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, BufferedInputFile
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Video uchun papka yaratamiz
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply(
        "👋 Salom!\n"
        "📥 Video link yuboring.\n"
        "🎬 YouTube, TikTok, Instagram, Facebook"
    )

@dp.message()
async def download_video(message: types.Message):
    # /start va boshqa buyruqlarni bildirishlari
    if message.text and message.text.startswith("/"):
        return
        
    url = message.text.strip()

    if not url.startswith("http"):
        await message.reply("❌ Iltimos, to‘g‘ri link yuboring")
        return

    await message.reply("⏳ Video yuklanmoqda, kuting...")

    ydl_opts = {
        "format": "worst",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "video.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
        "no_warnings": True,
        "max_filesize": 20000000,
        "socket_timeout": 300,
        "http_chunk_size": 10485760,
        "retries": 5,
        "fragment_retries": 5,
        "skip_unavailable_fragments": True,
        "no_check_certificate": True,
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Yuklanmoqda: {url}")
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Absolyut fayl yo'lini yaratamiz
        file_path = os.path.join(DOWNLOAD_DIR, os.path.basename(filename))
        
        print(f"Fayl: {file_path}")
        print(f"Mavjud: {os.path.exists(file_path)}")

        if os.path.exists(file_path):
            video = FSInputFile(path=file_path)
            await message.answer_video(video)
            os.remove(file_path)
            await message.reply("✅ Video yuborildi!")
        else:
            await message.reply("❌ Video fayl topilmadi")

    except yt_dlp.utils.DownloadError as e:
        await message.reply(f"❌ Yuklab bo'lmadi: Link noto'g'ri yoki video mavjud emas")
    except yt_dlp.utils.ExtractorError as e:
        await message.reply("❌ Bu sayt uchun yt-dlp qo'llab-quvvatlashni to'xtatgan")
    except Exception as e:
        error_msg = str(e)
        print(f"Xato: {error_msg}")
        if "too large" in error_msg.lower():
            await message.reply("❌ Video juda katta (50MB dan ortiq)")
        elif "not found" in error_msg.lower():
            await message.reply("❌ Video topilmadi")
        else:
            await message.reply(f"❌ Xato: {error_msg[:80]}")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot)) 
    