from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = '8501659678:AAHx1IeNKd--QIFSC2WI_A9IU3O8IbdWUdQ'
BOT_USERNAME: Final = "@failprint_bot"

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Thanks for using our bot!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Our bot will monitor the images it receives from Raspberry Pi and will tell you if your print goes wrong.")

async def status_command(update, context):
    await update.message.reply_text(
        "📡 Bot is online and waiting for Raspberry Pi messages."
    )


def main():
    print("Starting bot...")

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))

    # Run bot
    app.run_polling()

if __name__ == "__main__":
    main()