from telethon import TelegramClient, events, sync

import httpx
import yaml
import time
import json
import os
import re
import asyncio
import logging
from typing import *

# pip3 install telethon pysocks httpx pyyaml 或者 py -3 -m pip install telethon pysocks httpx pyyaml
# 云函数用户本地脚本路径,自动解析serverless.yml cookie
#path: Final = "/XXXXXX/jd_scripts"

'''
def get_ck() -> str:
    with open(os.path.join(path, "serverless.yml"), "r") as f:
        data: dict = yaml.load(f, Loader=yaml.CLoader)
    env: dict = data["inputs"]["environment"]["variables"]
    return "&".join(env["JD_COOKIE"])

'''
# cookies中间用&分开
# 云函数自动解析.非云函数手动替换get_ck()为'ck1&ck2'
cks='pt_key=AAJgNlFQADBu4izQthB-Pj5hz-hY7PQAz-emb3YTd9vFu53zOewc6Fk1oVBS4EADAgYbISEwnnY;pt_pin=jd_499678af3e75e;'

# url1 = 'https://api.m.jd.com/client.action?functionId=liveDrawLotteryV842&body={"lotteryId":666351,"liveId":3656131}&uuid=8888888&client=apple&clientVersion=9.4.1&st=1615429563038&sign=17c699f8504b22f3e0bf961f7a7d941e&sv=121'

total_bean: int = 0


async def send_live(cks: str, url: str, shop: str) -> None:
    if len(cks) > 0:
        str_ck = cks.split("&")
        for i in range(1, len(str_ck) + 1):
            if len(str_ck[i - 1]) > 0:
                # print(str_ck[i-1])
                # header
                header = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
                    "Cookie": str_ck[i - 1],
                }
                # 访问url
                async with httpx.AsyncClient() as client:
                    r = await client.get(url=url, headers=header)
                # r = await httpx.get(url=url, headers=header)
                bean = json.loads(r.text)["data"]["couponQuota"]
                if bean is None:
                    logging.info(f"{shop}啥也没中!")
                else:
                    bean = int(bean[:-2])
                    logging.debug(bean)
                    global total_bean
                    total_bean += bean
                    logging.info(f"{shop}中了{bean}京豆.挂机开始共{total_bean}京东")
                await asyncio.sleep(0.5)


# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
# 必须填写 api_id api_hash proxy
api_id = '3420052'
api_hash = "ec130bf6eb5a4b0710e6e989cbb7dd28"
# 使用代理proxy
client = TelegramClient("test", api_id, api_hash)
# 不使用代理
# client = TelegramClient('test', api_id, api_hash)

p1=re.compile(r"[(](.*?)[)]", re.S)


@client.on(events.NewMessage(incoming=True, chats="🍉&🐱&🥔", from_users="直播间京豆📢"))
async def my_event_handler(event):
    if "跳转直播间抽奖" in event.raw_text and "抽奖直达" in event.raw_text:
        # logging.info(event.message)
        shop: str = event.message.message.split("\n")[0].split(" ")[0]
        sec = re.findall(p1, event.message.text)
        if sec != None and len(sec) == 2:
            await send_live(cks, sec[1], shop)
        else:
            logging.error(f"failed to extract url,msg:{event.message}")


if __name__ == "__main__":
    # 输出到指定文件
    # logging.basicConfig(filename='XXXXXX',level=logging.INFO)
    logging.basicConfig(level=logging.INFO)
    with client:
        # client.loop.run_until_complete(main())
        client.loop.run_forever()
