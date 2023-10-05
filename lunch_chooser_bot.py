import logging
import os
import random

from telegram import ForceReply, Update
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

PLACES = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    place_name = update.message.text.removeprefix("/add ")
    PLACES.append({"name": place_name})
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


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


def main() -> None:
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("choose", choose_command))
    application.add_handler(CommandHandler("list", list_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

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
