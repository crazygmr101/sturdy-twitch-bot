from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from twitchbot.bot import TwitchBot


@dataclass
class Message:
    """
    ``:crazygmr101!crazygmr101@crazygmr101.tmi.twitch.tv PRIVMSG #crazygmr101 :-say hi``

    full: `full content`

    content: -say hi

    user: crazygmr101

    channel: crazygmr101

    arg_list: hi

    cmd: say

    type: PRIVMSG
    """
    full: str
    content: str
    timestamp: datetime
    channel: str
    user: str
    arg_list: Optional[str]
    cmd:  Optional[str]
    type: str
    bot: TwitchBot
