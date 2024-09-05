import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import schedule
import time
from datetime import datetime, timedelta

BOT_TOKEN = '1123674437:AAGnL_lLkmM8uPro6oALQNFA-MBh9M1Vio8'
bot = telebot.TeleBot(BOT_TOKEN)

reminders = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "ברוך הבא! השתמש ב-/set_reminder כדי להגדיר תזכורת חדשה, /view_reminders לצפייה בתזכורות, /edit_reminder לעריכה ו-/delete_reminder למחיקה.")

@bot.message_handler(commands=['set_reminder'])
def set_reminder(message):
    markup = InlineKeyboardMarkup()
    today = datetime.now()
    for i in range(7):
        date = today + timedelta(days=i)
        markup.add(InlineKeyboardButton(date.strftime("%d/%m/%Y"), callback_data=f"date_{date.strftime('%Y-%m-%d')}"))
    bot.reply_to(message, "בחר תאריך:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('date_'))
def callback_date(call):
    date = call.data.split('_')[1]
    markup = InlineKeyboardMarkup()
    for hour in range(0, 24, 2):
        markup.add(InlineKeyboardButton(f"{hour:02d}:00", callback_data=f"time_{date}_{hour:02d}:00"),
                  InlineKeyboardButton(f"{hour:02d}:30", callback_data=f"time_{date}_{hour:02d}:30"))
    bot.edit_message_text("בחר שעה:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('time_'))
def callback_time(call):
    date_time = call.data.split('_')[1:]
    bot.edit_message_text(f"נבחר: {date_time[0]} {date_time[1]}\nעכשיו הקלד את תוכן התזכורת:", call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, save_reminder, date_time)

def save_reminder(message, date_time):
    content = message.text
    reminder_time = datetime.strptime(f"{date_time[0]} {date_time[1]}", '%Y-%m-%d %H:%M')
    user_id = message.from_user.id
    
    if user_id not in reminders:
        reminders[user_id] = []
    
    reminders[user_id].append((reminder_time, content))
    schedule_reminder(user_id, reminder_time, content)
    bot.reply_to(message, f"תזכורת נקבעה ל-{reminder_time.strftime('%Y-%m-%d %H:%M')}: {content}")

@bot.message_handler(commands=['view_reminders'])
def view_reminders(message):
    user_id = message.from_user.id
    if user_id not in reminders or not reminders[user_id]:
        bot.reply_to(message, "אין לך תזכורות מוגדרות.")
        return
    
    response = "התזכורות שלך:\n"
    for idx, (reminder_time, content) in enumerate(reminders[user_id], 1):
        response += f"{idx}. {reminder_time.strftime('%Y-%m-%d %H:%M')} - {content}\n"
    bot.reply_to(message, response)

@bot.message_handler(commands=['edit_reminder'])
def edit_reminder(message):
    user_id = message.from_user.id
    if user_id not in reminders or not reminders[user_id]:
        bot.reply_to(message, "אין לך תזכורות לערוך.")
        return
    
    markup = InlineKeyboardMarkup()
    for idx, (reminder_time, content) in enumerate(reminders[user_id], 1):
        markup.add(InlineKeyboardButton(f"{idx}. {reminder_time.strftime('%Y-%m-%d %H:%M')} - {content}", callback_data=f"edit_{idx}"))
    
    bot.reply_to(message, "בחר תזכורת לעריכה:", reply_markup=markup)

@bot.message_handler(commands=['delete_reminder'])
def delete_reminder(message):
    user_id = message.from_user.id
    if user_id not in reminders or not reminders[user_id]:
        bot.reply_to(message, "אין לך תזכורות למחוק.")
        return
    
    markup = InlineKeyboardMarkup()
    for idx, (reminder_time, content) in enumerate(reminders[user_id], 1):
        markup.add(InlineKeyboardButton(f"{idx}. {reminder_time.strftime('%Y-%m-%d %H:%M')} - {content}", callback_data=f"delete_{idx}"))
    
    bot.reply_to(message, "בחר תזכורת למחיקה:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('edit_', 'delete_')))
def callback_query(call):
    user_id = call.from_user.id
    action, idx = call.data.split('_')
    idx = int(idx) - 1
    
    if action == 'edit':
        bot.answer_callback_query(call.id, "אנא הזן את הפרטים החדשים בפורמט: YYYY-MM-DD HH:MM תוכן_חדש")
        bot.register_next_step_handler(call.message, edit_reminder_step, idx)
    elif action == 'delete':
        del reminders[user_id][idx]
        bot.answer_callback_query(call.id, "התזכורת נמחקה בהצלחה")
        bot.edit_message_text("התזכורת נמחקה בהצלחה", call.message.chat.id, call.message.message_id)

def edit_reminder_step(message, idx):
    try:
        date_time_str, content = message.text.split(' ', 1)
        reminder_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
        user_id = message.from_user.id
        reminders[user_id][idx] = (reminder_time, content)
        schedule_reminder(user_id, reminder_time, content)
        bot.reply_to(message, f"התזכורת עודכנה ל-{reminder_time.strftime('%Y-%m-%d %H:%M')}: {content}")
    except:
        bot.reply_to(message, "פורמט לא תקין. אנא נסה שוב.")

@bot.message_handler(func=lambda message: True)
def handle_reminder(message):
    try:
        date_time_str, content = message.text.split(' ', 1)
        reminder_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
        user_id = message.from_user.id
        
        if user_id not in reminders:
            reminders[user_id] = []
        
        reminders[user_id].append((reminder_time, content))
        schedule_reminder(user_id, reminder_time, content)
        bot.reply_to(message, f"תזכורת נקבעה ל-{reminder_time.strftime('%Y-%m-%d %H:%M')}: {content}")
    except:
        bot.reply_to(message, "פורמט לא תקין. אנא נסה שוב.")

def schedule_reminder(user_id, reminder_time, content):
    schedule.every().day.at(reminder_time.strftime("%H:%M")).do(send_reminder, user_id, content).tag(f"user_{user_id}")

def send_reminder(user_id, content):
    bot.send_message(user_id, f"תזכורת: {content}")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

import threading
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

bot.polling()
