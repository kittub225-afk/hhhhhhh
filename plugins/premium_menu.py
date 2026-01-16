from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from db import db

MAIN_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("💎 Premium Settings", callback_data="menu:settings"),
     InlineKeyboardButton("💎 Premium Commands", callback_data="menu:commands")]
])

SETTINGS_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎨 Font Color", callback_data="ps:font_color"),
     InlineKeyboardButton("🅰️ Font Style", callback_data="ps:font_style")],
    [InlineKeyboardButton("✏️ File Name", callback_data="ps:file_name"),
     InlineKeyboardButton("💧 PDF Watermark", callback_data="ps:pdf_watermark")],
    [InlineKeyboardButton("⬅️ Back", callback_data="menu:main")]
])

COMMANDS_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("✍️ Text ➜ .txt", callback_data="pc:t2t"),
     InlineKeyboardButton("📝 Edit .txt", callback_data="pc:edit")],
    [InlineKeyboardButton("📂 Split .txt", callback_data="pc:split")],
    [InlineKeyboardButton("⬅️ Back", callback_data="menu:main")]
])

def register_premium_menu(bot: Client):

    @bot.on_callback_query()
    async def menu_router(client: Client, cq: CallbackQuery):

        if not db.is_user_authorized(cq.from_user.id, client.me.username):
            await cq.answer("❌ Premium required", show_alert=True)
            return

        if cq.data == "menu:main":
            await cq.message.edit_reply_markup(MAIN_MENU)

        elif cq.data == "menu:settings":
            await cq.message.edit_reply_markup(SETTINGS_MENU)

        elif cq.data == "menu:commands":
            await cq.message.edit_reply_markup(COMMANDS_MENU)

        elif cq.data == "pc:t2t":
            await cq.message.reply_text("👉 Use /t2t command")

        await cq.answer()
