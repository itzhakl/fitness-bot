from telegram.ext import CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from conversation.user_management import update_user_profile

# Define states for the conversation
(NAME, GENDER, AGE, HEIGHT, WEIGHT, ACTIVITY_LEVEL, FITNESS_GOALS) = range(7)

async def update_personal_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("בוא נעדכן את הפרטים האישיים שלך. מה השם שלך?")
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("תודה! מה המגדר שלך? (זכר/נקבה/אחר)")
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gender'] = update.message.text
    await update.message.reply_text("מה הגיל שלך?")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['age'] = update.message.text
    await update.message.reply_text("מה הגובה שלך בס\"מ?")
    return HEIGHT

async def height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['height'] = update.message.text
    await update.message.reply_text("מה המשקל שלך בק\"ג?")
    return WEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['weight'] = update.message.text
    await update.message.reply_text("מה רמת הפעילות שלך? (נמוכה/בינונית/גבוהה)")
    return ACTIVITY_LEVEL

async def activity_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['activity_level'] = update.message.text
    await update.message.reply_text("מה המטרה שלך בתחום הכושר והבריאות?")
    return FITNESS_GOALS

async def fitness_goals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['fitness_goals'] = update.message.text
    
    update_user_profile(update.effective_user.id, context.user_data)

    await update.message.reply_text(
        f"תודה! הנה הפרטים שעדכנת:\n"
        f"שם: {context.user_data['name']}\n"
        f"מגדר: {context.user_data['gender']}\n"
        f"גיל: {context.user_data['age']}\n"
        f"גובה: {context.user_data['height']} ס\"מ\n"
        f"משקל: {context.user_data['weight']} ק\"ג\n"
        f"רמת פעילות: {context.user_data['activity_level']}\n"
        f"מטרה בכושר ובריאות: {context.user_data['fitness_goals']}"
    )
    
    return ConversationHandler.END

async def cancel(update: Update) -> int:
    await update.message.reply_text("עדכון הפרטים האישיים בוטל.")
    return ConversationHandler.END

# Add this to your main function or wherever you set up your application
update_personal_info_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(update_personal_info, pattern='^update_personal_info$')],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
        GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
        ACTIVITY_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, activity_level)],
        FITNESS_GOALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, fitness_goals)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

