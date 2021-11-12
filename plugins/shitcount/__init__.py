from nonebot.adapters import Bot, Event
from nonebot.plugin import on_message, on_command
from nonebot.typing import T_State
from nonebot import on_keyword
from nonebot import get_driver
from nonebot.rule import to_me
import regex as re

from .config import Config
from . import data_source
import pymysql
import random


global_config = get_driver().config
config = Config(**global_config.dict())


# 因为关键词都比较恶臭所以放进别的文件了。可以自行创建关键词集[' ', ' ',..]
ShitCount = on_keyword(keywords=data_source.KeyWordSet,
                       priority=2, block=False)


@ShitCount.handle()
async def handle_shit_count(bot: Bot, event: Event, state: T_State):
    GroupId = str(event.group_id)
    UserId = event.get_user_id()
    UserName = event.sender.card
    if UserName == "":
        UserName = event.sender.nickname
    # 将这里的ShitGroupList替换成需要记录的群
    if GroupId in data_source.ShitGroupList and UserId != bot.self_id:
        # 打开数据库连接, 将这里的连接信息替换为你的数据库连接信息
        db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                             password=data_source.DB_PASS, database=data_source.DB_NAME,
                             charset=data_source.DB_CHARSET)
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)

        # 如果表不存在则创建一张新表
        create_table = """CREATE TABLE IF NOT EXISTS shitcount_{0} (
         UserId  VARCHAR(255) NOT NULL,
         ShitCount  INT(255),
         NickName  VARCHAR(255)) CHARSET=utf8mb4""".format(GroupId)
        cursor.execute(create_table)
        # db.commit()
        # 检查数据库中有无用户
        check_user = "select * from shitcount_{0} where UserId='{1}'".format(
            GroupId, UserId)
        cursor.execute(check_user)
        if cursor.fetchone() == None:
            create_user = "insert into shitcount_{3} (UserId,ShitCount,NickName) values('{0}',{1},'{2}')".format(
                UserId, 1, UserName, GroupId)
            cursor.execute(create_user)
            db.commit()
            await ShitCount.finish("恭喜{}获得第一个标记物，请继续努力".format(UserName))
        else:
            add_count = "update shitcount_{2} set ShitCount=ShitCount+1,NickName='{0}' where UserId='{1}'".format(
                UserName, UserId, GroupId)
            cursor.execute(add_count)
            db.commit()
            get_count = "select ShitCount from shitcount_{1} where UserId='{0}'".format(
                UserId, GroupId)
            cursor.execute(get_count)
            cur_count = cursor.fetchone().get('ShitCount')
            finalreply = "{0}标记物+1，当前有{1}个标记物，".format(
                UserName, cur_count) + data_source.ReplySet[random.randint(0, len(data_source.ReplySet) - 1)]
            await ShitCount.finish(finalreply)
        db.close()

        # Export something for other plugin
        # export = nonebot.export()
        # export.foo = "bar"

        # @export.xxx
        # def some_function():
        #     pass
ShitCountShow = on_message(priority=6)


# 查询标记物个数的命令
@ShitCountShow.handle()
async def handle_shit_count_show(bot: Bot, event: Event, state: T_State):
    GroupId = str(event.group_id)
    if event.get_plaintext() == "标记物记录" and GroupId in data_source.ShitGroupList:
        db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                             password=data_source.DB_PASS, database=data_source.DB_NAME,
                             charset=data_source.DB_CHARSET)
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(
            "select * from shitcount_{}".format(GroupId))
        result_message = "标记物数量：\n\n"
        result = cursor.fetchall()
        for row in result:
            user_name = row.get("NickName")
            user_count = row.get("ShitCount")
            result_message += "{0}：{1}\n".format(user_name, user_count)
        result_message += "请各位继续努力！"
        db.close()
        await ShitCountShow.finish(result_message)

# 关键词触发，必须@机器人
Debt = on_keyword(keywords=["标记物"], rule=to_me(),
                  priority=2, block=True)

'''
使用方法：
    发送消息："@bot 标记物[number] @被标记人"
    number：正有理数或负有理数，正数不必加+，负数需要加-

返回：
    波特："[被标记人昵称]现在有[标记数]个标记"
    标记数会更新到数据库中
'''


@Debt.handle()
async def handle_shit_change(bot: Bot, event: Event, state: T_State):

    if event.get_user_id() != data_source.SuperUser:
        await Debt.finish("你无法操纵标记物")
    GroupId = str(event.group_id)  # Nonebot1  获取当前群聊的号码
    message_text = event.get_message()
    number_list = re.findall("[+|-]?\d+.?\d*", message_text[0].data['text'])

    debt_num = int(number_list[0])
    DayeID = int(message_text[1].data['qq'])
    DayeInfo = await bot.call_api(api="get_group_member_info", group_id=event.group_id,
                                  user_id=DayeID, no_cache=False)
    DayeNickName = DayeInfo.get("card")
    if DayeNickName == "":
        DayeNickName = DayeInfo["nickname"]
    # 将这里的ShitGroupList替换成需要记录的群
    if GroupId in data_source.ShitGroupList:
        # 打开数据库连接, 将这里的连接信息替换为你的数据库连接信息
        db = pymysql.connect(host=data_source.DB_HOST, user=data_source.DB_USER,
                             password=data_source.DB_PASS, database=data_source.DB_NAME,
                             charset=data_source.DB_CHARSET)
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)

        # 如果表不存在则创建一张新表
        create_table = """CREATE TABLE IF NOT EXISTS shitcount_{0} (
         UserId  VARCHAR(255) NOT NULL,
         ShitCount  INT(255),
         NickName  VARCHAR(255)) CHARSET=utf8mb4""".format(GroupId)
        cursor.execute(create_table)
        db.commit()
        # 检查数据库中有无用户
        check_user = "select ShitCount from shitcount_{0} where UserId='{1}'".format(
            GroupId, DayeID)
        cursor.execute(check_user)
        res = cursor.fetchone()
        if res == None:
            create_user = "insert into shitcount_{0} (UserId,ShitCount,NickName) values('{1}',{2},'{3}')".format(
                GroupId, DayeID, debt_num, DayeNickName)
            cursor.execute(create_user)
            db.commit()
            await Debt.finish("{0}当前有{1}个标记物".format(DayeNickName, debt_num))
        else:
            shit_count_old = int(res.get("ShitCount"))
            shit_count_new = shit_count_old + debt_num
            add_count = "update shitcount_{0} set ShitCount={1},NickName='{2}' where UserId='{3}'".format(
                GroupId, shit_count_new, DayeNickName, DayeID)
            cursor.execute(add_count)
            db.commit()

            finalreply = "{0}当前有{1}个标记物".format(DayeNickName, shit_count_new)
            await Debt.finish(finalreply)
        db.close()
