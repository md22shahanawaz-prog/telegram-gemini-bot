import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Get tokens from Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# Initialize Telegram Application
tg_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your Gemini AI chatbot. Ask me anything!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # Generate response from Gemini
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("Sorry, I had trouble thinking about that.")

# Add handlers to Telegram
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route('/webhook', methods=['POST'])
async def webhook():
    # Process the update from Telegram
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), tg_app.bot)
        await tg_app.initialize()
        await tg_app.process_update(update)
        return "OK", 200

@app.route('/')
def home():
    return "Bot is running live!", 200

if __name__ == '__main__':
    app.run(port=5000)
