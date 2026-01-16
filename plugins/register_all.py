from pyrogram import Client

from plugins.premium_menu import register_premium_menu
# baad me use karoge
# from plugins.text_tools import register_text_tools
# from plugins.cookies import register_cookies


def register_all_plugins(bot: Client):
    register_premium_menu(bot)
