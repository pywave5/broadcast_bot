import asyncio
import threading

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from telethon import TelegramClient
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from telethon.sessions import StringSession

from .models import Account

def run_in_new_loop(coro):
    result = {}
    def target():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result["data"] = loop.run_until_complete(coro)
        except Exception as e:
            result["error"] = e
        finally:
            loop.close()
    thread = threading.Thread(target=target)
    thread.start()
    thread.join()
    if "error" in result:
        raise result["error"]
    return result.get("data")

def clear_auth_session(request, account_id):
    for key in ['session_string', 'phone_code_hash', 'auth_step']:
        request.session.pop(f'{key}_{account_id}', None)

async def send_code(account: Account):
    client = TelegramClient(StringSession(), account.api_id, account.api_hash)
    await client.connect()
    try:
        result = await asyncio.wait_for(client.send_code_request(account.phone_number), timeout=15)
        return {
            "session_string": client.session.save(),
            "phone_code_hash": result.phone_code_hash
        }
    except asyncio.TimeoutError:
        raise Exception("Код не получен: таймаут")

async def sign_in_with_code(account: Account, session_str: str, code: str, phone_code_hash: str):
    client = TelegramClient(StringSession(session_str), account.api_id, account.api_hash)
    await client.connect()
    try:
        await client.sign_in(account.phone_number, code, phone_code_hash=phone_code_hash)
        return client.session.save()
    except SessionPasswordNeededError:
        return "password_needed"
    finally:
        await client.disconnect()

async def sign_in_with_password(account: Account, session_str: str, password: str):
    client = TelegramClient(StringSession(session_str), account.api_id, account.api_hash)
    await client.connect()
    await client.sign_in(password=password)
    session = client.session.save()
    await client.disconnect()
    return session

@login_required
@user_passes_test(lambda u: u.is_staff)
def telegram_code_view(request, account_id):
    account = get_object_or_404(Account, id=account_id)

    if request.method == "GET" and request.GET.get("reset") == "1":
        clear_auth_session(request, account_id)

    session_string = request.session.get(f'session_string_{account_id}')
    phone_code_hash = request.session.get(f'phone_code_hash_{account_id}')
    step = request.session.get(f'auth_step_{account_id}', 'code')
    code_sent = session_string is not None

    if request.method == "POST":
        action = request.POST.get("action")
        session_string = request.session.get(f'session_string_{account_id}')
        phone_code_hash = request.session.get(f'phone_code_hash_{account_id}')
        step = request.session.get(f'auth_step_{account_id}', 'code')

        if action == "get_code":
            try:
                result = run_in_new_loop(send_code(account))
                request.session[f'session_string_{account_id}'] = result["session_string"]
                request.session[f'phone_code_hash_{account_id}'] = result["phone_code_hash"]
                request.session[f'auth_step_{account_id}'] = "code"
                messages.success(request, "Код отправлен в Telegram.")
            except FloodWaitError as e:
                minutes = e.seconds // 60
                seconds = e.seconds % 60
                messages.error(request, f"Telegram требует подождать: {minutes} мин {seconds} сек.")
            except Exception as e:
                messages.error(request, f"Ошибка при отправке кода: {e}")
            return redirect(request.path)

        if action == "submit_code":
            code = request.POST.get("code")
            if not session_string or not phone_code_hash:
                messages.error(request, "Сессия устарела. Пожалуйста, получите код заново.")
                return redirect(request.path)
            try:
                result = run_in_new_loop(sign_in_with_code(account, session_string, code, phone_code_hash))
                if result == "password_needed":
                    request.session[f'auth_step_{account_id}'] = "password"
                    messages.info(request, "Введите 2FA пароль от Telegram.")
                    return redirect(request.path)
                account.session_string = result
                account.is_active = True
                account.save()
                clear_auth_session(request, account_id)
                messages.success(request, "Успешно авторизован!")
                return redirect('/admin/account/account/')
            except Exception as e:
                messages.error(request, f"Ошибка при авторизации: {e}")
                return redirect(request.path)

        if action == "submit_password":
            password = request.POST.get("password")
            if not session_string:
                messages.error(request, "Сессия устарела. Пожалуйста, получите код заново.")
                return redirect(request.path)
            try:
                result = run_in_new_loop(sign_in_with_password(account, session_string, password))
                account.session_string = result
                account.is_active = True
                account.save()
                clear_auth_session(request, account_id)
                messages.success(request, "Авторизация с 2FA прошла успешно!")
                return redirect('/admin/account/account/')
            except Exception as e:
                messages.error(request, f"Ошибка при вводе пароля: {e}")
                return redirect(request.path)

    elif request.method == "POST" and not request.POST.get("code") and not request.POST.get("password"):
        try:
            result = run_in_new_loop(send_code(account))
            request.session[f'session_string_{account_id}'] = result["session_string"]
            request.session[f'phone_code_hash_{account_id}'] = result["phone_code_hash"]
            request.session[f'auth_step_{account_id}'] = "code"
            messages.success(request, "Код отправлен в Telegram.")
            return redirect(request.path)
        except FloodWaitError as e:
            minutes = e.seconds // 60
            seconds = e.seconds % 60
            messages.error(request, f"Telegram требует подождать: {minutes} мин {seconds} сек.")
        except Exception as e:
            messages.error(request, f"Не удалось отправить код: {e}")
        return redirect(request.path)

    return render(request, 'admin/account/authorize.html', {
        'account': account,
        'code_sent': code_sent,
        'step': request.session.get(f'auth_step_{account_id}', 'code'),
        'is_authenticated': account.is_active
    })
