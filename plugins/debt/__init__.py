from nonebot.adapters import Bot, Event
from nonebot.plugin import on_command
from nonebot.typing import T_State
from nonebot.rule import to_me
from nonebot import on_keyword
from nonebot import get_driver
import regex as re

from .config import Config
from . import data_source
import pymysql

# Nonebot1 里没有或者不需要的东西你自己看着删一哈


global_config = get_driver().config
config = Config(**global_config.dict())


# Nonebot1 关键词触发，必须@机器人
DebtAdd = on_keyword(keywords=["债务"], rule=to_me(),
                     priority=2, block=True)

'''
使用方法：
    债主发送消息："@龙bot 债务[number] @欠款人"
    number：正有理数或负有理数，正数不必加+，负数需要加-

返回：
    龙波特："[欠款人昵称]欠[债主昵称][债务]元"
    债务为负就是反向欠钱了
    债务会更新到数据库中
'''


@DebtAdd.handle()
async def handle_shit_count(bot: Bot, event: Event, state: T_State):
    # group_id 是int
    GroupId = str(event.group_id)  # Nonebot1  获取当前群聊的号码

    message_text = event.get_message()
    number_list = re.findall("[+|-]?\d+.?\d*", message_text[0].data['text'])
    debt_num = float(number_list[0])

    SunziID = event.get_user_id()  # Nonebot1 获取发送消息的人的QQ号
    SunziNickName = event.sender.card  # Nonebot1 获取发送消息的人的群名片
    if SunziNickName == "":
        SunziNickName = event.sender.nickname  # Nonebot1 获取发送消息的人的QQ昵称

    DayeID = int(message_text[1].data['qq'])
    DayeInfo = await bot.call_api(api="get_group_member_info", group_id=event.group_id,
                                  user_id=DayeID, no_cache=False)
    DayeNickName = DayeInfo.get("card")

    if DayeNickName == "":
        DayeNickName = DayeInfo["nickname"]
    # 将这里的ShitGroupList替换成需要记录的群
    if GroupId in data_source.ShitGroupList and SunziID != DayeID:
        # 打开数据库连接, 将这里的连接信息替换为你的数据库连接信息
        db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                             password=data_source.DB_PASS, database=data_source.DB_NAME,
                             charset=data_source.DB_CHARSET)
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)

        # 如果表不存在则创建一张新表
        # 欠钱的是大爷，债主是孙子
        create_table = """CREATE TABLE IF NOT EXISTS debt_{0} (
         DayeId  VARCHAR(255) NOT NULL,
         DebtNum  DOUBLE,
         DayeNickName  VARCHAR(255),
         SunziID VARCHAR(255) NOT NULL,
         SunziNickName VARCHAR(255)) CHARSET=utf8mb4""".format(GroupId)
        cursor.execute(create_table)
        db.commit()
        # 检查数据库中有无用户
        check_user = "select DebtNum from debt_{0} where (DayeId='{1}' and SunziID='{2}')".format(
            GroupId, DayeID, SunziID)
        cursor.execute(check_user)
        res = cursor.fetchone()
        if res == None:
            create_user = "insert into debt_{5} (DayeID,DebtNum,DayeNickName,SunziID,SunziNickName) values('{0}',{1},'{2}','{3}','{4}')".format(
                DayeID, debt_num, DayeNickName, SunziID, SunziNickName, GroupId)
            cursor.execute(create_user)
            db.commit()
            db.close()
            await DebtAdd.finish("【{0}({3})】 欠 【{1}({4})】 {2} 元".format(DayeNickName, SunziNickName, debt_num, DayeID, SunziID))
        else:
            debt_num_old = float(res.get('DebtNum'))
            debt_num_new = debt_num_old + debt_num
            add_debt = "update debt_{5} set DebtNum={0},DayeNickName='{1}',SunziNickName='{2}' where (DayeID='{3}' and SunziID='{4}')".format(
                debt_num_new, DayeNickName, SunziNickName, DayeID, SunziID, GroupId)
            cursor.execute(add_debt)
            db.commit()
            finalreply = "【{0}({3})】 欠 【{1}({4})】 {2} 元".format(
                DayeNickName, SunziNickName, debt_num_new, DayeID, SunziID)
            db.close()
            await DebtAdd.finish(finalreply)


# 完全匹配触发
ShitCountShow = on_command("债务记录", priority=6)


# 查询债务记录
@ShitCountShow.handle()
async def handle_shit_count_show(bot: Bot, event: Event, state: T_State):
    GroupId = str(event.group_id)
    if GroupId in data_source.ShitGroupList:
        db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                             password=data_source.DB_PASS, database=data_source.DB_NAME,
                             charset=data_source.DB_CHARSET)
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(
            "select * from debt_{0}".format(GroupId))
        result_message = "债务记录：\n---------------\n"
        result = cursor.fetchall()
        for row in result:
            daye_name = row.get("DayeNickName")
            sunzi_name = row.get("SunziNickName")
            daye_id = row.get("DayeId")
            sunzi_id = row.get("SunziID")
            okane_num = row.get("DebtNum")
            result_message += "【{0}({3})】 欠 【{1}({4})】 {2} 元\n".format(
                daye_name, sunzi_name, okane_num, daye_id, sunzi_id)
        result_message += "---------------"
        db.close()
        await ShitCountShow.finish(result_message)
