import sys
from telethon import events
import io

from __main__ import bot_kernel as bot


@bot.client.on(events.NewMessage(pattern=r"(?s)^\.\s*help\s*$", outgoing=True))
async def cmd_help(event):
    if not bot.is_targeted(event):
        return

    sys_modules = set()
    cus_modules = set()
    for m in sys.modules.keys():
        parts = m.split('.')
        if len(parts) > 2 and parts[:2] == ['forelka', 'modules']:
            sys_modules.add(parts[2])
        elif len(parts) > 1 and parts[0] == 'modules':
            cus_modules.add(parts[1])

    sys_list = sorted(sys_modules)
    cus_list = sorted(cus_modules)
    total_modules = len(sys_list) + len(cus_list)

    text = (
        f"<b><emoji id=5931415565955503486,default=🤖> Модули юзербота</b>\n\n"
        f"<b><emoji id=5825794181183836432,default=✔️> {total_modules} модулей доступно</b>\n"
        f" системных <b>{len(sys_list)}</b> • кастомных <b>{len(cus_list)}</b>\n\n"
    )

    if sys_list:
        text += "<b><emoji id=5879895758202735862,default=🔒> Системные модули</b>\n\n"
        text += "\n".join(f"<emoji id=5879895758202735862,default=🔒> <code>{m}</code>" for m in sys_list)
        text += "\n\n"

    if cus_list:
        text += "<b><emoji id=5936017305585586269,default=🪪> Кастомные модули</b>\n\n"
        text += "\n".join(f"<emoji id=5936017305585586269,default=🪪> <code>{m}</code>" for m in cus_list)

    text += f"\n\n<i>{total_modules} модулей загружено, {len(sys_list)} из них системные</i>"

    if len(text) > 3900:
        f = io.BytesIO(text.encode("utf-8"))
        f.name = "modules.txt"
        await bot.client.send_file(event.chat_id, f, caption="<b>Список модулей отправлен файлом</b>")
        await event.delete()
        return

    await bot.edit(event, text)