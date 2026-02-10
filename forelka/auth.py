import os, asyncio, qrcode
from telethon import TelegramClient, errors

C, G, Y, R, W = "\033[94m", "\033[92m", "\033[93m", "\033[91m", "\033[0m"

class Authenticator:
    def __init__(self, client: TelegramClient, banner_func):
        self.client = client
        self.banner = banner_func

    async def start(self):
        if await self.client.is_user_authorized():
            return
        self.banner()
        print(f"{Y}>>> Login method:{W}\n[{G}1{W}] QR Code\n[{G}2{W}] Phone Number")
        choice = input(f"{G}Choice: {W}")
        if choice == "1":
            await self._qr_login()
        else:
            try:
                await self.client.start()
            except errors.SessionPasswordNeededError:
                await self._handle_2fa()

    async def _handle_2fa(self):
        print(f"\n{Y}>>> 2FA Enabled.{W}")
        pw = input(f"{G}Password: {W}")
        await self.client.sign_in(password=pw)

    async def _qr_login(self):
        qr_login = await self.client.qr_login()
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.banner()
            print(f"{Y}>>> Scan QR in Telegram Devices:{W}\n")
            qr = qrcode.QRCode()
            qr.add_data(qr_login.url)
            qr.print_ascii(invert=True)
            try:
                await qr_login.wait(60)
                break
            except asyncio.TimeoutError:
                qr_login = await self.client.qr_login()
                continue
            except errors.SessionPasswordNeededError:
                await self._handle_2fa()
                break