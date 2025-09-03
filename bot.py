import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# === НАСТРОЙКИ ===
TOKEN = os.getenv("BOT_TOKEN")   # бот возьмёт токен из переменных окружения
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # и айди тоже из переменных окружения
REF_LINK = "https://www.bitrue.com/referral/landing?cn=600000&inviteCode=TZLLALV"  # твоя реферальная ссылка
COPYTRADING_LINK = "https://www.bitrue.com/copy-trading/trader/2833136590890188833"  # ссылка на копитрейдинг

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения user_id последнего скриншота
pending_users = {}

# === СТАРТ ===
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 Привет!\n"
        "Вот твоя реферальная ссылка для регистрации:\n"
        f"{REF_LINK}\n\n"
        "После регистрации отправь сюда скриншот подтверждения."
    )

# === ПОЛУЧАЕМ СКРИНШОТ ===
@dp.message_handler(content_types=["photo"])
async def handle_screenshot(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    # Пересылаем админу скрин
    await message.forward(chat_id=ADMIN_ID)

    # Кнопки для админа
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")
    )

    await bot.send_message(
        ADMIN_ID,
        f"📩 Скриншот от @{username} (ID: {user_id})",
        reply_markup=keyboard
    )

    # Запоминаем пользователя
    pending_users[user_id] = message.chat.id

    await message.answer("✅ Скриншот отправлен на проверку. Ждите ответа!")

# === ОБРАБОТКА ВЫБОРА АДМИНА ===
@dp.callback_query_handler(lambda c: c.data.startswith(("approve", "reject")))
async def process_callback(callback: types.CallbackQuery):
    action, user_id = callback.data.split("_")
    user_id = int(user_id)

    if action == "approve":
        await bot.send_message(user_id, f"🎉 Ваша заявка одобрена!\nВот ссылка: {COPYTRADING_LINK}")
        await callback.message.edit_text("✅ Вы одобрили заявку.")
    else:
        await bot.send_message(user_id, "❌ Ваша заявка отклонена. Попробуйте снова.")
        await callback.message.edit_text("❌ Вы отклонили заявку.")

    await callback.answer()

# === СТАРТ БОТА ===
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
