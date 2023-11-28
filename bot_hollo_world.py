# Author : Gemechis Elias
# Date created : Nov 28, 2023
# Description : Simple Bot Command

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
    await message.send_copy(chat_id=message.chat.id)
        


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
