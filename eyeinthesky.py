import os
import time
from telegram.ext import Updater, MessageHandler, filters
from settings import TELEGRAM_JUJUBES_API_KEY
# Replace with your own Telegram bot token
BOT_TOKEN = TELEGRAM_JUJUBES_API_KEY

# Replace with the channel name you want to monitor
CHANNEL_NAME = 'FIRA INDICATOR'

# Replace with the chat ID where you want to receive the alerts
ALERT_CHAT_ID = '-4186260396'

def start_bot():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    channel_handler = MessageHandler(filters.chat(CHANNEL_NAME), handle_channel_message)
    dispatcher.add_handler(channel_handler)

    updater.start_polling()
    print(f'Bot started monitoring {CHANNEL_NAME} channel.')

    # Keep the bot running until you press Ctrl+C
    updater.idle()

def handle_channel_message(update, context):
    message = update.message.text
    print(f'New message received from {CHANNEL_NAME}: {message}')
    context.bot.send_message(chat_id=ALERT_CHAT_ID, text=f'New message from {CHANNEL_NAME}:\n\n{message}')

if __name__ == '__main__':
    start_bot()