# Author : Gemechis Elias
# Date created : Nov 28, 2023
# Description : Simple Bot with Inline button

import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

# Load environment variables from the .env file
load_dotenv()

TOKEN = getenv("TOKEN")
if TOKEN is None:
    raise ValueError("Telegram token is not set. Please set the TOKEN environment variable.")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {message.from_user.full_name}!")


@dp.message(Command("hello_world"))
async def hello_world_handler(message: Message) -> None:
    """
    Handler for the /hello_world command
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("Yes", callback_data="happy_yes"), InlineKeyboardButton("No", callback_data="happy_no"))

    await message.answer("Are you happy today?", reply_markup=keyboard)


# @dp.message.callback_query_handler(lambda c: c.data.startswith('happy_'))
# async def process_callback_query(callback_query: types.CallbackQuery):
#     answer = callback_query.data.split('_')[1]
#     await dp.bot.send_message(callback_query.from_user.id, f"You are {'happy' if answer == 'yes' else 'not happy'} today!")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
