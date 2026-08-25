import os
import asyncio
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

async def main():
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="Supermax Bot is online and working!")
    print("Message sent!")

if __name__ == "__main__":
    asyncio.run(main())
