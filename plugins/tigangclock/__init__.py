# import nonebot
from nonebot import require
from nonebot import get_driver
import nonebot

from .config import Config
from . import data_source

global_config = get_driver().config
config = Config(**global_config.dict())


scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("interval", minutes=600)
async def Tiyixia():
    bot = nonebot.get_bots().get("2216682142")
    await bot.call_api(api="send_group_msg", group_id=data_source.ABanG_id,
                       message="打扰一下，记得提⭕")
    # Export something for other plugin
    # export = nonebot.export()
    # export.foo = "bar"

    # @export.xxx
    # def some_function():
    #     pass
