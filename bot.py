import os
import logging
import re
from collections import Counter
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hello! I'm a *Word Counter Bot*.\n\n"
        "Just send me any text and I'll count:\n"
        "• 📝 Words\n"
        "• 🔤 Characters (with & without spaces)\n"
        "• 📄 Sentences\n"
        "• 📋 Paragraphs\n\n"
        "Use /help to see all commands.",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 *Word Counter Bot — Help*\n\n"
        "/start — Welcome message\n"
        "/help  — Show this help\n"
        "/about — About this bot\n\n"
        "Simply send any text message and I'll analyse it instantly!",
        parse_mode="Markdown",
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📊 *Word Counter Bot*\n\n"
        "A simple bot to count words, characters, sentences and paragraphs.\n\n"
        "Hosted on Render.com 🚀",
        parse_mode="Markdown",
    )


def analyse_text(text: str) -> dict:
    words = text.split()
    word_count = len(words)
    char_with_spaces = len(text)
    char_without_spaces = len(text.replace(" ", ""))
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = len(sentences)
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    paragraph_count = len(paragraphs)

    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "is", "it", "was", "are", "be", "this", "that",
        "with", "as", "by", "from", "i", "you", "he", "she", "we",
        "they", "have", "has", "had", "do", "did", "will", "would",
        "can", "could", "should", "my", "your", "its", "our"
    }
    filtered = [
        w.lower().strip(".,!?;:'\"()[]") for w in words
        if w.lower().strip(".,!?;:'\"()[]") not in stop_words and len(w) > 2
    ]
    top_words = Counter(filtered).most_common(3)
    avg_word_length = (
        round(sum(len(w) for w in words) / word_count, 1) if word_count else 0
    )

    return {
        "word_count": word_count,
        "char_with_spaces": char_with_spaces,
        "char_without_spaces": char_without_spaces,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "top_words": top_words,
        "avg_word_length": avg_word_length,
    }


async def count_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    stats = analyse_text(text)

    top_words_str = (
        ", ".join(f"`{w}` ({c})" for w, c in stats["top_words"])
        if stats["top_words"] else "N/A"
    )

    reply = (
        f"📊 *Text Analysis*\n"
        f"{'─' * 28}\n"
        f"📝 *Words:*             {stats['word_count']}\n"
        f"🔤 *Chars (w/ spaces):* {stats['char_with_spaces']}\n"
        f"🔡 *Chars (no spaces):* {stats['char_without_spaces']}\n"
        f"📄 *Sentences:*         {stats['sentence_count']}\n"
        f"📋 *Paragraphs:*        {stats['paragraph_count']}\n"
        f"📏 *Avg word length:*   {stats['avg_word_length']} chars\n"
        f"{'─' * 28}\n"
        f"🏆 *Top words:* {top_words_str}"
    )

    await update.message.reply_text(reply, parse_mode="Markdown")


def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_words))

    logger.info("Bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
