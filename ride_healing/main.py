# Author : Gemechis Elias
# Date created : Nov 28, 2023
# Description : Ride Healinng Bot
import json
import sqlite3
import asyncio
import random
import re
import logging
import sys
from os import getenv
from datetime import datetime
from aiogram.methods.get_user_profile_photos import GetUserProfilePhotos
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher,types, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup
)
from my_callback import MyCallback
from passenger_role_handler import process_passenger_role
from send_ride_alert import send_new_passenger_notification
from user_profile_handler import process_user_profile
from driver_role_handler import process_driver_role

# Load environment variables from the .env file
load_dotenv()
form_router = Router()

TOKEN = getenv("RIDE_TOKEN")
if TOKEN is None:
    raise ValueError("Telegram token is not set.")

dp = Dispatcher()
    
class Form(StatesGroup):
    id = State()
    fullname = State()
    phone = State()
    role = State()
    date = State()
    history = State()
    current_location = State()
    destination = State()


# START: COMMAND    
@form_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user_id = message.chat.id
    conn = sqlite3.connect('ride_healing/users.db')
    cursor = conn.cursor()

    try:
        # Fetch full name and phone number from the database
        cursor.execute('SELECT fullname, phone, completed_rides FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            menu = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🚘 Book Ride', callback_data=MyCallback(name="ride", id="4").pack()),
            InlineKeyboardButton(text='🔁 Driver Matching', callback_data=MyCallback(name="match", id="5").pack())],
            [InlineKeyboardButton(text='⭐️ Rate Driver', callback_data=MyCallback(name="rate", id="6").pack()),
            InlineKeyboardButton(text='🧾 History', callback_data=MyCallback(name="history", id="7").pack())],
            [InlineKeyboardButton(text='⚙️ Profile', callback_data=MyCallback(name="profile", id="8").pack())],], )
            await message.answer(f"{hbold("Welcome to Ride Healing Bot 🚖")}!\n\nSteer your ride! Where would you like to go?😎\nSelect from features ..  ", reply_markup=menu)
            
        else:
            await state.set_state(Form.fullname)
            menu = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='▶️ Registration', callback_data=MyCallback(name="registration", id="0").pack())]
            ])
            await message.answer(f"Hi, {hbold('Welcome to Ride Healing Bot 🚖')}!\nPlease register to continue.", reply_markup=menu)
    except Exception as e:
        # Handle exceptions (e.g., database errors)
        print(f"Error fetching data from the database: {e}")

    finally:
        conn.close()
# REGISTRATION: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "registration"))
async def my_callback_foo(query: types.CallbackQuery, callback_data: MyCallback):
    await query.message.delete()
    await query.message.answer(f"Please enter your full name to continue.")
    print("Clicked =", callback_data.id)

# FULL NAME: PROCESS
@form_router.message(Form.fullname)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(fullname=message.text)
    await state.update_data(date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    await state.update_data(id=message.chat.id)
    
    await state.set_state(Form.phone)
    await message.answer(
        "Please share your phone number by clicking the button below.",
        reply_markup= ReplyKeyboardMarkup(  keyboard=[
                [
                    KeyboardButton(text="Share Phone Number", request_contact=True),
                ]
            ],resize_keyboard=True),
    )
    
    
# PHONE NUMBER: PROCESS   
@form_router.message(Form.phone)
async def process_phone_number(message: Message, state: FSMContext) -> None:
    # Extract phone number from the message
    phone_number = message.contact.phone_number
    await state.update_data(phone=phone_number)
    await state.set_state(Form.role)
    await message.answer(f"Processing phone number...",  reply_markup=ReplyKeyboardRemove())
    await message.delete()
    role = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🚖 Driver', callback_data=MyCallback(name="driver", id="1").pack()),
        InlineKeyboardButton(text='👤 Passenger', callback_data=MyCallback(name="passenger", id="2").pack())],
                                                                  ])
    await message.answer(f"Are you a driver or passenger.\nPlease, Choose role", reply_markup=role)

# DRIVER: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "driver"))
async def callback_process_driver_role(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext):
    await process_driver_role(query, callback_data, state)

    
# PASSENGER: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "passenger"))
async def callback_process_passenger(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext):
    await process_passenger_role(query, callback_data, state)

        
# HOME MAIN MENU: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "home"))
async def process_home(query: types.CallbackQuery, callback_data: MyCallback):
    await query.message.delete()
    menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🚘 Book Ride', callback_data=MyCallback(name="ride", id="4").pack()),
    InlineKeyboardButton(text='🔁 Driver Matching', callback_data=MyCallback(name="match", id="5").pack())],
    [InlineKeyboardButton(text='⭐️ Rate Driver', callback_data=MyCallback(name="rate", id="6").pack()),
    InlineKeyboardButton(text='🧾 History', callback_data=MyCallback(name="history", id="7").pack())],
    [InlineKeyboardButton(text='⚙️ Profile', callback_data=MyCallback(name="profile", id="8").pack())],], )
    await query.message.answer(f"{hbold("Welcome to Ride Healing Bot 🚖")}!\n\nSteer your ride! Where would you like to go?😎\nSelect from features ..  ", reply_markup=menu)
        



# BOOK RIDE: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "ride"))
async def process_ride(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext):
    await state.set_state(Form.current_location)
    await query.message.answer("Please enter your current location.\ne.g. <i>Bole Medhanialem</i>", parse_mode="HTML")


# CURRENT LOCATION
@form_router.message(Form.current_location)
async def process_current_location(message: Message, state: FSMContext):
    data = await state.get_data()
    current_location = data.get("current_location", [])
    current_location.append(message.text)
    
    await state.update_data(current_location=current_location)
    await message.answer("Now, please enter your destination location.")
    await state.set_state(Form.destination)
    

# DESTINATION
@form_router.message(Form.destination)
async def process_destination(message: Message, state: FSMContext):
    data = await state.get_data()
    destination = data.get("destination", [])
    destination.append(message.text)
    await state.update_data(destination=destination)
    
    user_id = message.chat.id
    conn = sqlite3.connect('ride_healing/users.db')
    cursor = conn.cursor()

    try:
        # Fetch full name and phone number from the database
        cursor.execute('SELECT fullname, phone, completed_rides FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            fullname, phone, current_completed_rides_str = result
            current_completed_rides = json.loads(current_completed_rides_str)
            
            # Process the obtained data as needed
            print("Full Name:", fullname)
            print("Phone Number:", phone)
            print("Curr Location:", data.get("current_location")   )
            print("Destination:", data.get("destination")   )
            print("Current Completed Rides:", current_completed_rides)

        else:
            print("User not found.")

    except Exception as e:
        # Handle exceptions (e.g., database errors)
        print(f"Error fetching data from the database: {e}")

    finally:
        conn.close()
    # ============================== DATABASE ==============================
    current_location = data.get("current_location")
    destination = data.get("destination")

    ride_info = [current_location, destination]
    current_completed_rides.append(ride_info)
    conn = sqlite3.connect('ride_healing/users.db')
    cursor = conn.cursor()

    # Update the completed_rides field in the database
    cursor.execute('UPDATE users SET completed_rides = ? WHERE user_id = ?', (json.dumps(current_completed_rides), user_id))

    conn.commit()
    conn.close()

    
    # Fake progress bar
    progress_message = await message.answer("Calculating time... [                      ]")

    for i in range(1, 11):
        await asyncio.sleep(0.5)  # Simulate some processing time
        bar = "[" + "▬" * i + " " * (10 - i) + "]"
        await progress_message.edit_text(f"⏳Calculating time. \nPlease wait...\n {bar}")
    
    estimated_time = random.randint(5, 30)
    
    menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Back', callback_data=MyCallback(name="home", id="3").pack())]])
    await progress_message.edit_text(f"⏰Estimated arrival time from {message.text} is {hbold(estimated_time)} minutes. \n Your Driver will arrive soon.", reply_markup=menu )
    
    # Send alert to drivers
    await send_new_passenger_notification(dp,fullname, phone, message.text, destination, message)
  

# DRIVER MATCHING: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "match"))
async def process_match(query: types.CallbackQuery, callback_data: MyCallback):
    menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Back', callback_data=MyCallback(name="home", id="3").pack())]])
    await query.message.answer(f"✅ Notification is on.\nYou will be notified when booking ride", reply_markup=menu)
    
# RATE DRIVER: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "rate"))
async def process_rate(query: types.CallbackQuery, callback_data: MyCallback):
    user_id = query.message.chat.id
    conn = sqlite3.connect('ride_healing/users.db')
    cursor = conn.cursor()

    try:
        # Fetch the user's role from the database
        cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            user_role = result[0]

            if user_role == "driver":
                # If the user is a driver, list passengers for rating
                cursor.execute('SELECT user_id, fullname FROM users WHERE role = "passenger"')
                passengers = cursor.fetchall()

                # Display a list of passengers for rating
                if passengers:
                    menu = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=f"Rate {passenger[1]}", callback_data=MyCallback(name="rate_passenger", id=f"{passenger[0]}").pack())]
                        for passenger in passengers
                    ])
                    await query.message.answer("Select a passenger to rate:", reply_markup=menu)
                else:
                    await query.message.answer("No passengers available for rating.")

            elif user_role == "passenger":
                # If the user is a passenger, list drivers for rating
                cursor.execute('SELECT user_id, fullname FROM users WHERE role = "driver"')
                drivers = cursor.fetchall()

                # Display a list of drivers for rating
                if drivers:
                    menu = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=f"Rate - {driver[1]}", callback_data=MyCallback(name="rate_passenger", id=f"{driver[0]}").pack())]
                        for driver in drivers
                    ])
                    await query.message.answer("Select a driver to rate:", reply_markup=menu)
                else:
                    await query.message.answer("No drivers available for rating.")

            else:
                await query.message.answer("User role not recognized.")

        else:
            await query.message.answer("User not found in the database.")

    except Exception as e:
        # Handle exceptions (e.g., database errors)
        print(f"Error fetching data from the database: {e}")

    finally:
        conn.close()

# RATE PASSENGER: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "rate_passenger"))
async def process_rate_passenger(query: types.CallbackQuery, callback_data: MyCallback):
    user_name = callback_data.name
    await query.message.delete()
    await query.message.answer(f"Please rate passenger {user_name}, from 1 to 5 stars.",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                   # stars
                                      [InlineKeyboardButton(text='     ⭐️', callback_data=MyCallback(name="star", id="1").pack())],
                                       [  InlineKeyboardButton(text='   ⭐️⭐️', callback_data=MyCallback(name="star", id="2").pack())],
                                       [  InlineKeyboardButton(text='  ⭐️⭐️⭐️', callback_data=MyCallback(name="star", id="3").pack())],
                                       [  InlineKeyboardButton(text=' ⭐️⭐️⭐️⭐️', callback_data=MyCallback(name="star", id="4").pack())],
                                       [  InlineKeyboardButton(text='⭐️⭐️⭐️⭐️⭐️', callback_data=MyCallback(name="star", id="5").pack())],
                                   
                               ]
                               ))
   
# STAR: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "star"))
async def process_star(query: types.CallbackQuery, callback_data: MyCallback):
    await query.message.delete()
    await query.message.answer(f"✅Thanks for your feedback. \nYour rating has been recorded. \n\n🔙 Back to main menu", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Back', callback_data=MyCallback(name="home", id="3").pack())]]))
    
# DISPLAY HISTORY 1: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "history"))
async def process_history(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext):
    await query.message.delete()

    # Fetch completed rides from the database
    user_id = query.message.chat.id
    conn = sqlite3.connect('ride_healing/users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT completed_rides FROM users WHERE user_id = ?', (user_id,))
    completed_rides_str = cursor.fetchone()[0]
    completed_rides = json.loads(completed_rides_str) if completed_rides_str else []

    conn.close()

    # Process the completed rides (e.g., display it)
    history_text = f"{hbold('🧾 Your Travel History\n\n')}"
    for i, ride_info in enumerate(completed_rides, start=1):
        current, dest = ride_info
        history_text += f"{i}. From: {current}, To: {dest}\n\n\n"

    menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 Back', callback_data=MyCallback(name="home", id="3").pack())]])
    
    await query.message.answer(history_text, reply_markup=menu)
 
# DISPLAY HISTORY 2
@form_router.message(Form.history)
async def display_history(message: Message, state: FSMContext):
    await message.delete()
    
    data = await state.get_data()
    current_location = data.get("current_location", [])
    destination = data.get("destination", [])

    # Process the history (e.g., display it)
    history_text = f"Travel history:\n"
    for i, (current, dest) in enumerate(zip(current_location, destination), start=1):
        history_text += f"{i}. From: {current}, To: {dest}\n"

    await message.answer(history_text)

    
# PROFILE: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "profile"))
async def callback_process_user_profile(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext):
    await process_user_profile(query, state, hbold, MyCallback)
 
# EDIT PROFILE: CALLBACK QUERY
@form_router.callback_query(MyCallback.filter(F.name == "profile_edit"))
async def callback_process_edit_profile(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext):
        await query.message.answer("What's your full name?")
        await From.edit_fullname.set()

# Handle the user's full name input
@form_router.message(state=Form.edit_fullname)
async def process_edit_name(message: Message, state: FSMContext) -> None:
    # Get the user data from the state
    user_id =  message.chat.id

    # Update the user's full name in the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET fullname = ? WHERE user_id = ?', (message.text, user_id))
    conn.commit()
    conn.close()

    # Send a profile updated message
    await message.answer("Your profile has been updated successfully!")

    # Return to the home screen or any other desired behavior
    await process_home(query=types.CallbackQuery, callback_data=MyCallback(name="home", id="3"), state=state) 

# SEE USERS: COMMAND
@form_router.message(Command("users"))
async def command_users(message: Message):
    conn = sqlite3.connect('ride_healing/users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id, fullname, role FROM users')
    users_data = cursor.fetchall()

    conn.close()

    # Format and send the list of users
    if users_data:
        user_list_text = "List of Users:\n"
        for i, (user_id, fullname, role) in enumerate(users_data, start=1):
            user_list_text += f"{i}. {user_id} {fullname}, {role}\n"
        await message.answer(user_list_text)
    else:
        await message.answer("No users found.")


# ============================== MAIN ==============================    
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

