from nonebot.adapters import Bot, Event
from nonebot.exception import FinishedException
from nonebot.typing import T_State
from nonebot import on_keyword
from nonebot import get_driver
import os
import random

from .config import Config
from . import data_source

global_config = get_driver().config
config = Config(**global_config.dict())


send_pihua = on_keyword(data_source.keyword_set, rule=None, priority=4, block=False)


@send_pihua.handle()
async def handle_send_pihua(bot: Bot, event: Event, state: T_State):
    Gruop_id = str(event.group_id)
    User_id = event.get_user_id()
    if Gruop_id not in data_source.allowed_group or User_id in data_source.baned_id:
        raise FinishedException
    if Gruop_id in data_source.allowed_group and User_id not in data_source.baned_id:
        filepath = "../../pihua_image"
        image_list = os.listdir(filepath)
        times = random.randint(0, len(image_list)-1)
        file_abs_path = "file:///" + \
            os.path.abspath(filepath) + "\\" + image_list[times],
        final_path = file_abs_path[0].replace('\\', '/')
        Content = [
            {
                "type": "image",
                "data": {
                    "file": final_path
                }
            }
        ]
        await send_pihua.finish(Content)

    # Export something for other plugin
    # export = nonebot.export()
    # export.foo = "bar"

    # @export.xxx
    # def some_function():
    #     pass
