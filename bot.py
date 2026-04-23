from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import time

# ================== НАСТРОЙКИ ==================
TOKEN = "8522934495:AAEyGsE4RYznrBQp41HrF3zjoc-B15UyJKA"
ADMIN_ID = 8284104420
BOT_USERNAME = "VimeVirt_bot"

SERVER_NAME = "VimeMc"

PAYMENT_TEXT = (
    "💳 Реквизиты для оплаты:\n\n"
    "📱 Перевод на номер: 89824624608\n\n"
    "⚠️ После оплаты отправь скрин сюда"
)

REVIEW_LINK = "https://t.me/+OKkKi9f8eAMwODEy"

# ================== МЕНЮ ==================
menu = ReplyKeyboardMarkup(
    [["💰 Купить валюту", "🖥 Сервер"]],
    resize_keyboard=True
)

amount_menu = ReplyKeyboardMarkup(
    [["10", "20", "50"], ["✏️ Своя сумма"]],
    resize_keyboard=True
)

# ================== ДАННЫЕ ==================
waiting_custom = {}
waiting_nick = {}

orders = {}
user_ref = {}
bonus_balance = {}
review_bonus = {}

order_counter = 1000
last_request = {}

prices = {
    "small": 4.5,
    "medium": 4,
    "large": 3.5
}

# ================== ЦЕНА ==================
def calc_price(amount):
    if amount <= 10:
        return amount * prices["small"]
    elif amount <= 50:
        return amount * prices["medium"]
    else:
        return amount * prices["large"]

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # рефералка через ссылку
    if context.args:
        try:
            ref_id = int(context.args[0])
            if ref_id != user_id:
                user_ref[user_id] = ref_id
        except:
            pass

    # реф ссылка
    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    await update.message.reply_text(
        "💰 Магазин валюты\n\n"
        f"👥 Приглашай друзей и получай +2 млн\n"
        f"🔗 Твоя ссылка:\n{ref_link}",
        reply_markup=menu
    )

# ================== ЛОГИКА ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_counter

    text = update.message.text
    user_id = update.effective_user.id

    # антиспам
    if user_id in last_request:
        if time.time() - last_request[user_id] < 3:
            await update.message.reply_text("⏳ Подожди")
            return
    last_request[user_id] = time.time()

    # ================== АДМИН ==================
    if user_id == ADMIN_ID:

        if text == "orders":
            if not orders:
                await update.message.reply_text("Нет заказов")
                return

            msg = "📋 Заказы:\n\n"
            for oid, o in orders.items():
                msg += f"#{oid} | {o['nick']} | {o['amount']}м | {o['price']}₽\n"

            await update.message.reply_text(msg)
            return

        if text.startswith("done"):
            try:
                _, oid = text.split()
                oid = int(oid)

                if oid in orders:
                    o = orders.pop(oid)

                    await context.bot.send_message(
                        chat_id=o["user_id"],
                        text="✅ Заказ выполнен!"
                    )

                    review_bonus[o["user_id"]] = review_bonus.get(o["user_id"], 0) + 1

                    await context.bot.send_message(
                        chat_id=o["user_id"],
                        text=(
                            "⭐ Спасибо за заказ!\n\n"
                            f"💬 Оставь отзыв:\n{REVIEW_LINK}\n\n"
                            "🎁 +1 млн бонус за отзыв"
                        )
                    )

                    await update.message.reply_text(f"Готово #{oid}")
            except:
                await update.message.reply_text("done 1001")
            return

        if text.startswith("setprice"):
            try:
                _, limit, price = text.split()
                limit = float(limit)
                price = float(price)

                if limit <= 10:
                    prices["small"] = price
                elif limit <= 50:
                    prices["medium"] = price
                else:
                    prices["large"] = price

                await update.message.reply_text("Цена обновлена")
            except:
                await update.message.reply_text("setprice 10 5")
            return

    # ================== ПОЛЬЗОВАТЕЛЬ ==================

    if text == "💰 Купить валюту":
        await update.message.reply_text("Выбери сумму:", reply_markup=amount_menu)
        return

    if text == "🖥 Сервер":
        await update.message.reply_text(f"Сервер: {SERVER_NAME}")
        return

    if text == "✏️ Своя сумма":
        waiting_custom[user_id] = True
        await update.message.reply_text("Введи сумму (до 120 млн):")
        return

    # кастом сумма
    if user_id in waiting_custom:
        try:
            amount = float(text)

            if amount > 120:
                await update.message.reply_text("❌ максимум 120 млн")
                return

            waiting_custom.pop(user_id)
            waiting_nick[user_id] = amount
            await update.message.reply_text("🎮 Введи ник:")
        except:
            await update.message.reply_text("введи число")
        return

    if text in ["10", "20", "50"]:
        waiting_nick[user_id] = float(text)
        await update.message.reply_text("🎮 Введи ник:")
        return

    # ник
    if user_id in waiting_nick:
        nick = text
        amount = waiting_nick.pop(user_id)

        price = calc_price(amount)

        bonus = bonus_balance.get(user_id, 0)
        bonus += review_bonus.get(user_id, 0)

        final_price = max(price - bonus, 0)

        bonus_balance[user_id] = 0
        review_bonus[user_id] = 0

        order_counter += 1
        oid = order_counter

        orders[oid] = {
            "user_id": user_id,
            "nick": nick,
            "amount": amount,
            "price": final_price
        }

        # реферал +2 млн
        ref = user_ref.get(user_id)
        if ref:
            bonus_balance[ref] = bonus_balance.get(ref, 0) + 2

        await update.message.reply_text(
            f"🧾 Заказ #{oid}\n\n"
            f"👤 {nick}\n"
            f"📦 {amount} млн\n"
            f"💰 {final_price} руб\n\n"
            f"{PAYMENT_TEXT}\n\n"
            "📸 Отправь скрин оплаты"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🛒 #{oid}\n{nick}\n{amount} млн\n{final_price} руб"
        )
        return

# ================== СКРИН ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=f"📸 скрин @{update.effective_user.username}"
    )

    await update.message.reply_text("⏳ ожидайте подтверждения")

# ================== ЗАПУСК ==================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
