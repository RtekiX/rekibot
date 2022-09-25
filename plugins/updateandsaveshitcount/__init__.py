# import nonebot
from nonebot import require
from nonebot import get_driver
import nonebot
import pymysql

from .config import Config
from . import data_source

global_config = get_driver().config
config = Config(**global_config.dict())


scheduler4 = require("nonebot_plugin_apscheduler").scheduler


@scheduler4.scheduled_job("cron", day=28, hour=22, minute=0)
async def UpdateAndSave():
    # 打开数据库连接, 将这里的连接信息替换为你的数据库连接信息
    bot = nonebot.get_bots().get("2216682142")

    db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                         password=data_source.DB_PASS, database=data_source.DB_NAME,
                         charset=data_source.DB_CHARSET)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    for GroupNumber in data_source.ShitGroupList:
        find_max = "select * from shitcount_{0} order by ShitCount desc".format(
            GroupNumber)
        cursor.execute(find_max)
        max_user = cursor.fetchone()
        if max_user != None:
            max_user_nickname = max_user.get("NickName")
            max_user_count = max_user.get("ShitCount")
            await bot.call_api(api="send_group_msg", group_id=int(GroupNumber),
                               message="本月的恶臭之王是{0}，他勇夺{1}个标记物，下个月继续努力".format(max_user_nickname, str(max_user_count)))
        clear_table = "truncate table shitcount_{0}".format(GroupNumber)
        cursor.execute(clear_table)
        db.commit()
    db.close()

    # Export something for other plugin
    # export = nonebot.export()
    # export.foo = "bar"

    # @export.xxx
    # def some_function():
    #     pass
