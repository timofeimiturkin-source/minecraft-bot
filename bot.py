from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ================== НАСТРОЙКИ ==================
TOKEN = "8522934495:AAEZXzCkJfEZt1s92zzlog4LMcibM4EbgK8"
ADMIN_ID = 8284104420
BOT_USERNAME = "VimeVirt_bot"

PAYMENT_TEXT = (
    "💳 Реквизиты для оплаты:\n\n"
    "📱 Перевод на номер: 89824624608\n\n"
    "⚠️ После оплаты отправь скрин сюда"
)

REVIEW_LINK = "https://t.me/+OKkKi9f8eAMwODEy"

# ================== МЕНЮ ==================
menu = ReplyKeyboardMarkup(
    [["💰 Купить валюту", "👥 Рефералка"],
     ["⭐ Отзывы"]],
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

    if context.args:
        try:
            ref_id = int(context.args[0])
            if ref_id != user_id:
                user_ref[user_id] = ref_id
        except:
            pass

    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    await update.message.reply_text(
        "💰 Магазин валюты\n\n"
        f"🔗 Ваша реферальная ссылка:\n{ref_link}",
        reply_markup=menu
    )

# ================== ЛОГИКА ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_counter

    text = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or "нет_username"

    # ================== ОТЗЫВЫ ==================
    if text == "⭐ Отзывы":
        await update.message.reply_text(
            f"⭐ Отзывы наших покупателей:\n\n{REVIEW_LINK}\n\n"
            "Можешь ознакомиться перед покупкой"
        )
        return

    # ================== РЕФЕРАЛКА ==================
    if text == "👥 Рефералка":
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

        await update.message.reply_text(
            "👥 Реферальная система\n\n"
            f"🔗 Ваша ссылка:\n{ref_link}\n\n"
            "💰 За каждого друга: +2 млн"
        )
        return

    # ================== АДМИН ==================
    if user_id == ADMIN_ID:

        # 🔧 ИЗМЕНЕНИЕ ЦЕНЫ
        if text.startswith("/setprice"):
            try:
                _, tier, value = text.split()
                value = float(value)

                if tier in prices:
                    prices[tier] = value
                    await update.message.reply_text(f"Цена {tier} изменена на {value}")
                else:
                    await update.message.reply_text("Используй: small / medium / large")

            except:
                await update.message.reply_text("Пример: /setprice small 4.5")
            return

        if text == "orders":
            if not orders:
                await update.message.reply_text("Нет заказов")
                return

            msg = "📋 ЗАКАЗЫ:\n\n"
            for oid, o in orders.items():
                msg += (
                    f"#{oid}\n"
                    f"🔗 @{o.get('username','нет_username')}\n"
                    f"🎮 {o['nick']}\n"
                    f"📦 {o['amount']} млн\n"
                    f"💰 {o['price']} руб\n\n"
                )

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

    # ================== ПОЛЬЗОВАТЕЛЬ ==================

    if text == "💰 Купить валюту":
        await update.message.reply_text("Выбери сумму:", reply_markup=amount_menu)
        return

    if text == "✏️ Своя сумма":
        waiting_custom[user_id] = True
        await update.message.reply_text("Введи сумму (до 120 млн):")
        return

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

    # ================== ЗАКАЗ ==================
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
            "username": username,
            "nick": nick,
            "amount": amount,
            "price": final_price
        }

        ref = user_ref.get(user_id)
        if ref:
            bonus_balance[ref] = bonus_balance.get(ref, 0) + 2

        await update.message.reply_text(
            f"🧾 Заказ #{oid}\n\n"
            f"📦 {amount} млн\n"
            f"💰 {final_price} руб\n\n"
            f"{PAYMENT_TEXT}\n\n"
            "📸 Отправь скрин оплаты"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🛒 НОВЫЙ ЗАКАЗ #{oid}\n\n"
                f"🔗 @{username}\n"
                f"🆔 {user_id}\n\n"
                f"🎮 Ник: {nick}\n"
                f"📦 {amount} млн\n"
                f"💰 {final_price} руб"
            )
        )
        return

# ================== СКРИН ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"📸 скрин @{update.effective_user.username or 'нет_username'}"
    )

    await update.message.reply_text("⏳ ожидайте пополнения баланса")

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
