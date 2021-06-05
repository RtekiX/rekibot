from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot import on_keyword
from nonebot import get_driver

from .config import Config
from . import data_source
import pymysql
import random


global_config = get_driver().config
config = Config(**global_config.dict())


# 因为关键词都比较恶臭所以放进别的文件了。可以自行创建关键词集[' ', ' ',..]
ShitCount = on_keyword(keywords=data_source.KeyWordSet, priority=2)


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
