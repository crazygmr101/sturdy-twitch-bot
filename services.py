from twitchbot.message import Message


async def add(m: Message):
    num = list(map(int, m.arg_list.split()))
    await m.bot.send(sum(num))