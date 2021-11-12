from . import data_source
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.exception import FinishedException
import requests
import os
import time
import timeout_decorator

image = on_command("上传给图", rule=None, priority=3)


@image.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    Gruop_id = str(event.group_id)
    User_id = event.get_user_id()
    if Gruop_id not in data_source.allowed_group or User_id in data_source.baned_id:
        raise FinishedException
    args = str(event.get_message()).strip()  # 首次发送命令时跟随的参数
    if args:
        state["image_content"] = args  # 如果用户发送了参数则直接赋值


@timeout_decorator.timeout(120)
@image.got("image_content", prompt="发送需要上传的图片，没有则回复结束")
async def handle_image_content(bot: Bot, event: Event, state: T_State):
    Gruop_id = str(event.group_id)
    User_id = event.get_user_id()
    if Gruop_id not in data_source.allowed_group or User_id in data_source.baned_id:
        raise FinishedException
    image_content = state["image_content"]
    if image_content == "结束":
        await image.finish("上传结束")
    else:
        img_url = image_content.split(',')[2][4:-1]
        urlup(img_url, event.get_user_id(), str(event.group_id))
        await image.reject("继续")


def urlup(url, uploader, up_group):
    filepath = "../../gay_image"
    if not os.path.exists(filepath):  # 判断当前路径是否存在，没有则创建new文件夹
        os.makedirs(filepath)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    cont = requests.get(url=url, headers=headers)
    print(cont.headers["Content-Type"])
    t = str(int(time.time())) + "." + \
        cont.headers["Content-Type"].split("/")[1]
    filename = "{0}/{2}_{3}_{1}".format(filepath, t, up_group, uploader)
    with open(filename, 'wb+') as f2:
        f2.write(cont.content)
