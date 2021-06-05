# import nonebot
from nonebot import require
from nonebot import get_driver
import nonebot
import pymysql
import csv
import datetime
import os

from .config import Config
from . import data_source

global_config = get_driver().config
config = Config(**global_config.dict())


scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", day=31, hour=22, minute=0)
async def UpdateAndSave():
    # 打开数据库连接, 将这里的连接信息替换为你的数据库连接信息
    bot = nonebot.get_bots().get("2216682142")

    db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                         password=data_source.DB_PASS, database=data_source.DB_NAME,
                         charset=data_source.DB_CHARSET)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    update_time = datetime.date.today()
    for GroupNumber in data_source.ShitGroupList:
        get_all_info = "select * from shitcount_{0}".format(GroupNumber)
        cursor.execute(get_all_info)
        check_exist = cursor.fetchone()
        if check_exist != None:

            cur_data = cursor.fetchall()
            filepath = "../../shit_count_csv"
            if not os.path.exists(filepath):  # 判断当前路径是否存在，没有则创建new文件夹
                os.makedirs(filepath)
            filename = "{0}/{1}_{2}.csv".format(filepath,
                                                GroupNumber, update_time)
            fp = open(filename, mode='w+', encoding='utf-8')
            write = csv.writer(fp, dialect='excel')
            for item in cur_data:
                write.writerow(item)
            find_max = "select * from shitcount_{0} order by ShitCount desc".format(
                GroupNumber)
            cursor.execute(find_max)
            max_user = cursor.fetchone()
            if max_user != None:
                max_user_nickname = max_user.get("NickName")
                max_user_count = max_user.get("ShitCount")
                await bot.call_api(api="send_group_msg", group_id=int(GroupNumber),
                                   message="本月的恶臭之王是{0}，他勇夺{1}个标记物，下个月也要努力哦".format(max_user_nickname, str(max_user_count)))
            clear_table = "truncate table shitcount_{0}".format(GroupNumber)
            cursor.execute(clear_table)
            db.commit()
        else:
            await bot.call_api(api="send_group_msg", group_id=int(GroupNumber),
                                   message="本月没有人获得标记物，无事发生！")
    db.close()

    # Export something for other plugin
    # export = nonebot.export()
    # export.foo = "bar"

    # @export.xxx
    # def some_function():
    #     pass
