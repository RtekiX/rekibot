# import nonebot
from nonebot import require
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot import get_driver
from nonebot.exception import FinishedException
from nonebot.rule import to_me
from nonebot import on_keyword
import nonebot
import pymysql

from .config import Config
from . import data_source

global_config = get_driver().config
config = Config(**global_config.dict())


scheduler11 = require("nonebot_plugin_apscheduler").scheduler
scheduler22 = require("nonebot_plugin_apscheduler").scheduler
Check = on_keyword(keywords=["打卡"], rule=to_me(), priority=2, block=True)


# 每天0点确认今天是否打卡
@scheduler11.scheduled_job("cron", hour=23, minute=59)
async def Tiyixia():
    db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                         password=data_source.DB_PASS, database=data_source.DB_NAME,
                         charset=data_source.DB_CHARSET)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    Group_id = 742366168
    GetAll = "select * from check_{0}".format(Group_id)
    cursor.execute(GetAll)
    result = cursor.fetchall()
    daily_message = "今日未打卡:\n"
    for row in result:
        is_check = row.get('TodayCount')
        ID = row.get('ID')
        act = row.get('ACT')
        if is_check == 1:
            update_info = "update check_{0} set TodayCount='{1}' where (ID='{2}' and ACT='{3}')".format(
                Group_id, 0, ID, act)
            cursor.execute(update_info)
            db.commit()
        else:
            update_info = "update check_{0} set SeqCount='{1}',TodayCount='0' where (ID='{2}' and ACT='{3}')".format(
                Group_id, 0, ID, act)
            cursor.execute(update_info)
            db.commit()
            daily_message += "用户({})，{}\n".format(
                data_source.ID_name_dict[ID], act)
    daily_message += '连续打卡天数已清零'
    bot = nonebot.get_bots().get("2216682142")
    await bot.call_api(api="send_group_msg", group_id=Group_id, message=daily_message)


@scheduler22.scheduled_job("cron", hour=18, minute=0)
async def Tixing():
    bot = nonebot.get_bots().get("2216682142")
    await bot.call_api(api="send_group_msg", group_id=742366168,
                           message="记得完成每日任务")


@Check.handle()
async def handle_daily_check(bot: Bot, event: Event, state: T_State):
    GroupId = str(event.group_id)
    if GroupId not in data_source.allowedID:
        raise FinishedException

    message_text = event.get_plaintext()
    act = message_text[message_text.find('卡')+1:]  # 打卡的活动名
    user_id = event.user_id
    str_user_id = str(user_id)

    # 打开数据库连接, 将这里的连接信息替换为你的数据库连接信息
    db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                         password=data_source.DB_PASS, database=data_source.DB_NAME,
                         charset=data_source.DB_CHARSET)
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)

    # 如果表不存在则创建一张新表
    create_table = """CREATE TABLE IF NOT EXISTS check_{0} (
         ID  VARCHAR(255) NOT NULL,
         ACT  VARCHAR(255) NOT NULL,
         TodayCount INT,
         TotalCount INT,
         SeqCount INT) CHARSET=utf8mb4""".format(GroupId)
    cursor.execute(create_table)
    db.commit()
    # 检查数据库中有无用户
    check_user = "select * from check_{0} where (ID='{1}' and ACT='{2}')".format(
        GroupId, user_id, act)
    cursor.execute(check_user)
    res = cursor.fetchone()
    if res == None:
        create_user = "insert into check_{5} (ID,ACT,TodayCount,TotalCount,SeqCount) values('{0}','{1}','{2}','{3}','{4}')".format(
            user_id, act, 1, 1, 1, GroupId)
        cursor.execute(create_user)
        db.commit()
        db.close()
        await Check.finish("用户({0})今日【{1}】打卡成功，连续打卡{2}天，总打卡次数:{3}".format(data_source.ID_name_dict[str_user_id], act, 1, 1))
    else:
        is_check = int(res.get('TodayCount'))
        count_num_old = int(res.get('TotalCount'))
        if is_check == 1:
            db.close()
            await Check.finish("用户({0})今日【{1}】已打卡".format(data_source.ID_name_dict[str_user_id], act))
        else:
            Seq_count_old = int(res.get('SeqCount'))
            Seq_count_new = Seq_count_old + 1
            count_num_new = count_num_old + 1
            add_check = "update check_{0} set TodayCount={1},TotalCount='{2}',SeqCount='{5}' where (ID='{3}' and ACT='{4}')".format(
                GroupId, 1, count_num_new, user_id, act, Seq_count_new)
            cursor.execute(add_check)
            db.commit()
            db.close()
            await Check.finish("用户({0})今日【{1}】打卡成功，连续打卡{2}天，总打卡次数:{3}".format(data_source.ID_name_dict[str_user_id], act, Seq_count_new, count_num_new))
    # Export something for other plugin
    # export = nonebot.export()
    # export.foo = "bar"

    # @export.xxx
    # def some_function():
    #     pass
