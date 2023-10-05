import logging
import os
import random

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

PLACES = [
    'Shashlikyan',
    'Пивна Дума',
    'Very Well',
    'NUNU',
]

CHOOSE_BUTTON_TEXT = "Вибрати варіанти на сьогодні"
START_RANDOM_BUTTON_TEXT = "Запустити рандом"

START_BUTTONS = [
    [CHOOSE_BUTTON_TEXT],
    [START_RANDOM_BUTTON_TEXT],
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Привіт, {user.mention_html()}!"
        rf"Я створений для зручного вибору місця обіду.",
        reply_markup=ReplyKeyboardMarkup(START_BUTTONS),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    place_name = update.message.text.removeprefix("/add ")
    PLACES.append(place_name)
    await update.message.reply_text(
        f'Заклад {place_name} додано до сьогоднішнього списку варіантів'
    )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Заклади до вибору на сьогодні: {", ".join(PLACES)}')


async def choose_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(PLACES) < 1:
        await update.message.reply_text("Не можу вибрати заклад, бо немає варіантів(")
        return
    await update.message.reply_text(f'Сьогодні вибрано {random.choice(PLACES)["name"]}')


async def choose_action_from_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == CHOOSE_BUTTON_TEXT:
        message = await context.bot.send_poll(
            update.effective_chat.id,
            "Виберіть місця, які будуть брати участь в рандомі:",
            PLACES,
            is_anonymous=True,
            allows_multiple_answers=True,
        )
        payload = {
            message.poll.id: {
                "questions": PLACES,
                "message_id": message.message_id,
                "chat_id": update.effective_chat.id,
                "answers": 0,
            }
        }
        context.bot_data.update(payload)
    if update.message.text == START_RANDOM_BUTTON_TEXT:
        await update.message.reply_text(f'Сьогодні вибрано {random.choice(PLACES)}')


def main() -> None:
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("choose", choose_command))
    application.add_handler(CommandHandler("list", list_command))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, choose_action_from_button)
    )

    if os.getenv("DEPLOY"):
        application.run_webhook(
            listen='0.0.0.0',
            port=os.getenv("PORT"),
            webhook_url=os.getenv("WEBHOOK_URL"),
        )
    else:
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
