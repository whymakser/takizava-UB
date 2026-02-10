import re, json, os, subprocess, secrets, asyncio, time
from telethon import functions, types
from aiogram import types as aiotypes
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .premium import ids

class InlineQuerySender:
    def __init__(self, kernel):
        self.kernel = kernel

    async def send(self, chat_id, text, buttons=None):
        bot_user = await self.kernel.aiobot.get_me()
        query_text = f"{text} | {buttons}" if buttons else text
        results = await self.kernel.client(functions.messages.GetInlineBotResultsRequest(
            bot=bot_user.username, peer=chat_id, query=query_text, offset=''
        ))
        return await self.kernel.client(functions.messages.SendInlineBotResultRequest(
            peer=chat_id, query_id=results.query_id, id=results.results[0].id, clear_draft=True
        ))

class Kernel:
    def __init__(self):
        self.client = None
        self.me = None
        self.aiobot = None
        self.dp = None
        self.start_time = time.time()
        self.config_path = "config.json"
        self.config = self.load_config()
        self.pattern = re.compile(r"(?i)<emoji id=(?P<name>\w+),default=(?P<def>.+?)>")
        self.inline = self
        self.query = InlineQuerySender(self)
        self.bot = self

    def load_config(self):
        if not os.path.exists(self.config_path):
            return {"prefix": ".", "owners": [], "api_id": None, "api_hash": None, "bot_token": None, "topics": {}, "nonick_users": []}
        with open(self.config_path, "r") as f:
            try:
                data = json.load(f)
                for key, default in [("topics", {}), ("nonick_users", []), ("owners", [])]:
                    if key not in data: data[key] = default
                return data
            except:
                return {"prefix": ".", "owners": [], "api_id": None, "api_hash": None, "bot_token": None, "topics": {}, "nonick_users": []}

    def get_uptime(self):
        uptime_seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def save_config(self):
        with open(self.config_path, "w") as f: json.dump(self.config, f, indent=4)

    def get_commit(self):
        try: return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode('ascii').strip()
        except: return "None"

    async def init_owner(self):
        self.me = await self.client.get_me()
        if self.me and self.me.id not in self.config["owners"]:
            self.config["owners"].insert(0, self.me.id)
            self.save_config()

    def render(self, text: str) -> str:
        def replace(match):
            name, default = match.group("name").lower(), match.group("def")
            eid = ids.get(name)
            return f"<emoji id='{eid}'>{default}</emoji>" if eid else default
        return self.pattern.sub(replace, text)

    def is_owner(self, user_id): return user_id in self.config.get("owners", [])
    def is_targeted(self, event): return event.sender_id in self.config.get("owners", [])

    def parse_buttons(self, buttons_str):
        builder = InlineKeyboardBuilder()
        if buttons_str:
            matches = re.findall(r"<(.+?)>\[(.+?)\]", buttons_str)
            for name, data in matches:
                if data.strip().startswith("http"):
                    builder.row(aiotypes.InlineKeyboardButton(text=name, url=data.strip()))
                else:
                    builder.row(aiotypes.InlineKeyboardButton(text=name, callback_data=data.strip()))
        return builder.as_markup()

    async def send(self, chat_id, text, buttons=None):
        return await self.aiobot.send_message(
            chat_id, self.render(text), reply_markup=self.parse_buttons(buttons), parse_mode="HTML"
        )

    async def edit(self, event, text, buttons=None):
        rendered = self.render(text)
        if event.out:
            return await event.edit(rendered, parse_mode='html')
        return await self.send(event.chat_id, text, buttons)

    async def answer_inline(self, iq: aiotypes.InlineQuery, text: str, buttons: str = None):
        results = [aiotypes.InlineQueryResultArticle(
            id=secrets.token_hex(4), title="Result",
            input_message_content=aiotypes.InputTextMessageContent(message_text=self.render(text), parse_mode="HTML"),
            reply_markup=self.parse_buttons(buttons)
        )]
        return await iq.answer(results, cache_time=0, is_personal=True)