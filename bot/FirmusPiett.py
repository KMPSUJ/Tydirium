import os
from datetime import datetime, timedelta
import discord
from discord.ext import tasks
from bot.server_client import get_door_state


HOST_NAME = "localhost"
PORT = 7216
PIETT_TOKEN = os.getenv('PIETT_TOKEN', "")
PATIENCE = timedelta(minutes=10, seconds=0)
REFRESH_TIME = 10  # in seconds
CMD_LEADER = "Admiral,"


def export(code, last):
    file_path = "./stats.txt"
    with open(file_path, "a") as f:
        f.write(f"{last.strftime('%Y %m %d %H %M %S')}  {code}\n")


def gender(author):
    first_name = author.display_name.split()[0]
    name_ending = list(first_name)[-1]
    if name_ending == 'a':
        return "My Lady"
    else:
        return "Sir"


class FirmusPiett(discord.Client):
    host_name: str
    port: int
    class Communicate:
        def __init__(self):
            self._communicates = [
                ({"type": discord.ActivityType.watching, "name": "Koło zamknięte. Nakazuję odwrót!"},
                 {"type": discord.ActivityType.watching, "name": "Koło otwarte. Utrzymujcie kurs i prędkość"}),
                ({"type": discord.ActivityType.listening, "name": "Knockin' On Koło's Door"},
                 {"type": discord.ActivityType.listening, "name": "Baby It's Cold Outside"})
            ]
            self._status = {
                -1: discord.Status.invisible,
                0: discord.Status.do_not_disturb,
                1: discord.Status.online
            }
            self._currentlyUsed = 0

        def setCurrent(self, idx):
            if idx < 0 or idx > len(self._communicates):
                raise IndexError("no such communicate")
            self._currentlyUsed = idx

        def get(self, state):
            state = int(state) if 0 <= int(state) <= 1 else -1
            response = {"status": self._status[state]}
            if state < 0:
                response["activity"] = None
            else:
                response["activity"] = discord.Activity(**self._communicates[self._currentlyUsed][state])
            return response

    def __init__(self, host: str, port: int):
        super().__init__()
        #  self._panel = panel
        self._last_code = -1
        self._communicate = FirmusPiett.Communicate()
        self.last_update = None
        if host == "":
            self.host_name = "localhost"
        else:
            self.host_name = host
        self.port = port

    @tasks.loop(seconds=REFRESH_TIME)
    async def refreshStatus(self):
        now = datetime.now()
        previous_code = self._last_code
        door_state, self.last_update = get_door_state(self.host_name, self.port)
        if self.last_update is not None and (now - self.last_update) > PATIENCE:
            door_state = -1
        if self._last_code != door_state:
            self._last_code = door_state
            presence = self._communicate.get(self._last_code)
            await self.change_presence(**presence)
        if self._last_code != previous_code:
            export(self._last_code,now)
        print("Current code:", self._communicate._currentlyUsed, "/", self._last_code)

    async def on_ready(self):
        try:
            self.refreshStatus.start()
            print('We have logged in as {0.user}'.format(self))
        except:
            pass
        presence = self._communicate.get(self._last_code)
        await self.change_presence(**presence)

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith(CMD_LEADER):
            await self.execute_order(message.content[len(CMD_LEADER):], message.channel, message.author)

    async def execute_order(self, cmd, channel, author):
        HELP = "help"
        NEW_CODE = "new code"
        REPORT = "report"
        cmd = cmd.strip()
        if cmd.startswith(HELP):
            await self.print_help(cmd[len(HELP):], channel, author)
        elif cmd.startswith(NEW_CODE):
            await self.new_code(cmd[len(NEW_CODE):], channel, author)
        elif cmd.startswith(REPORT):
            await self.report(cmd[len(REPORT):], channel, author)
        else:
            await self.bad_command(channel, author)

    async def print_help(self, cmd, channel, author):
        salutation = gender(author)
        cmd = cmd.strip()
        if cmd != "" and cmd != "!" and cmd != ".":
            await self.bad_command(channel, author)
        ans = f"Calm down, {salutation}, I'm here.\n" \
              "You can ask me for `report` to see current state of the door " \
              "and last time when it was updated.\n" \
              "You can also order me to `new code n`, so I would display " \
              "the state of the door in different ways."
        await channel.send(ans)

    async def new_code(self, cmd, channel, author):
        salutation = gender(author)
        cmd = cmd.strip()
        try:
            perms = author.guild_permissions
            if perms.administrator or perms.manage_channels or perms.manage_guild or perms.manage_nicknames or perms.manage_messages or perms.manage_roles:
                cmd = int(cmd)
                if 0 <= cmd < len(self._communicate._communicates):
                    self._communicate.setCurrent(cmd)
                    self._last_code = -1
                    await channel.send(f"Yes {salutation}! Code {cmd}")
                else:
                    await channel.send(f"{salutation}, code {cmd} is out of the protocol!")
            else:
                await channel.send(f"{salutation}, your powers are insufficient to set a new code.")
        except:
            await self.bad_command(channel, author)
        
    async def report(self, cmd, channel, author):
        salutation = gender(author)
        cmd = cmd.strip()
        if cmd != "" and cmd != "!" and cmd != ".":
            await self.bad_command(channel, author)
        await self.refreshStatus()
        ans = ""
        if self._last_code == 0:
            ans += f"{salutation}, according to our intelligence the door is closed.\n"
        elif self._last_code == 1:
            ans += f"{salutation}, according to our intelligence the door is open.\n"
        else:
            ans += f"{salutation}, despite many Bothans died, we have not determined the state of the door.\n"
        if self.last_update is None:
            ans += "We haven't received any information from them yet."
        elif self.last_update.year < 2000:
            ans += "We haven't received any information from them yet."
        else:
            ans += "Last update from Tydirium was received "
            ans += self.last_update.strftime("%d.%m.%Y at %H:%M:%S.")
        await channel.send(ans)

    async def bad_command(self, channel, author):
        salutation = gender(author)
        await channel.send(f"We have some communication disruption, {salutation}. Please repeat.")


if __name__ == "__main__":
    piett = FirmusPiett(HOST_NAME, PORT)
    piett.run(PIETT_TOKEN)
