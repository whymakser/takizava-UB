import sys, io, traceback, asyncio, os
from __main__ import bot_kernel as bot
from telethon import events

@bot.client.on(events.NewMessage(pattern=r"(?s)^\.e (?P<code>.*)"))
async def run_eval(event):
    if not bot.is_owner(event.sender_id): return
    code = event.pattern_match.group("code")
    if event.out: await bot.edit(event, "<b>🐍 $</b> <code>Executing...</code>")
    old_stdout, old_stderr = sys.stdout, sys.stderr
    redirected_output, redirected_error = io.StringIO(), io.StringIO()
    sys.stdout, sys.stderr = redirected_output, redirected_error
    locs = {
        "bot": bot, "client": bot.client, "inline": bot.inline, "query": bot.query,
        "event": event, "reply": await event.get_reply_message(),
        "msg": event.message, "os": os, "asyncio": asyncio
    }
    try:
        clean_code = "".join(f"\n    {line}" for line in code.split("\n"))
        exec_code = f"async def _(bot, client, inline, query, event, reply, msg):{clean_code}"
        exec(exec_code, globals(), locs)
        await locs["_"](bot, bot.client, bot.inline, bot.query, event, locs["reply"], event.message)
    except Exception:
        traceback.print_exc()
    stdout, stderr = redirected_output.getvalue(), redirected_error.getvalue()
    sys.stdout, sys.stderr = old_stdout, old_stderr
    if event.out:
        output = f"🐍 $ <code>{code}</code>"
        if stdout: output += f"\n\n✅ <b>stdout:</b>\n<code>{stdout.strip()}</code>"
        if stderr: output += f"\n\n⚠️ <b>stderr:</b>\n<code>{stderr.strip()}</code>"
        if not stdout and not stderr: output += "\n\n✔️ <b>Success</b>"
        await bot.edit(event, output)
    elif stdout or stderr:
        await event.reply(f"<b>🐍 Result:</b>\n<code>{stdout.strip() or stderr.strip()}</code>", parse_mode='html')

@bot.client.on(events.NewMessage(pattern=r"(?s)^\.t (?P<cmd>.*)"))
async def run_terminal(event):
    if not bot.is_owner(event.sender_id): return
    cmd = event.pattern_match.group("cmd")
    process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    res = (stdout.decode() + stderr.decode()).strip()
    await event.reply(f"<code>{res or 'No output'}</code>", parse_mode='html')