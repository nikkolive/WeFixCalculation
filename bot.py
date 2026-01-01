import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import re

START_MESSAGE = (
    "👋 *Добро пожаловать в бот!*\n\n"
    "Этот бот поможет вам:\n"
    "• рассчитать чистую прибыль\n"
    "• определить процентную ставку\n"
    "• узнать средний чек за период\n\n"
    "📌 *Как пользоваться ботом*\n"
    "• Каждая строка — это *одна выполненная работа*\n"
    "• Можно вводить *несколько работ*, каждая — с новой строки\n"
    "• Просто отправляйте сообщения — расчёт происходит автоматически\n\n"
    "✍️ *Как вводить данные*\n"
    "1️⃣ Укажите стоимость продажи до налога\n"
    "2️⃣ Если были расходы (запчасти или скидка), укажите их в скобках\n"
    "3️⃣ Если расходов не было — укажите только сумму продажи\n\n"
    "✅ *Пример ввода:*\n"
    "```\n"
    "200 (20) (35)\n"
    "180 (15)\n"
    "250\n"
    "```\n"
    "• 200 / 180 / 250 — стоимость продажи\n"
    "• 20 / 15 — себестоимость запчастей\n"
    "• 35 — сумма скидки\n\n"
    "Бот автоматически рассчитает прибыль, средний чек и вашу зарплату."
)

from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        START_MESSAGE,
        parse_mode="Markdown"
    )

clean_profits = []

def get_percentage(acp):
    if acp >= 300:
        return 0.60
    elif acp >= 250:
        return 0.55
    elif acp >= 200:
        return 0.50
    else:
        return 0.45

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clean_profits.clear()
    await update.message.reply_text("🔄 All jobs cleared. New period started.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = text.splitlines()
    added_jobs = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        sale_match = re.match(r"^\d+(\.\d+)?", line)
        if not sale_match:
            continue

        sale_price = float(sale_match.group())

        expenses = re.findall(r"\((\d+(\.\d+)?)\)", line)
        total_expenses = sum(float(e[0]) for e in expenses)

        clean_profit = sale_price - total_expenses
        clean_profits.append(clean_profit)
        added_jobs += 1

    if added_jobs == 0:
        await update.message.reply_text("❌ Invalid input. Example:\n225 (50) (25)")
        return

    total_cp = sum(clean_profits)
    job_count = len(clean_profits)
    acp = total_cp / job_count
    percent = get_percentage(acp)

    salary = total_cp * percent
    new_salary = total_cp * 0.45

    await update.message.reply_text(
        f"📊 RESULTS\n\n"
        f"💰 Текущая зарплата: ${salary:.2f}\n"
        f"📈 Средний чек: ${acp:.2f}\n"
        f"🎯 Ставка %: {int(percent * 100)}%\n"
        f"👶 Текущая зарплата (45%): ${new_salary:.2f}\n"
        f"📦 Количество работ: {job_count}"
    )

def main():
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("start", start))
    

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()




