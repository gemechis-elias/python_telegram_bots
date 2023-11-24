import asyncio
import logging
import sys
from os import getenv
import os
from datetime import datetime
import aiohttp
import requests 
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
# Load environment variables from the .env file
load_dotenv()
 
TOKEN = getenv("TOKEN")
if TOKEN is None:
    raise ValueError("Telegram token is not set. Please set the TELEGRAM_TOKEN environment variable.")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

@dp.message(Command("hello_world"))
async def hello_world_handler(message: Message) -> None:
    """
    Handler for the /hello_world command
    """
    await message.answer("Hello, world!")
    
@dp.message()
async def handle_message(message: types.Message):
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    if message.photo:
        # Download the photo
        file_path = await bot.get_file(message.photo[-1].file_id)
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")

      
        folder_path = "images"

        # Construct the new file path with the current time and folder
        new_file_path = os.path.join(folder_path, f'photo_by_{message.chat.first_name}_{current_time}.jpg')
        async with aiohttp.ClientSession() as session:  # Use aiohttp as a context manager
            async with session.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_path.file_path}') as file:
                # Save the photo
                os.makedirs(folder_path, exist_ok=True)
                with open(new_file_path, 'wb') as f:
                    f.write(await file.read())

       
        # Upload the photo to the OCR API
        with open('photo.jpg', 'rb') as f:
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files={'photo.jpg': f},
                data={'apikey': 'K86055456288957'}
            )

        # Extract the text from the OCR API response
        result = response.json()
        text = result['ParsedResults'][0]['ParsedText']

        # Send the text back to the user if it's not empty
        if text:
            await bot.send_message(chat_id=message.chat.id, text=text)
        else:
            await message.send_copy(chat_id=message.chat.id)
    else:
        # If the message doesn't have a photo, just echo it back
        await message.send_copy(chat_id=message.chat.id)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot("6728616782:AAE7Mm1G6sZlXJSayt13GULtEBWTUMUEJV0", parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
