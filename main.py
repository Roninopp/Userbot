"""
main.py
aiogram bot — this is what users talk to in order to add their account.
Flow:
  /start -> force-join check -> /addaccount -> phone -> OTP -> session saved.

Run this with: python bot/main.py
"""

import asyncio
import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
)
from aiogram.exceptions import TelegramBadRequest

from pyrogram import Client
from pyrogram.errors import (
    PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded, PhoneNumberInvalid
)

import database as db

logging.basicConfig(level=logging.INFO)

# ---- CONFIG ----
BOT_TOKEN = os.getenv("BOT_TOKEN", "8787470204:AAExtvCXEFdEK0WQQAFnPNKCX4eCCJqkcLM")
API_ID = int(os.getenv("API_ID", "21502134"))
API_HASH = os.getenv("API_HASH", "e09a3f453b841ca4d1823d3b4004672d")

# Telegram user IDs allowed to run /fixdb. Add your own numeric telegram_id here.
ADMIN_IDS = [6837532865]

# Keep this in sync with AVAILABLE_PLUGINS in userbot_manager.py and FULL_PLUGIN_LIST in fixdb.py
FULL_PLUGIN_LIST = "ping,raid,afk,help,echo,clone"

# ---- Force-join channels ----
# Use @username for public channels, or the numeric chat id for private ones.
FORCE_JOIN_CHANNELS = [
    {"name": "Goa Games Gods", "username": "@Goa_Games_Gods", "invite_link": "https://t.me/Goa_Games_Gods"},
    {"name": "Channel 2", "username": None, "invite_link": "https://t.me/+all_1TRgXdM0Mzc9"},
]

# Leave blank — add manually later via imgbb URL or local file path
START_PIC = ""  # e.g. "https://i.ibb.co/xxxxx/banner.jpg" or "assets/start_pic.jpg"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

pending_clients = {}  # telegram_id -> {"client": Client, "phone_code_hash": str, "phone": str, "code": str}


class AddAccount(StatesGroup):
    waiting_phone = State()
    waiting_otp = State()
    waiting_password = State()


# ---------- Force-join check ----------
async def check_membership(telegram_id: int) -> list:
    """Returns list of channels the user has NOT joined yet."""
    not_joined = []
    for ch in FORCE_JOIN_CHANNELS:
        chat_ref = ch["username"] if ch["username"] else ch["invite_link"]
        try:
            member = await bot.get_chat_member(chat_id=ch["username"] or chat_ref, user_id=telegram_id)
            if member.status in ("left", "kicked"):
                not_joined.append(ch)
        except TelegramBadRequest:
            # If bot can't check (e.g. private channel with no username),
            # we can't verify — treat as not joined to be safe, user must confirm manually.
            not_joined.append(ch)
        except Exception:
            not_joined.append(ch)
    return not_joined


def join_keyboard(not_joined: list) -> InlineKeyboardMarkup:
    buttons = []
    for ch in not_joined:
        buttons.append([InlineKeyboardButton(text=f"📢 Join {ch['name']}", url=ch["invite_link"])])
    buttons.append([InlineKeyboardButton(text="✅ I've Joined — Check Again", callback_data="check_join")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ---------- Welcome / Menu ----------
WELCOME_TEXT = (
    "🌑 <b>Welcome to Control Angel</b> 🌑\n"
    "<i>Turn your Telegram account into a fully automated userbot — free, no coding, no hosting.</i>\n\n"
    "<blockquote>"
    "✨ Add your account in under a minute\n"
    "🔌 Plug in ready-made modules: ping, afk, raid, echo, clone \\& more\n"
    "🛡️ Runs 24/7 on our servers — your phone can stay off"
    "</blockquote>\n\n"
    "Tap <b>Add Account</b> below to get started, or check <b>How To Use</b> first."
)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add Account", callback_data="menu_addaccount")],
        [
            InlineKeyboardButton(text="📖 How To Use", callback_data="menu_howto"),
            InlineKeyboardButton(text="🧩 Bot Features", callback_data="menu_features"),
        ],
        [InlineKeyboardButton(text="💬 Support", url="https://t.me/Goa_Games_Gods")],
    ])


HOWTO_TEXT = (
    "📖 <b>How To Use Control Angel</b>\n\n"
    "<blockquote>"
    "1️⃣ Tap <b>Add Account</b>\n"
    "2️⃣ Send your phone number (with country code)\n"
    "3️⃣ Enter the OTP using the number pad\n"
    "4️⃣ Done! Your account is now a live userbot"
    "</blockquote>\n\n"
    "Once connected, go to <b>your own account</b> (any chat) and try:\n"
    "<code>.ping</code> — test if it's alive\n"
    "<code>.help</code> — see every available command\n\n"
    "⚠️ Use responsibly — automated spam-like behavior can get your account limited by Telegram."
)

FEATURES_TEXT = (
    "🧩 <b>Available Modules</b>\n\n"
    "<blockquote>"
    "🏓 <b>Ping</b> — test response time\n"
    "🌙 <b>AFK</b> — auto-reply when you're away\n"
    "📢 <b>Raid</b> — auto-reply once to new DMs\n"
    "🔁 <b>Echo</b> — mirror a user's messages\n"
    "🎭 <b>Clone</b> — clone a profile (name/bio/photo), with revert"
    "</blockquote>\n\n"
    "Type <code>.help</code> from your own account after setup for the full live list."
)


async def send_welcome(chat_id: int):
    kwargs = dict(chat_id=chat_id, text=WELCOME_TEXT, parse_mode="HTML", reply_markup=main_menu_keyboard())
    if START_PIC:
        try:
            photo = FSInputFile(START_PIC) if not START_PIC.startswith("http") else START_PIC
            await bot.send_photo(chat_id=chat_id, photo=photo, caption=WELCOME_TEXT,
                                  parse_mode="HTML", reply_markup=main_menu_keyboard())
            return
        except Exception:
            pass  # fall back to text-only if photo fails
    await bot.send_message(**kwargs)


# ---------- OTP Keyboard ----------
def otp_keyboard():
    buttons = []
    row = []
    for i in range(1, 10):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"otp_{i}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    buttons.append([
        InlineKeyboardButton(text="0", callback_data="otp_0"),
        InlineKeyboardButton(text="⌫ Delete", callback_data="otp_del"),
        InlineKeyboardButton(text="✅ Submit", callback_data="otp_submit"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ---------- Handlers ----------
@dp.message(Command("start"))
async def start_cmd(message: Message):
    not_joined = await check_membership(message.from_user.id)
    if not_joined:
        await message.answer(
            "🔒 <b>Access Locked</b>\n\nJoin these channels first to unlock the bot:",
            parse_mode="HTML",
            reply_markup=join_keyboard(not_joined)
        )
        return
    await send_welcome(message.chat.id)


@dp.callback_query(F.data == "check_join")
async def recheck_join(callback: CallbackQuery):
    not_joined = await check_membership(callback.from_user.id)
    if not_joined:
        await callback.answer("You haven't joined all channels yet.", show_alert=True)
        return
    await callback.message.delete()
    await send_welcome(callback.message.chat.id)


@dp.callback_query(F.data == "menu_howto")
async def show_howto(callback: CallbackQuery):
    await callback.message.edit_text(
        HOWTO_TEXT, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="menu_back")]
        ])
    ) if not callback.message.photo else await callback.message.answer(HOWTO_TEXT, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "menu_features")
async def show_features(callback: CallbackQuery):
    await callback.message.edit_text(
        FEATURES_TEXT, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="menu_back")]
        ])
    ) if not callback.message.photo else await callback.message.answer(FEATURES_TEXT, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "menu_back")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(WELCOME_TEXT, parse_mode="HTML", reply_markup=main_menu_keyboard())
    await callback.answer()


@dp.callback_query(F.data == "menu_addaccount")
async def menu_addaccount(callback: CallbackQuery, state: FSMContext):
    not_joined = await check_membership(callback.from_user.id)
    if not_joined:
        await callback.answer("Join the required channels first!", show_alert=True)
        return
    await state.set_state(AddAccount.waiting_phone)
    await callback.message.answer(
        "📱 Send your phone number in international format.\nExample: +919876543210"
    )
    await callback.answer()


@dp.message(Command("addaccount"))
async def add_account_start(message: Message, state: FSMContext):
    not_joined = await check_membership(message.from_user.id)
    if not_joined:
        await message.answer(
            "🔒 Join these channels first to unlock account setup:",
            reply_markup=join_keyboard(not_joined)
        )
        return
    await state.set_state(AddAccount.waiting_phone)
    await message.answer(
        "📱 Send your phone number in international format.\nExample: +919876543210"
    )


@dp.message(AddAccount.waiting_phone)
async def receive_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    telegram_id = message.from_user.id

    await message.answer("⏳ Sending OTP to your Telegram account...")

    client = Client(
        name=f"session_{telegram_id}",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True
    )

    try:
        await client.connect()
        sent = await client.send_code(phone)
    except PhoneNumberInvalid:
        await message.answer("❌ That phone number is invalid. Try /addaccount again.")
        await state.clear()
        return
    except Exception as e:
        await message.answer(f"❌ Failed to send code: {e}")
        await state.clear()
        return

    pending_clients[telegram_id] = {
        "client": client,
        "phone": phone,
        "phone_code_hash": sent.phone_code_hash,
        "code": ""
    }

    await state.set_state(AddAccount.waiting_otp)
    await message.answer(
        "🔢 Enter the OTP sent to your Telegram app using the buttons below:",
        reply_markup=otp_keyboard()
    )


@dp.callback_query(F.data.startswith("otp_"), AddAccount.waiting_otp)
async def handle_otp_button(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    action = callback.data.split("_")[1]

    if telegram_id not in pending_clients:
        await callback.answer("Session expired, please /addaccount again.", show_alert=True)
        return

    entry = pending_clients[telegram_id]

    if action == "del":
        entry["code"] = entry["code"][:-1]
        await callback.answer()
        return

    if action == "submit":
        await callback.message.edit_text("⏳ Verifying...")
        await finish_login(telegram_id, callback, state)
        return

    entry["code"] += action
    await callback.answer(f"Code: {entry['code']}")


async def finish_login(telegram_id: int, callback: CallbackQuery, state: FSMContext):
    entry = pending_clients[telegram_id]
    client: Client = entry["client"]

    try:
        await client.sign_in(
            phone_number=entry["phone"],
            phone_code_hash=entry["phone_code_hash"],
            phone_code=entry["code"]
        )
    except PhoneCodeInvalid:
        await callback.message.edit_text("❌ Invalid code. Use /addaccount to try again.")
        await cleanup(telegram_id, state)
        return
    except PhoneCodeExpired:
        await callback.message.edit_text("❌ Code expired. Use /addaccount to try again.")
        await cleanup(telegram_id, state)
        return
    except SessionPasswordNeeded:
        await state.set_state(AddAccount.waiting_password)
        await callback.message.edit_text("🔒 Your account has 2FA enabled. Please send your password:")
        return
    except Exception as e:
        await callback.message.edit_text(f"❌ Login failed: {e}")
        await cleanup(telegram_id, state)
        return

    await complete_session_save(telegram_id, callback.message, state)


@dp.message(AddAccount.waiting_password)
async def receive_2fa_password(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    entry = pending_clients.get(telegram_id)
    if not entry:
        await message.answer("Session expired, please /addaccount again.")
        await state.clear()
        return

    client: Client = entry["client"]
    try:
        await client.check_password(message.text.strip())
    except Exception as e:
        await message.answer(f"❌ Incorrect password: {e}\nUse /addaccount to try again.")
        await cleanup(telegram_id, state)
        return

    await complete_session_save(telegram_id, message, state)


async def complete_session_save(telegram_id: int, message: Message, state: FSMContext):
    entry = pending_clients[telegram_id]
    client: Client = entry["client"]

    session_string = await client.export_session_string()
    await db.save_session(telegram_id, entry["phone"], session_string)
    await client.disconnect()

    await message.answer(
        "✅ <b>Account connected successfully!</b>\n\n"
        "Your userbot is now active. Go to your own account and type:\n"
        "<code>.ping</code> to test it, or <code>.help</code> to see every command.",
        parse_mode="HTML"
    )

    await cleanup(telegram_id, state)


async def cleanup(telegram_id: int, state: FSMContext):
    pending_clients.pop(telegram_id, None)
    await state.clear()


@dp.message(Command("fixdb"))
async def fixdb_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ You're not authorized to use this command.")
        return

    parts = message.text.split(maxsplit=1)
    plugin_list = parts[1].strip() if len(parts) > 1 else FULL_PLUGIN_LIST

    await message.answer(f"⏳ Updating all users to: <code>{plugin_list}</code>...", parse_mode="HTML")
    try:
        updated_count = await db.set_all_plugins(plugin_list)
        await message.answer(
            f"✅ Done. Updated {updated_count} user(s).\n"
            f"plugins_enabled = <code>{plugin_list}</code>\n\n"
            f"Restart the worker dyno for changes to take effect.",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Error: {e}")


async def main():
    await db.init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
