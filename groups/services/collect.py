import asyncio
from asgiref.sync import sync_to_async

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Channel, User, InputChannel, Chat
from telethon.errors import ChannelInvalidError

from account.models import Account
from groups.models import Group, GroupUser
from django.utils import timezone


@sync_to_async
def get_or_create_group(account, entity):
    group, _ = Group.objects.get_or_create(
        account=account,
        group_id=entity.id,
        defaults={
            "title": entity.title,
            "access_hash": entity.access_hash,
        }
    )
    return group


@sync_to_async
def clear_old_users(group):
    group.users.all().delete()


@sync_to_async
def save_user(group, user):
    GroupUser.objects.create(
        group=group,
        user_id=user.id,
        access_hash=user.access_hash,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_bot=user.bot
    )


@sync_to_async
def save_group_timestamp(group):
    group.last_synced = timezone.now()
    group.save()


async def collect_users(account: Account, group: Group):
    client = TelegramClient(StringSession(account.session_string), account.api_id, account.api_hash)
    await client.connect()

    try:
        if group.access_hash:
            input_channel = InputChannel(channel_id=group.group_id, access_hash=group.access_hash)
            entity = await client.get_entity(input_channel)
        else:
            entity = await client.get_entity(group.title)

        # await client(JoinChannelRequest(entity))

        if not isinstance(entity, (Channel, Chat)):
            raise Exception("Это не группа или канал.")

        await clear_old_users(group)

        participants = await client.get_participants(entity, aggressive=True)

        for user in participants:
            if isinstance(user, User):
                await save_user(group, user)

        await save_group_timestamp(group)

    except ChannelInvalidError:
        raise Exception("Невозможно получить группу. Ссылка неправильная или доступ запрещен.")
    finally:
        await client.disconnect()