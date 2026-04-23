from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8522934495:AAEyGsE4RYznrBQp41HrF3zjoc-B15UyJKA"
ADMIN_ID = 8284104420

menu = ReplyKeyboardMarkup(
    [["💰 Купить валюту", "🖥 Сервер"]],
    resize_keyboard=True
)

amount_menu = ReplyKeyboardMarkup(
    [["10", "20", "50"], ["✏️ Своя сумма"]],
    resize_keyboard=True
)

server = "VimeMc"

waiting_custom = {}
waiting_nick = {}
orders = {}
waiting_confirm = {}

order_counter = 1000  # ID старт

prices = {
    "small": 4.5,
    "medium": 4,
    "large": 3.5
}

def calc_price(amount):
    if amount <= 10:
        return amount * prices["small"]
    elif amount <= 50:
        return amount * prices["medium"]
    else:
        return amount * prices["large"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Магазин валюты 💰", reply_markup=menu)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_counter

    text = update.message.text
    user_id = update.effective_user.id

    # ===== АДМИН КОМАНДЫ =====

    if user_id == ADMIN_ID:

        # список заказов
        if text == "orders":
            if not orders:
                await update.message.reply_text("Нет заказов")
                return

            msg = "📋 Список заказов:\n\n"
            for oid, data in orders.items():
                msg += f"#{oid} | {data['nick']} | {data['amount']}м | {data['price']}₽\n"

            await update.message.reply_text(msg)
            return

        # завершить заказ
        if text.startswith("done"):
            try:
                _, oid = text.split()
                oid = int(oid)

                if oid in orders:
                    data = orders.pop(oid)

                    await context.bot.send_message(
                        chat_id=data["user_id"],
                        text="✅ Ваш заказ выполнен! Спасибо за покупку 💰"
                    )

                    await update.message.reply_text(f"Заказ #{oid} закрыт")
                else:
                    await update.message.reply_text("Нет такого заказа")
            except:
                await update.message.reply_text("Пример: done 1001")
            return

        # изменить цену
        if text.startswith("setprice"):
            try:
                _, limit, new_price = text.split()
                limit = float(limit)
                new_price = float(new_price)

                if limit <= 10:
                    prices["small"] = new_price
                elif limit <= 50:
                    prices["medium"] = new_price
                else:
                    prices["large"] = new_price

                await update.message.reply_text("Цена обновлена")
            except:
                await update.message.reply_text("setprice 10 5")
            return

    # ===== КЛИЕНТ =====

    if text == "💰 Купить валюту":
        await update.message.reply_text("Выбери количество:", reply_markup=amount_menu)
        return

    elif text == "🖥 Сервер":
        await update.message.reply_text(f"Сервер: {server}")
        return

    elif text == "✏️ Своя сумма":
        waiting_custom[user_id] = True
        await update.message.reply_text("Введи количество:")
        return

    if user_id in waiting_custom:
        try:
            amount = float(text)
            waiting_custom.pop(user_id)
            waiting_nick[user_id] = amount
            await update.message.reply_text("Введи ник:")
        except:
            await update.message.reply_text("Введи число!")
        return

    if text in ["10", "20", "50"]:
        amount = float(text)
        waiting_nick[user_id] = amount
        await update.message.reply_text("Введи ник:")
        return

    # ввод ника
    if user_id in waiting_nick:
        nick = text
        amount = waiting_nick.pop(user_id)
        price = calc_price(amount)

        order_counter += 1
        oid = order_counter

        orders[oid] = {
            "user_id": user_id,
            "nick": nick,
            "amount": amount,
            "price": price
        }

        await update.message.reply_text(
            f"🧾 Заказ #{oid}\n\n"
            f"{nick}\n{amount} млн\n{price} руб\n\n"
            f"📌 Перевод: 89824624608\n"
            f"📸 Отправь скрин оплаты"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🛒 Заказ #{oid}\n{nick}\n{amount} млн\n{price} руб\n@{update.effective_user.username}"
        )
        return

    # подтверждение после скрина
    if text == "✅ Я оплатил":
        if user_id in waiting_confirm:
            await update.message.reply_text("Спасибо! Ожидайте 💰", reply_markup=menu)
        else:
            await update.message.reply_text("Сначала отправь скрин")
        return

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1].file_id

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=f"📸 Скрин\n@{update.effective_user.username}"
    )

    confirm_menu = ReplyKeyboardMarkup([["✅ Я оплатил"]], resize_keyboard=True)

    waiting_confirm[user_id] = True

    await update.message.reply_text("Нажми 'Я оплатил'", reply_markup=confirm_menu)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
