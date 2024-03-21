import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from settings import TELEGRAM_TRAVELLER_API_KEY, GEMINI_API_KEY
import requests
from PIL import Image
from io import BytesIO
import os 


from llm_handler.GHandler import GHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Traveller here! Send me an image of your travel itinerary and I will digitise it for you!")

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the message is a reply to the bot or mentions the bot in a group
    chat_type = update.effective_chat.type

    if chat_type  == "private":
        process_image = True
    elif chat_type in ["group", "supergroup"]:
        process_image = any(
            mention.user.id == context.bot.id for mention in update.message.entities
        )
    elif update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot:
        process_image = True
    elif update.message.entities and any(ent.type == "mention" for ent in update.message.entities):
        process_image = True
    else:
        process_image = False

    if not process_image:
        return  # Ignore the message if it's not directed at the bot

    if not update.message.photo:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I can only process images!")
        return
    

    if not update.message.photo:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I can only process images!")
        return

    file = await context.bot.get_file(update.message.photo[-1].file_id)
    response = requests.get(file.file_path)
    img = Image.open(BytesIO(response.content))
    
    # Save the image file locally
    file_name = f"{update.message.photo[-1].file_unique_id}.jpg"  # Change the extension if needed
    file_path = os.path.join("./database/travel/telegram/", file_name)

    # Get the caption of the photo, if any
    caption = update.message.caption or ""
    # You can add image processing logic here (e.g., resize, convert format)
    text = f"Image ({caption}) received\n ---> <Gemini> processing..."  # Update message after processing
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    with open(file_path, "wb") as f:
        f.write(response.content) 
    # ANALYSES HERE
    prompt_1 = """The image is a travel itinerary that i want to digitise so that i can populate a database. 
                Help analyse the content and reproduce it in a structured format such that it is easily extractable
                """
    g_handler = GHandler(GEMINI_API_KEY,                  
                generation_config = {"temperature": 0.9,
                                    "top_p": 0.95,
                                    "top_k": 40,
                                    "max_output_tokens": 1024,
                                    },
                block_threshold="BLOCK_NONE",
                )
    
    g_response = g_handler.prompt_image(model_name = "gemini-pro-vision",
                                  image_path = file_path,
                                  prompt_1 = prompt_1,
                                  prompt_2 = None,
                                        )
    # LLM analyse image

    await context.bot.send_message(chat_id=update.effective_chat.id, text=g_response.text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TRAVELLER_API_KEY).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Create a MessageHandler instance for image_handler
    image_handler_instance = MessageHandler(filters.PHOTO, image_handler)
    application.add_handler(image_handler_instance)

    application.run_polling()