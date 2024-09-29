from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import AUTHORISATION_CODE


# קבוע לציון מצב המתנה לקוד
WAITING_FOR_CODE = 1

# מאגר משתמשים מורשים
authorized_users = set()

async def check_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    code = update.message.text
    
    if code == AUTHORISATION_CODE:
        authorized_users.add(user.id)
        await update.message.reply_text("קוד נכון! אתה מורשה להשתמש בבוט.")
        # כאן אתה יכול להוסיף לוגיקה נוספת, כמו שליחה להמשך השיחה
        return ConversationHandler.END
    else:
        await update.message.reply_text("קוד שגוי. נסה שוב או הקלד /start להתחלה מחדש.")
        return WAITING_FOR_CODE

def is_user_authorized(user_id: int) -> bool:
    return user_id in authorized_users

def add_authorized_user(user_id: int):
    authorized_users.add(user_id)