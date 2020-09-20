from __future__ import annotations

import asyncio
import datetime
import logging
from typing import Dict, Callable, Awaitable, List, Optional, Any

import websockets

from .message import Message


class TwitchBot:
    def __init__(self, token: str, channel: str, username: str, prefix: str):
        self.token = token
        self.channel = channel
        self.username = username
        self._command_callbacks: Dict[str, Callable[[Message], Awaitable[None]]] = {}
        self._state_callbacks: Dict[str, List[Callable[[TwitchBot], Awaitable[None]]]] = {}
        self._connection: Optional[websockets.WebSocketClientProtocol] = None
        self._prefix = prefix

    # region # websocket code
    async def _send(self, msg: str, prnt: str = None):
        logging.info(prnt or f"< {msg}")
        await self._connection.send(msg)

    async def _recv(self) -> str:
        msg = await self._connection.recv()
        for m in msg.splitlines(keepends=False):
            logging.info(f"> {m}")
        return msg

    async def _conv_msg(self, full) -> Message:
        m = [r.strip() for r in full.split(":")]
        content = m[2]
        if content.startswith(self._prefix):
            if len(m[2].split()) > 1:
                cmd = m[2][len(self._prefix):m[2].index(" ")]
                arg_list = m[2][m[2].index(" ") + 1:]
            else:
                cmd = m[2][len(self._prefix):]
                arg_list = None
        else:
            cmd = (arg_list := None)
        return Message(full, content, datetime.datetime.now(),
                       m[1].split()[2][1:],
                       m[1].split()[0].split("!")[0],
                       arg_list,
                       cmd,
                       m[1].split()[1],
                       self)

    # endregion

    # region # run/login
    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        await self.login()
        await self.loop()

    async def login(self):
        logging.info("Logging into twitch")
        self._connection = await websockets.connect("wss://irc-ws.chat.twitch.tv:443")
        await self._send(f"PASS {self.token}", prnt="PASS *****")
        await self._send(f"NICK {self.username}")
        await self._send(f"JOIN #{self.channel}")
        msg = ""
        while "End of /NAMES list" not in msg:
            msg = await self._recv()
        if "connect" in self._state_callbacks:
            await asyncio.gather(*(callback(self) for callback in self._state_callbacks["connect"]))

    async def loop(self):
        while True:
            msg = (await self._recv()).strip()
            if msg == "PING :tmi.twitch.tv":
                await self._send("PONG :tmi.twitch.tv")
                continue
            converted = await self._conv_msg(msg)
            if converted.user.lower() == self.username.lower():
                continue
            if converted.cmd and converted.cmd in self._command_callbacks:
                logging.info(f"calling {converted.cmd} with {converted.arg_list}")
                await self._command_callbacks[converted.cmd](converted)

    # endregion

    def add_command_callback(self, name: str, callback: Callable[[Message], Awaitable[None]]):
        if name in self._command_callbacks:
            raise ValueError("Callback already added")
        self._command_callbacks[name] = callback

    def add_state_callback(self, name: str, callback: Callable[[TwitchBot], Awaitable[None]]):
        if name not in ("connect", "disconnect"):
            raise ValueError
        if name not in self._state_callbacks:
            self._state_callbacks[name] = []
        self._state_callbacks[name].append(callback)

    async def send(self, msg: Any):
        await self._send(f"PRIVMSG #{self.channel} :{msg}")
