from telegram import Update
from telegram.ext import ContextTypes
from conversation import initialize_user_history

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    initialize_user_history(user.id)
    await update.message.reply_html(
        f"שלום {user.mention_html()}! אני אלון, מאמן הכושר הווירטואלי שלך. כאן כדי לעזור לך להגיע ליעדים שלך. שנתחיל?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("אני יכול לעזור לך בנושאי כושר ותזונה. פשוט שאל אותי כל שאלה!")
