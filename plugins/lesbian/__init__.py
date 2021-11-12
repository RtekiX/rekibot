from nonebot.adapters import Bot, Event
from nonebot.plugin import on_command
from nonebot.typing import T_State
from nonebot import on_message
from nonebot import get_driver
from nonebot.exception import FinishedException
import os
import random

from .config import Config
from . import data_source

global_config = get_driver().config
config = Config(**global_config.dict())


send_image = on_message(rule=None, priority=3, block=False)


@send_image.handle()
async def handle_send_image(bot: Bot, event: Event, state: T_State):
    Gruop_id = str(event.group_id)
    User_id = event.get_user_id()
    if Gruop_id not in data_source.allowed_group or User_id in data_source.baned_id:
        raise FinishedException
    if event.get_plaintext() in data_source.keyword_set:
        filepath = "../../uploaded_image"
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
        await send_image.finish(Content)

help_command = on_command("帮助", priority=3)


@help_command.handle()
async def handle_send_help(bot: Bot, event: Event, state: T_State):
    Gruop_id = str(event.group_id)
    User_id = event.get_user_id()
    if Gruop_id not in data_source.allowed_group or User_id in data_source.baned_id or event.get_plaintext() != "帮助":
        raise FinishedException
    filepath = "./plugins/lesbian"
    file_abs_path = "file:///" + \
        os.path.abspath(filepath) + "\\help.png",
    final_path = file_abs_path[0].replace('\\', '/')
    print(final_path)
    Content = [
        {
            "type": "image",
            "data": {
                "file": final_path
            }
        }
    ]
    await help_command.finish(Content)
    # Export something for other plugin
    # export = nonebot.export()
    # export.foo = "bar"

    # @export.xxx
    # def some_function():
    #     pass
