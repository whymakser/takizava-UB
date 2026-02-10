import os, sys
from telethon import events
from __main__ import bot_kernel as bot

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.prefix (?P<char>.+)"))
async def change_prefix(event):
    if not bot.is_targeted(event): return
    new_prefix = event.pattern_match.group("char").strip()[0]
    bot.config["prefix"] = new_prefix
    bot.save_config()
    await bot.edit(event, f"<emoji id=ok,default=✔️> <b>Prefix changed to:</b> <code>{new_prefix}</code>\n<b>Restart required.</b>")

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.addowner(?P<args>.*)"))
async def add_owner(event):
    if not bot.is_targeted(event): return
    args = event.pattern_match.group("args").strip()
    user_id = None
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
    elif args.isdigit():
        user_id = int(args)
    if user_id:
        if user_id not in bot.config["owners"]:
            bot.config["owners"].append(user_id)
            bot.save_config()
            await bot.edit(event, f"<emoji id=ok,default=✔️> <b>User</b> <code>{user_id}</code> <b>added as owner.</b>")
        else:
            await bot.edit(event, "<b>User is already an owner.</b>")
    else:
        await bot.edit(event, "<b>Reply to someone or provide an ID.</b>")

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.delowner(?P<args>.*)"))
async def del_owner(event):
    if not bot.is_targeted(event): return
    args = event.pattern_match.group("args").strip()
    user_id = None
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
    elif args.isdigit():
        user_id = int(args)
    if user_id == bot.me.id:
        return await bot.edit(event, "<b>You cannot remove yourself.</b>")
    if user_id and user_id in bot.config["owners"]:
        bot.config["owners"].remove(user_id)
        bot.save_config()
        await bot.edit(event, f"<emoji id=ok,default=✔️> <b>User</b> <code>{user_id}</code> <b>removed from owners.</b>")
    else:
        await bot.edit(event, "<b>User not found in owners list.</b>")

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.owners"))
async def list_owners(event):
    if not bot.is_targeted(event): return
    msg = "<emoji id=ok,default=✔️> <b>Owners List:</b>\n"
    for i, owner in enumerate(bot.config["owners"], 1):
        msg += f"{i}. <code>{owner}</code>\n"
    await bot.edit(event, msg)

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.nonick"))
async def toggle_nonick(event):
    if not bot.is_targeted(event): return
    uid = bot.me.id
    if uid in bot.config["nonick_users"]:
        bot.config["nonick_users"].remove(uid)
        res = "<emoji id=ok,default=✔️> <b>Owner signature:</b> <code>ENABLED</code>"
    else:
        bot.config["nonick_users"].append(uid)
        res = "<emoji id=ok,default=✔️> <b>Owner signature:</b> <code>DISABLED</code>"
    bot.save_config()
    await bot.edit(event, res)

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.restart"))
async def restart_bot(event):
    if not bot.is_targeted(event): return
    await bot.edit(event, "<emoji id=reload,default=⏳> <b>Restarting...</b>")
    bot.config["last_reboot"] = {"chat": event.chat_id, "msg": event.id}
    bot.save_config()
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.hub"))
async def setup_hub_cmd(event):
    if not bot.is_targeted(event): return
    await bot.edit(event, "<emoji id=reload,default=⏳> <b>Setting up Hub...</b>")
    hub_id = await bot.setup_hub()
    await bot.edit(event, f"<emoji id=ok,default=✔️> <b>Hub created:</b> <code>{hub_id}</code>")