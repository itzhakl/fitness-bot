from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from conversation.user_management import initialize_user_profile
from bot.change_info import update_personal_info

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"ברוך הבא, {user.mention_html()}! 🏋️‍♂️💪\n\n"
        f"אני אלון, מאמן הכושר הווירטואלי האישי שלך. נרגש לעזור לך להשיג את יעדי הכושר שלך ולהפוך לגרסה הטובה ביותר של עצמך.\n\n"
        f"מוכן להתחיל במסע הכושר שלך? בוא נצא לדרך!"
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "הנה כמה דרכים בהן אני יכול לעזור לך:\n\n"
        "🏋️‍♂️ תוכניות אימונים מותאמות אישית\n"
        "🥗 עצות תזונה ותפריטים מומלצים\n"
        "📊 מעקב אחר ההתקדמות שלך\n"
        "❓ מענה לשאלות בנושאי כושר ובריאות\n\n"
        "פשוט שאל אותי כל שאלה, ואני אשמח לעזור!"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    developer_name = "itzhak • יצחק"
    developer_username = "itzhak_il"  # Replace with the actual username
    await update.message.reply_text(
        f"היי! אני אלון, המאמן הווירטואלי שלך לכושר ואורח חיים בריא. 🤖💪\n\n"
        f"נוצרתי כדי לספק לך הדרכה אישית, מוטיבציה ותמיכה בדרך להשגת יעדי הכושר והתזונה שלך. "
        f"אני משלב ידע מקצועי עם גישה אישית כדי לעזור לך להצליח.\n\n"
        f"פותחתי על ידי [{developer_name}](https://t.me/{developer_username}), "
        f"מפתח שרוצה להנגיש אימוני כושר וידע תזונתי איכותי לכולם.\n\n"
        f"בוא נעבוד יחד להשגת המטרות שלך! 💯",
        parse_mode=ParseMode.MARKDOWN
    )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    
    if query:
        await query.answer()
        if query.data == 'update_personal_info':
            await update_personal_info(update, context)
            return
    
    keyboard = [
        [InlineKeyboardButton("עדכון פרטים אישיים", callback_data='update_personal_info')],
        [InlineKeyboardButton("הגדרת יעדי כושר", callback_data='set_fitness_goals')],
        [InlineKeyboardButton("התאמת תדירות התזכורות", callback_data='adjust_reminders')],
        [InlineKeyboardButton("שינוי העדפות שפה", callback_data='change_language')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = "🛠️ הגדרות\n\nבחר את ההגדרה שברצונך לשנות:"
    
    if query:
        await query.edit_message_text(text=message_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=message_text, reply_markup=reply_markup)


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_profile = initialize_user_profile(user_id)
    await update.message.reply_text(
        "👤 הפרופיל שלך\n\n"
        "• נתונים אישיים\n"
        f"שם: {user_profile.name}\n"
        f"מגדר: {user_profile.gender}\n"
        f"גיל: {user_profile.age}\n"
        f"גובה: {user_profile.height}\n"
        f"משקל: {user_profile.weight}\n"
        f"רמת פעילות: {user_profile.activity_level}\n"
        f"מטרות כושר: {user_profile.fitness_goals}\n\n"
        f"לשינוי שלח /settings"
    )