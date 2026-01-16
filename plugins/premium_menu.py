from __future__ import annotations

from typing import Dict, Any, Optional

from pyrogram import Client
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)

# Your project DB
from db import db

# -----------------------------
# UI Text (Screenshots-style)
# -----------------------------

SETTINGS_CAPTION = (
    "💎 **Premium Settings Panel** 💎\n\n"
    "✨ _Customize your experience &_\n"
    "_un/lock full potential!_\n\n"
    "🎛️ **Fonts • Thumbnails • Watermarks**\n"
    "🚀 _Supercharge your uploads with pro tools_"
)

COMMANDS_CAPTION = (
    "💎 **Premium Command Panel** 💎\n\n"
    "✨ _Smart tools to manage & process_\n"
    "_your uploads_\n\n"
    "✍️ **Convert • Edit • Split • Clean**\n"
    "⚡ _Extract with ease_"
)

MAIN_CAPTION = (
    "🧰 **Menu**\n\n"
    "Choose a panel:"
)

# -----------------------------
# Keyboards (Same buttons)
# -----------------------------

PREMIUM_SETTINGS_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎨 Font Color", callback_data="ps:font_color"),
     InlineKeyboardButton("🅰️ Font Style", callback_data="ps:font_style")],

    [InlineKeyboardButton("✏️ File Name", callback_data="ps:file_name"),
     InlineKeyboardButton("🎞️ Video Thumb", callback_data="ps:video_thumb")],

    [InlineKeyboardButton("🖼️ PDF Thumb", callback_data="ps:pdf_thumb"),
     InlineKeyboardButton("🧵 Auto Topic", callback_data="ps:auto_topic")],

    [InlineKeyboardButton("✍️ Add Credit", callback_data="ps:add_credit"),
     InlineKeyboardButton("💧 PDF Watermark", callback_data="ps:pdf_watermark")],

    [InlineKeyboardButton("💦 Video Watermark", callback_data="ps:video_watermark"),
     InlineKeyboardButton("🎚️ Video Quality", callback_data="ps:video_quality")],

    [InlineKeyboardButton("🔗 PDF Hyperlinks", callback_data="ps:pdf_hyperlinks"),
     InlineKeyboardButton("🔑 Set Token", callback_data="ps:set_token")],

    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="menu:main")]
])

PREMIUM_COMMANDS_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("✍️ Text ➜ .txt", callback_data="pc:t2t"),
     InlineKeyboardButton("📝 Edit .txt", callback_data="pc:edit_txt")],

    [InlineKeyboardButton("📂 Split .txt", callback_data="pc:split_txt"),
     InlineKeyboardButton("🧹 Replace Word", callback_data="pc:replace_word")],

    [InlineKeyboardButton("🧾 HTML Formatter", callback_data="pc:html_formatter")],

    [InlineKeyboardButton("⚪ Keyword Filter", callback_data="pc:keyword_filter"),
     InlineKeyboardButton("🧽 Title Clean", callback_data="pc:title_clean")],

    [InlineKeyboardButton("🧾 PW (.sh ➜ .txt)", callback_data="pc:pw_sh_to_txt"),
     InlineKeyboardButton("🎬 YouTube Extract", callback_data="pc:youtube_extract")],

    [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu:main")]
])

MAIN_MENU_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("💎 Premium Settings Panel", callback_data="menu:premium_settings")],
    [InlineKeyboardButton("💎 Premium Command Panel", callback_data="menu:premium_commands")],
])

# -----------------------------
# Settings store (DB wrapper)
# If your db doesn't have these,
# it will fallback to in-memory.
# -----------------------------

_mem_user_settings: Dict[int, Dict[str, Any]] = {}

def _get_settings(user_id: int, bot_username: str) -> Dict[str, Any]:
    # Try DB (if you already have something like this)
    try:
        fn = getattr(db, "get_user_settings", None)
        if callable(fn):
            data = fn(user_id, bot_username)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return _mem_user_settings.get(user_id, {}).copy()

def _set_setting(user_id: int, bot_username: str, key: str, value: Any) -> None:
    # Try DB
    try:
        fn = getattr(db, "set_user_setting", None)
        if callable(fn):
            fn(user_id, bot_username, key, value)
            return
    except Exception:
        pass

    # fallback memory
    _mem_user_settings.setdefault(user_id, {})[key] = value

# -----------------------------
# Helpers
# -----------------------------

async def _ask_text(client: Client, chat_id: int, prompt: str) -> Optional[str]:
    msg = await client.send_message(chat_id, prompt)
    try:
        inp: Message = await client.listen(chat_id)
        if not inp.text:
            return None
        text = inp.text.strip()
        if text.lower() in ("/cancel", "cancel"):
            return None
        return text
    finally:
        try:
            await msg.delete()
        except Exception:
            pass

def _is_authorized(user_id: int, bot_username: str) -> bool:
    try:
        if db.is_admin(user_id):
            return True
    except Exception:
        pass
    try:
        return db.is_user_authorized(user_id, bot_username)
    except Exception:
        return False

# -----------------------------
# Register
# -----------------------------

def register_premium_menu(bot: Client):
    @bot.on_callback_query()
    async def premium_callbacks(client: Client, cq: CallbackQuery):
        data = cq.data or ""
        bot_username = client.me.username
        user_id = cq.from_user.id
        chat_id = cq.message.chat.id

        if not _is_authorized(user_id, bot_username):
            await cq.answer("❌ Premium required", show_alert=True)
            return

        # ---- Menu navigation ----
        if data == "menu:main":
            # If it's a photo caption message -> edit_caption works
            try:
                await cq.message.edit_caption(MAIN_CAPTION, reply_markup=MAIN_MENU_KB)
            except Exception:
                # if normal text message
                await cq.message.edit_text(MAIN_CAPTION, reply_markup=MAIN_MENU_KB)
            await cq.answer()
            return

        if data == "menu:premium_settings":
            try:
                await cq.message.edit_caption(SETTINGS_CAPTION, reply_markup=PREMIUM_SETTINGS_KB)
            except Exception:
                await cq.message.edit_text(SETTINGS_CAPTION, reply_markup=PREMIUM_SETTINGS_KB)
            await cq.answer()
            return

        if data == "menu:premium_commands":
            try:
                await cq.message.edit_caption(COMMANDS_CAPTION, reply_markup=PREMIUM_COMMANDS_KB)
            except Exception:
                await cq.message.edit_text(COMMANDS_CAPTION, reply_markup=PREMIUM_COMMANDS_KB)
            await cq.answer()
            return

        # ---- Settings actions ----
        if data.startswith("ps:"):
            key = data.split("ps:", 1)[1]
            await cq.answer()

            # Simple input + save (abhi processing later connect kar denge)
            if key in ("font_color", "font_style", "file_name", "add_credit", "pdf_watermark", "video_watermark", "video_quality", "auto_topic"):
                val = await _ask_text(
                    client,
                    chat_id,
                    f"Send value for **{key}**\n\nType /cancel to stop."
                )
                if val is None:
                    await client.send_message(chat_id, "❌ Cancelled.")
                    return
                _set_setting(user_id, bot_username, key, val)
                await client.send_message(chat_id, f"✅ Saved **{key}** = `{val}`")
                return

            if key in ("pdf_thumb", "video_thumb"):
                await client.send_message(chat_id, "📌 Send a photo to set thumbnail (feature wiring next).")
                return

            if key == "pdf_hyperlinks":
                # on/off toggle
                st = _get_settings(user_id, bot_username)
                cur = bool(st.get("pdf_hyperlinks", False))
                new_val = not cur
                _set_setting(user_id, bot_username, "pdf_hyperlinks", new_val)
                await client.send_message(chat_id, f"✅ PDF Hyperlinks: **{'ON' if new_val else 'OFF'}**")
                return

            if key == "set_token":
                val = await _ask_text(client, chat_id, "🔑 Send token (Type /cancel to stop)")
                if val is None:
                    await client.send_message(chat_id, "❌ Cancelled.")
                    return
                _set_setting(user_id, bot_username, "token", val)
                await client.send_message(chat_id, "✅ Token saved!")
                return

            await client.send_message(chat_id, f"✅ Clicked: `{key}`")
            return

        # ---- Command actions ----
        if data.startswith("pc:"):
            cmd = data.split("pc:", 1)[1]
            await cq.answer()

            # Yaha hum existing commands ko call karwa rahe hain
            # (tumhare main.py me /t2t already hai)
            if cmd == "t2t":
                await client.send_message(chat_id, "✅ Use command: /t2t")
                return

            if cmd == "html_formatter":
                await client.send_message(chat_id, "✅ Use command: /t2h")
                return

            # Baaki tools: tumhare next parts me jo functions honge unse connect kar denge
            await client.send_message(chat_id, f"✅ Tool selected: `{cmd}` (wiring next)")
            return
  await cq.answer()
