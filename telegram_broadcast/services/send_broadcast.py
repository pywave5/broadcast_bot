import asyncio
from random import randint

from telethon import TelegramClient, Button
from telethon.sessions import StringSession
from telethon.tl.types import InputUser

from groups.models import GroupUser
from telegram_broadcast.models import Broadcast
from asgiref.sync import sync_to_async


@sync_to_async
def get_broadcast_and_users(broadcast_id):
    broadcast = Broadcast.objects.select_related("account", "message_to_forward", "group").get(id=broadcast_id)

    if broadcast.group:
        users = GroupUser.objects.filter(group=broadcast.group).only("user_id", "access_hash")
    else:
        users = GroupUser.objects.filter(group__account=broadcast.account).only("user_id", "access_hash")

    return broadcast, list(users)

@sync_to_async
def mark_as_sent(broadcast):
    broadcast.is_sent = True
    broadcast.save()

async def send_broadcast(broadcast_id: int):
    broadcast, users = await get_broadcast_and_users(broadcast_id)
    account = broadcast.account

    client = TelegramClient(StringSession(account.session_string), account.api_id, account.api_hash)
    await client.connect()

    try:
        buttons = None
        if broadcast.button_text and broadcast.button_url:
            buttons = [[Button.url(broadcast.button_text, broadcast.button_url)]]

        # Forward message
        if broadcast.message_to_forward:
            for user in users:
                try:
                    input_user = InputUser(user.user_id, user.access_hash)
                    await client.forward_messages(
                        entity=input_user,
                        messages=broadcast.message_to_forward.message_id,
                        from_peer=broadcast.message_to_forward.chat_id
                    )
                except Exception as e:
                    print(f"Ошибка при отправке пользователю {user.user_id}: {e}")
                await asyncio.sleep(randint(1, 3))

        # Send video
        elif broadcast.video:
            sent_msg = await client.send_file(
                entity="me",
                file=broadcast.video.path if hasattr(broadcast.video, "path") else broadcast.video,
                video_note=broadcast.is_video_note,
                caption=broadcast.text or "",
                buttons=buttons,
                parse_mode="Markdown"
            )
            message_id = sent_msg.id if hasattr(sent_msg, "id") else sent_msg[0].id

            for user in users:
                try:
                    input_user = InputUser(user.user_id, user.access_hash)
                    await client.forward_messages(
                        entity=input_user,
                        messages=message_id,
                        from_peer="me"
                    )
                    print(f"✅ Видео отправлено: {user.user_id}")
                except Exception as e:
                    print(f"❌ Ошибка (видео): {user.user_id}: {e}")
                await asyncio.sleep(randint(1, 3))

            await client.delete_messages("me", message_id)

        # Send photo
        elif broadcast.photo:
            sent_msg = await client.send_file(
                entity="me",
                file=broadcast.photo.path if hasattr(broadcast.photo, "path") else broadcast.photo,
                caption=broadcast.text or "",
                buttons=buttons,
                parse_mode="Markdown"
            )
            message_id = sent_msg.id if hasattr(sent_msg, "id") else sent_msg[0].id

            for user in users:
                try:
                    input_user = InputUser(user.user_id, user.access_hash)
                    await client.forward_messages(
                        entity=input_user,
                        messages=message_id,
                        from_peer="me"
                    )
                    print(f"✅ Фото отправлено: {user.user_id}")
                except Exception as e:
                    print(f"❌ Ошибка (фото): {user.user_id}: {e}")
                await asyncio.sleep(randint(1, 3))

            await client.delete_messages("me", message_id)

        # Send audio
        elif broadcast.audio:
            sent_msg = await client.send_file(
                entity="me",
                file=broadcast.audio.path if hasattr(broadcast.audio, "path") else broadcast.audio,
                caption=broadcast.text or "",
                video_note=broadcast.is_voice_note,
                buttons=buttons,
                parse_mode="Markdown"
            )
            message_id = sent_msg.id if hasattr(sent_msg, "id") else sent_msg[0].id

            for user in users:
                try:
                    input_user = InputUser(user.user_id, user.access_hash)
                    await client.forward_messages(
                        entity=input_user,
                        messages=message_id,
                        from_peer="me"
                    )
                    print(f"✅ Аудио отправлено: {user.user_id}")
                except Exception as e:
                    print(f"❌ Ошибка (аудио): {user.user_id}: {e}")
                await asyncio.sleep(randint(1, 3))

            await client.delete_messages("me", message_id)

        # Send text
        elif broadcast.text:
            for user in users:
                try:
                    input_user = InputUser(user.user_id, user.access_hash)
                    await client.send_message(
                        entity=input_user,
                        message=broadcast.text,
                        buttons=buttons,
                        parse_mode="Markdown"
                    )
                    print(f"✅ Текст отправлен: {user.user_id}")
                except Exception as e:
                    print(f"❌ Ошибка (текст): {user.user_id}: {e}")
                await asyncio.sleep(randint(1, 3))

        else:
            print("⚠️ Нет контента для рассылки (ни текст, ни медиа, ни форвард).")

    finally:
        await mark_as_sent(broadcast)
        await client.disconnect()
