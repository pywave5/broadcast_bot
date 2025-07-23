from aiogram import Bot, types
from aiogram.types import FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
import asyncio

from conf.settings import CHANNEL_ID, BOT_TOKEN

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def send_message_to_channel(bot_message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(_send(bot_message))

async def _send(bot_message):
    keyboard = None
    if bot_message.button_text and bot_message.button_url:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=bot_message.button_text, url=bot_message.button_url)]
        ])

    if bot_message.is_video_note and bot_message.video:
        msg = await bot.send_video_note(
            chat_id=bot_message.chat_id,
            video_note=FSInputFile(bot_message.video.path),
            reply_markup=keyboard
        )
        return msg.message_id

    if bot_message.video:
        msg = await bot.send_video(
            chat_id=bot_message.chat_id,
            video=FSInputFile(bot_message.video.path),
            caption=bot_message.text or "",
            reply_markup=keyboard
        )
        return msg.message_id

    msg = await bot.send_message(
        chat_id=bot_message.chat_id,
        text=bot_message.text,
        reply_markup=keyboard
    )
    return msg.message_id