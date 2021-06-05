# import nonebot
from nonebot import get_driver
from nonebot.plugin import on_notice
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
import random
from . import data_source

from .config import Config

global_config = get_driver().config
config = Config(**global_config.dict())


Notice_Match = on_notice(priority=1, block=True)


@Notice_Match.handle()
async def handle_receive_notice(bot: Bot, event: Event, state: T_State):
    NoticeType = event.notice_type
    if NoticeType == "group_admin":
        if event.sub_type == "set":
            await Notice_Match.finish(message="一顶崭新的绿帽升起了")
        else:
            await Notice_Match.finish(message="一名伟大的管理落幕了")
    elif NoticeType == "group_decrease" and event.sub_type == "leave":
        await Notice_Match.finish(message="有不好的事情发生了")
    elif NoticeType == "group_increase":
        reply_message = [{"type": "at", "data": {"qq": "{}".format(event.user_id)}}, {
            "type": "text", "data": {"text": "，欢迎加入本群"}}]
        await Notice_Match.finish(message=reply_message)
    elif NoticeType == "notify" and event.sub_type == "poke" and str(event.sender_id) != bot.self_id and str(event.target_id) == bot.self_id:
        reply_mes = [{"type": "poke", "data": {
            "qq": "{}".format(event.user_id)}}]
        if event.user_id == data_source.Gay_id:
            reply_mes += data_source.NudgeSet[random.randint(
                0, len(data_source.NudgeSet) - 1)]
        await Notice_Match.finish(message=reply_mes)
        # Export something for other plugin
        # export = nonebot.export()
        # export.foo = "bar"

        # @export.xxx
        # def some_function():
        #     pass
