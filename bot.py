"""Kichkina tabib - generates greeting/quote card images from a message.

Run: BOT_TOKEN=xxxxx python3 bot.py  (or put BOT_TOKEN in a .env file)
"""
import io
import logging
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
from imagegen.card import compose_card, compose_status
from quote_parser import parse_quote

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("kichkina_tabib")

WELCOME = (
    "Assalomu alaykum! Men *Kichkina tabib* — istalgan gap, iqtibos yoki tabrigingizni "
    "chiroyli rasmli kartochkaga aylantirib beraman.\n\n"
    "Shunchaki matn yuboring, masalan:\n"
    "_\"Tug'ilgan kuningiz muborak bo'lsin!\"_\n\n"
    "Muallifini ham qo'shmoqchi bo'lsangiz, oxiriga tire bilan yozing:\n"
    "_\"So'zing sening qiymatingdir. — Hazrat Ali (r.a.)\"_"
)


def _format_keyboard(fmt: str) -> InlineKeyboardMarkup:
    other_fmt = "status" if fmt == "card" else "card"
    other_label = "📱 Status (vertikal)" if fmt == "card" else "🖼 Tabrik (kvadrat)"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Boshqa dizayn", callback_data="regen")],
        [InlineKeyboardButton(other_label, callback_data=f"fmt:{other_fmt}")],
    ])


def _render(text: str, author: str | None, fmt: str, seed: int) -> io.BytesIO:
    img = compose_status(text, author=author, seed=seed) if fmt == "status" else compose_card(text, author=author, seed=seed)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    bio.name = "card.png"
    return bio


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, parse_mode=ParseMode.MARKDOWN)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, parse_mode=ParseMode.MARKDOWN)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = update.message.text
    if not raw or len(raw.strip()) < 2:
        return
    body, author = parse_quote(raw)
    if len(body) > 400:
        await update.message.reply_text("Matn juda uzun ekan, iltimos qisqaroq yuboring (400 belgigacha).")
        return

    seed = random.randint(0, 1_000_000)
    fmt = "card"
    context.user_data["last"] = {"text": body, "author": author, "fmt": fmt, "seed": seed}

    photo = _render(body, author, fmt, seed)
    await update.message.reply_photo(photo=photo, reply_markup=_format_keyboard(fmt))


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    last = context.user_data.get("last")
    if not last:
        await query.answer("Avval matn yuboring.", show_alert=True)
        return

    data = query.data
    if data == "regen":
        last["seed"] = random.randint(0, 1_000_000)
    elif data.startswith("fmt:"):
        last["fmt"] = data.split(":", 1)[1]
        last["seed"] = random.randint(0, 1_000_000)

    await query.answer()
    photo = _render(last["text"], last["author"], last["fmt"], last["seed"])
    await query.message.edit_media(
        media=InputMediaPhoto(photo),
        reply_markup=_format_keyboard(last["fmt"]),
    )


def main():
    if not config.BOT_TOKEN:
        raise SystemExit(
            "BOT_TOKEN topilmadi. .env faylida yoki muhit o'zgaruvchisida BOT_TOKEN=... ni belgilang."
        )
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("Bot ishga tushdi.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
