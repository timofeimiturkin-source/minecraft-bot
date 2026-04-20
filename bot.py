from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# =======================
# 🔐 НАСТРОЙКИ
# =======================

TOKEN = "8522934495:AAEyGsE4RYznrBQp41HrF3zjoc-B15UyJKA"
ADMIN_ID = 8284104420  # свой Telegram ID

server = "VimeMc"

waiting_custom = set()

# =======================
# 📱 МЕНЮ
# =======================

menu = ReplyKeyboardMarkup(
    [
        ["💰 10 млн", "💰 20 млн", "💰 50 млн"],
        ["✍️ Своя сумма", "🖥 Сервер"]
    ],
    resize_keyboard=True
)

# =======================
# 🧮 ЦЕНА
# =======================

def calc_price(amount):
    if amount <= 10:
        return amount * 4.5
    elif amount <= 50:
        return amount * 4
    else:
        return amount * 3.5

# =======================
# 🚀 START
# =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это магазин Minecraft валюты 💰",
        reply_markup=menu
    )

# =======================
# 💬 ОСНОВНАЯ ЛОГИКА
# =======================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_custom

    text = update.message.text
    user_id = update.effective_user.id

    # 🖥 сервер
    if text == "🖥 Сервер":
        await update.message.reply_text(f"Сервер: {server}")
        return

    # 🔘 фикс кнопки
    if text == "💰 10 млн":
        amount = 10
    elif text == "💰 20 млн":
        amount = 20
    elif text == "💰 50 млн":
        amount = 50
    else:
        amount = None

    # ✍️ своя сумма
    if text == "✍️ Своя сумма":
        waiting_custom.add(user_id)
        await update.message.reply_text("Введи количество миллионов:")
        return

    # ввод своей суммы
    if user_id in waiting_custom:
        try:
            amount = float(text)
            waiting_custom.remove(user_id)
        except:
            await update.message.reply_text("Введи число (например 25)")
            return

    if amount is None:
        return

    price = calc_price(amount)

    # 📦 пользователю
    await update.message.reply_text(
        f"🧮 Заказ:\n"
        f"{amount} млн\n"
        f"Сервер: {server}\n"
        f"💰 Цена: {price} руб\n\n"
        f"📌 Перевод: 89824624608\n"
        f"После оплаты отправь скрин 📸"
    )

    # 👑 админу
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🛒 НОВЫЙ ЗАКАЗ\n\n"
             f"{amount} млн\n"
             f"{price} руб\n"
             f"{server}\n"
             f"@{update.effective_user.username}"
    )

# =======================
# 📸 СКРИНЫ ОПЛАТЫ
# =======================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=f"📸 ОПЛАТА\nОт: @{update.effective_user.username}"
    )

# =======================
# 🔧 ЗАПУСК
# =======================

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()