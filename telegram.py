import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3
from datetime import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        category TEXT,
        date TEXT
    )
    """)
    conn.commit()
    conn.close()

# Command to start the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Use /add to record an expense. Use /report to see your expenses.")

# Add expense command
def add_expense(update: Update, context: CallbackContext) -> None:
    try:
        text = " ".join(context.args)
        amount, category = text.split()
        amount = float(amount)
        date = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)", (amount, category, date))
        conn.commit()
        conn.close()
        
        update.message.reply_text(f"Expense recorded: {amount} on {category}")
    except:
        update.message.reply_text("Usage: /add <amount> <category>")

# Show daily report
def daily_report(update: Update, context: CallbackContext) -> None:
    date = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date = ?", (date,))
    total = cursor.fetchone()[0]
    conn.close()
    total = total if total else 0
    update.message.reply_text(f"Today's total expenses: {total}")

# Show monthly report
def monthly_report(update: Update, context: CallbackContext) -> None:
    month = datetime.now().strftime("%Y-%m")
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (month + "%",))
    total = cursor.fetchone()[0]
    conn.close()
    total = total if total else 0
    update.message.reply_text(f"This month's total expenses: {total}")

# Main function to run the bot
def main():
    init_db()
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add_expense))
    dp.add_handler(CommandHandler("report", daily_report))
    dp.add_handler(CommandHandler("monthly", monthly_report))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
