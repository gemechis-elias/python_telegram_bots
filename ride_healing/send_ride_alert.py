import sqlite3
from aiogram import types
from aiogram.types import Message

from my_callback import MyCallback
async def send_new_passenger_notification(dp,username, phone, current, destination , message):
    conn = sqlite3.connect('ride_healing/users.db')
    cursor = conn.cursor()

    try:
        # Fetch user IDs of all users with the 'driver' role
        cursor.execute('SELECT user_id FROM users WHERE role = ?', ('driver',))
        driver_user_ids = [row[0] for row in cursor.fetchall()]

        # Send a notification to each driver
        for user_id in driver_user_ids:
            await message.bot.send_message(user_id, f"🚘 New Ride Alert 🚖 \n\nPassenger Name: {username}\nPhone No:{phone}\nFrom: {current}\nTo: {destination}\n\nPlease accept the ride request by clicking on the button below. \n⚠️ You're revieving this b/c you registered as driver ", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='✅ Accept', callback_data=MyCallback(name="home", id="3").pack())],
                [types.InlineKeyboardButton(text='❌ Reject', callback_data=MyCallback(name="home", id="3").pack())]
            ]))
            print("Notification sent successfully.")
             
    except Exception as e:
        # Handle exceptions (e.g., database errors)
        print(f"Error sending notifications: {e}")

    finally:
        conn.close()
