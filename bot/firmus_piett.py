import os
from datetime import datetime, timedelta
import discord
from discord.ext import tasks
from bot.server_client import ServerClient


HOST_NAME = "localhost"
PORT = 7216
PIETT_TOKEN = os.getenv('PIETT_TOKEN', "")
PATIENCE = timedelta(minutes=10, seconds=0)
REFRESH_TIME = 10  # in seconds

CMD_LEADER = "Admiral,"
HELP = "help"
NEW_CODE = "new code"
REPORT = "report"


class FirmusPiett(discord.Client, ServerClient):
    """
    Main class for maintaining discord bot.
    Responsible for correct displaying state of the door as bot status
    and responding for users commands.
    """

    class Communicate:
        """
        Discord bot inner class. Store all possible bot statuses
        and index of the one currently in use.
        Give easy access to proper communicate.
        """

        def __init__(self):
            self.communicates = [
                ({"type": discord.ActivityType.watching,
                  "name": "Koło zamknięte. Nakazuję odwrót!"},
                 {"type": discord.ActivityType.watching,
                  "name": "Koło otwarte. Utrzymujcie kurs i prędkość"}),
                ({"type": discord.ActivityType.listening,
                  "name": "Knockin' On Koło's Door"},
                 {"type": discord.ActivityType.listening,
                  "name": "Baby It's Cold Outside"})
            ]
            self._status = {
                -1: discord.Status.invisible,
                0: discord.Status.do_not_disturb,
                1: discord.Status.online
            }
            self._currently_used = 0

        def set_current(self, idx):
            if idx < 0 or idx > len(self.communicates):
                raise IndexError("no such communicate")
            self._currently_used = idx

        def get(self, state):
            state = int(state) if 0 <= int(state) <= 1 else -1
            response = {"status": self._status[state]}
            if state < 0:
                response["activity"] = None
            else:
                response["activity"] = discord.Activity(
                    **self.communicates[self._currently_used][state]
                )
            return response

    def __init__(self, host: str, port: int):
        super().__init__()
        #  self._panel = panel
        self._last_code = -1
        self._communicate = FirmusPiett.Communicate()
        self.last_update = None
        ServerClient.__init__(self, host, port)

    @tasks.loop(seconds=REFRESH_TIME)
    async def refresh_status(self):
        now = datetime.now()
        door_state, self.last_update = self.get_door_state()
        if self.last_update is not None and (now - self.last_update) > PATIENCE:
            door_state = -1
        if self._last_code != door_state:
            self._last_code = door_state
            presence = self._communicate.get(self._last_code)
            await self.change_presence(**presence)

    async def on_ready(self):
        try:
            self.refresh_status.start() # pylint: disable=E1101
        except:
            pass
        presence = self._communicate.get(self._last_code)
        await self.change_presence(**presence)

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith(CMD_LEADER):
            await self.execute_order(
                message.content[len(CMD_LEADER):],
                message.channel,
                message.author,
            )

    @staticmethod
    def get_salutation(author):
        first_name = author.display_name.split()[0]
        name_ending = list(first_name)[-1]
        if name_ending == 'a':
            return "My Lady"
        return "Sir"

    @staticmethod
    def has_permissions(author, required_level):
        try:
            perms = author.guild_permissions
            if required_level == 0:
                return True
            if required_level == 1:
                return any([
                    perms.administrator,
                    perms.manage_channels,
                    perms.manage_guild,
                    perms.manage_nicknames,
                    perms.manage_messages,
                    perms.manage_roles,
                ])
            if required_level == 2:
                return perms.administrator
            return False
        except:
            return False

    async def execute_order(self, cmd, channel, author):
        cmd = cmd.strip()
        if cmd.startswith(HELP):
            await FirmusPiett.print_help(cmd[len(HELP):], channel, author)
        elif cmd.startswith(NEW_CODE):
            await self.new_code(cmd[len(NEW_CODE):], channel, author)
        elif cmd.startswith(REPORT):
            await self.report(cmd[len(REPORT):], channel, author)
        else:
            await FirmusPiett.bad_command(channel, author)

    @staticmethod
    async def print_help(cmd, channel, author):
        salutation = FirmusPiett.get_salutation(author)
        cmd = cmd.strip()
        if not cmd in ["", "!", "."]:
            await FirmusPiett.bad_command(channel, author)
        ans = f"Calm down, {salutation}, I'm here.\n" \
              "You can ask me for `report` to see current state of the door " \
              "and last time when it was updated.\n" \
              "You can also order me to `new code n`, so I would display " \
              "the state of the door in different ways."
        await channel.send(ans)

    async def new_code(self, cmd, channel, author):
        salutation = FirmusPiett.get_salutation(author)
        if not FirmusPiett.has_permissions(author, 1):
            await channel.send(
                f"{salutation}, your powers are insufficient to set a new code."
            )
            return
        cmd = cmd.strip()
        try:
            cmd = int(cmd)
            if 0 <= cmd < len(self._communicate.communicates):
                self._communicate.set_current(cmd)
                self._last_code = -1
                await channel.send(f"Yes {salutation}! Code {cmd}")
            else:
                await channel.send(f"{salutation}, code {cmd} is out of the protocol!")
        except:
            await FirmusPiett.bad_command(channel, author)

    async def report(self, cmd, channel, author):
        salutation = FirmusPiett.get_salutation(author)
        cmd = cmd.strip()
        if cmd not in ["", "!", "."]:
            await FirmusPiett.bad_command(channel, author)
        await self.refresh_status()
        ans = ""
        if self._last_code == 0:
            ans += f"{salutation}, according to our intelligence the door is closed.\n"
        elif self._last_code == 1:
            ans += f"{salutation}, according to our intelligence the door is open.\n"
        else:
            ans += f"{salutation}, despite many Bothans died, " \
                    "we have not determined the state of the door.\n"
        if self.last_update is None:
            ans += "We haven't received any information from them yet."
        elif self.last_update.year < 2000:
            ans += "We haven't received any information from them yet."
        else:
            ans += "Last update from Tydirium was received "
            ans += self.last_update.strftime("%d.%m.%Y at %H:%M:%S.")
        await channel.send(ans)

    @staticmethod
    async def bad_command(channel, author):
        salutation = FirmusPiett.get_salutation(author)
        await channel.send(f"We have some communication disruption, {salutation}. Please repeat.")


if __name__ == "__main__":
    piett = FirmusPiett(HOST_NAME, PORT)
    piett.run(PIETT_TOKEN)
