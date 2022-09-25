# import nonebot
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot import require
from nonebot import get_driver
import nonebot
from nonebot import on_keyword
import pymysql
import random

from .config import Config
from . import data_source

global_config = get_driver().config
config = Config(**global_config.dict())

pihuaCount = on_keyword(keywords="批话", priority=2, block=True)


@pihuaCount.handle()
async def handle_pihua(bot: Bot, event: Event, state: T_State):
    GroupId = str(event.group_id)
    UserId = event.get_user_id()
    UserName = event.sender.card
    if UserName == "":
        UserName = event.sender.nickname
    # 将这里的ShitGroupList替换成需要记录的群
    if GroupId in data_source.pihuaGroupList and UserId != bot.self_id:
        # 打开数据库连接, 将这里的连接信息替换为你的数据库连接信息
        db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                             password=data_source.DB_PASS, database=data_source.DB_NAME,
                             charset=data_source.DB_CHARSET)
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)

        # 如果表不存在则创建一张新表
        create_table = """CREATE TABLE IF NOT EXISTS phcount_{0} (
         UserId  VARCHAR(255) NOT NULL,
         phCount  INT(255),
         NickName  VARCHAR(255)) CHARSET=utf8mb4""".format(GroupId)
        cursor.execute(create_table)
        # db.commit()
        # 检查数据库中有无用户
        check_user = "select * from phcount_{0} where UserId='{1}'".format(
            GroupId, UserId)
        cursor.execute(check_user)
        if cursor.fetchone() == None:
            create_user = "insert into phcount_{3} (UserId,phCount,NickName) values('{0}',{1},'{2}')".format(
                UserId, 1, UserName, GroupId)
            cursor.execute(create_user)
            db.commit()
        else:
            add_count = "update phcount_{2} set phCount=phCount+1,NickName='{0}' where UserId='{1}'".format(
                UserName, UserId, GroupId)
            cursor.execute(add_count)
            db.commit()
        db.close()


scheduler2 = require("nonebot_plugin_apscheduler").scheduler


@scheduler2.scheduled_job("interval", days=7)
async def countTotalPihua():
    # 打开数据库连接, 将这里的连接信息替换为你的数据库连接信息
    bot = nonebot.get_bots().get("2216682142")

    db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                         password=data_source.DB_PASS, database=data_source.DB_NAME,
                         charset=data_source.DB_CHARSET)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    for GroupNumber in data_source.pihuaGroupList:
        find_max = "select * from phcount_{0} order by phCount desc".format(
            GroupNumber)
        cursor.execute(find_max)
        max_user = cursor.fetchone()
        if max_user != None:
            max_user_nickname = max_user.get("NickName")
            max_user_count = max_user.get("phCount")
            await bot.call_api(api="send_group_msg", group_id=int(GroupNumber),
                               message="近7天内{0}使用了{1}次批话功能，为本群之最".format(max_user_nickname, str(max_user_count)))
        clear_table = "truncate table phcount_{0}".format(GroupNumber)
        cursor.execute(clear_table)
        db.commit()
    db.close()

    # Export something for other plugin
    # export = nonebot.export()
    # export.foo = "bar"

    # @export.xxx
    # def some_function():
    #     pass
