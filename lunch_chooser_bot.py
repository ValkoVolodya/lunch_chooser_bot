import logging
import os
import random

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PollHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

DEFAULT_PLACES = [
    'Shashlikyan',
    'Пивна Дума',
    'Very Well',
    'NUNU',
    'Пузата Хата',
    'Казан Диван',
    'Salateira',
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
    DEFAULT_PLACES.append(place_name)
    await update.message.reply_text(
        f'Заклад {place_name} додано до сьогоднішнього списку варіантів'
    )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Заклади до вибору на сьогодні: {", ".join(DEFAULT_PLACES)}')


async def choose_action_from_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == CHOOSE_BUTTON_TEXT:
        message = await context.bot.send_poll(
            update.effective_chat.id,
            "Виберіть місця, які будуть брати участь в рандомі:",
            DEFAULT_PLACES,
            is_anonymous=True,
            allows_multiple_answers=True,
        )
        payload = {
            message.poll.id: {
                "places": DEFAULT_PLACES,
                "message_id": message.message_id,
                "chat_id": update.effective_chat.id,
                "answers": 0,
            }
        }
        context.bot_data.update(payload)
    if update.message.text == START_RANDOM_BUTTON_TEXT:
        places_to_choose_from = DEFAULT_PLACES
        if len(context.bot_data['CHOSEN_PLACES']) > 0:
            places_to_choose_from = context.bot_data['CHOSEN_PLACES']
        chosen_place = random.choice(places_to_choose_from)
        context.bot_data['CHOSEN_PLACES'] = []
        await update.message.reply_text(f'Сьогодні вибрано {chosen_place}')


async def receive_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.poll.is_closed:
        return
    try:
        poll_data = context.bot_data[update.poll.id]
    except KeyError:
        return

    context.bot_data['CHOSEN_PLACES'] = [
        option.text for option in update.poll.options if option.voter_count > 0
    ]

    await context.bot.stop_poll(poll_data["chat_id"], poll_data["message_id"])


def main() -> None:
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("list2", list_command))
    application.add_handler(CommandHandler("list3", add_command))
    application.add_handler(PollHandler(receive_quiz_answer))

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
