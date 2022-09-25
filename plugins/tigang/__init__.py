# import nonebot
from nonebot import require
from nonebot import get_driver
import nonebot
import time

from .config import Config
from . import data_source

global_config = get_driver().config
config = Config(**global_config.dict())


scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", hour=11, minute=0)
async def Tigang():
    bot = nonebot.get_bots().get("2216682142")
    await bot.call_api(api="send_group_msg", group_id=data_source.ABanG_id,
                           message="喝水运动不要久坐")
