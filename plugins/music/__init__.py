from nonebot import on_command
from nonebot.exception import FinishedException
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import httpx
from . import data_source

weather = on_command("点歌", priority=4)


@weather.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    if str(event.group_id) in data_source.banned_group:
        raise FinishedException
    args = str(event.get_message()).strip()  # 首次发送命令时跟随的参数，例：点歌 XX，则args为XX
    if args:
        state["music"] = args  # 如果用户发送了参数则直接赋值


@weather.got("music", prompt="输入歌名")
async def handle_city(bot: Bot, event: Event, state: T_State):
    if str(event.group_id) in data_source.banned_group:
        raise FinishedException
    music_name = state["music"]
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"http://music.163.com/api/search/get/",
            data={"s": music_name, "limit": 1, "type": 1, "offset": 0},
        )
    jsonified_r = r.json()
    id = jsonified_r["result"]["songs"][0]["id"]
    songContent = [
        {
            "type": "music",
            "data": {
                "type": 163,
                "id": str(id)
            }
        }
    ]
    await weather.finish(songContent)
