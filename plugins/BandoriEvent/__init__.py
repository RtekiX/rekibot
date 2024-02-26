# import nonebot
from nonebot import require
from nonebot import get_driver
import nonebot
import requests
import time

from .config import Config
from . import data_source

global_config = get_driver().config
config = Config(**global_config.dict())


scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", hour='*/12', minute=1)
async def Bang():
    r = requests.get("https://bestdori.com/api/events/all.3.json")
    jsonified_r = r.json()

    EventNum = len(jsonified_r) - 1
    EventName = jsonified_r[str(EventNum)]["eventName"][0]
    EventStart = jsonified_r[str(EventNum)]["startAt"][0]
    EventEnd = jsonified_r[str(EventNum)]["endAt"][0]

    t1 = float(time.time())
    t2 = float(int(EventEnd)/1000)

    Lefthour = int(t2 - t1)/3600

    if Lefthour > 0 and (Lefthour <= 24 or Lefthour <= 12):

        bot = nonebot.get_bots().get("3659953886")
        await bot.call_api(api="send_group_msg", group_id=data_source.baopo,
                           message="距离日服【{0}】活动结束不足{1}小时，没拿卡的抓紧了".format(EventName, str(int(Lefthour)+1)))