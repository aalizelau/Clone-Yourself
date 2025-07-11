import logging
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import asyncio

BOT_TOKEN = "YOUR_BOT_TOKEN"  # Your Telegram bot token
IDENTITY_TOKEN = "YOUR_IDENTITY_TOKEN"  # Token for authenticating with your backend
TARGET_URL = "YOUR_BACKEND_URL"  # API endpoint to send messages to fine-tuned model


logging.basicConfig(level=logging.INFO)

# This function runs whenever the bot receives a message
async def relay_to_backend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

     # Construct ChatML input prompt
    prompt = f"<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.5,
            "top_p": 0.65,
            "repetition_penalty": 1.2
        }
    }

    headers = {
        "Authorization": f"Bearer {IDENTITY_TOKEN}",
        "Content-Type": "application/json"
    }

    # Send user message to your external backend
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    async with aiohttp.ClientSession() as session:
        logging.info(f"Sending message to backend: {user_message}")
        async with session.post(TARGET_URL, json=payload, headers=headers) as response:
            logging.info(f"Received response from backend: {response.status}")
            if response.status == 200:
                result_json = await response.json()
                text = result_json[0]["generated_text"]

                # Strip out the prompt and just keep the assistant’s reply
                if "<|im_start|>assistant\n" in text:
                    reply = text.split("<|im_start|>assistant\n", 1)[1]
                else:
                    reply = text
            else:
                reply = "Sorry, something went wrong with the backend."

    # Send the response back to the user
    await context.bot.send_message(chat_id=chat_id, text=reply)


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, relay_to_backend))
    app.run_polling()
