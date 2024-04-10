# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import os
import time
import socks
import argparse
import aiohttp
from telethon import events
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# 设置日志记录，便于调试和追踪程序运行情况。
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_args():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='Telegram Bot for Translating Messages')
    parser.add_argument('--session', type=str, required=True, help='Telegram session string')
    parser.add_argument('--api_id', type=str, required=True, help='Telegram API ID')
    parser.add_argument('--api_hash', type=str, required=True, help='Telegram API Hash')
    parser.add_argument('--proxy_host', type=str, default=None, help='Proxy host')
    parser.add_argument('--proxy_port', type=int, default=None, help='Proxy port')
    parser.add_argument('--config', type=str, default=None, help='Config file path')
    return parser.parse_args()

args = get_args()
config_path = args.config if args.config else './config.json'
session = args.session
api_id = args.api_id
api_hash = args.api_hash
proxy_host = args.proxy_host if args.proxy_host else "127.0.0.1"
proxy_port = args.proxy_port if args.proxy_port else 6153

def load_config():
    # load config from json file, check if the file exists first
    if not os.path.exists(config_path):
        # 创建config.json文件
        os.mknod('config.json')

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config

cfg = load_config()
target_config = cfg['target_config'] if 'target_config' in cfg else {}

if proxy_host and proxy_port:
    proxy = (socks.SOCKS5, proxy_host, proxy_port)
    # 初始化Telegram客户端和OpenAI客户端。
    client = TelegramClient(session=StringSession(session), api_id=api_id, api_hash=api_hash, proxy=proxy)
else:
    # 初始化Telegram客户端和OpenAI客户端。
    client = TelegramClient(session=StringSession(session), api_id=api_id, api_hash=api_hash)


def save_config():
    cfg['target_config'] = target_config
    with open(config_path, 'w') as f:
        json.dump(cfg, f, indent=2)

async def translate_single(text, source_lang, target_lang, session):
    if source_lang == target_lang:
        return target_lang, text

    url = "https://api.deeplx.org/translate"
    payload = {
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }

    start_time = time.time()
    async with session.post(url, json=payload) as response:
        logging.info(f"翻译从 {source_lang} 至 {target_lang} 耗时: {time.time() - start_time}")
        if response.status != 200:
            logging.error(f"翻译失败：{response.status}")
            raise Exception(f"翻译失败")

        result = await response.json()
        if result['code'] != 200:
            logging.error(f"翻译失败：{result}")
            raise Exception(f"翻译失败")

        return target_lang, result['data']


async def translate_text(text, source_lang, target_langs) -> {}:
    result = {}
    async with aiohttp.ClientSession() as session:
        tasks = [translate_single(text, source_lang, target_lang, session) for target_lang in target_langs]
        for lang, text in await asyncio.gather(*tasks):
            result[lang] = text

    return result


async def command_mode(event, target_key, text) -> bool:
    if text == '.tt-off':
        await event.delete()

        if target_key in target_config:
            del target_config[target_key]
            save_config()
            logging.info("已禁用: %s" % target_key)

        return False

    if text.startswith('.tt-on,'):
        await event.delete()

        _, source_lang, target_langs = text.split(',')
        target_config[target_key] = {
            'source_lang': source_lang,
            'target_langs': target_langs.split('|')
        }

        save_config()
        logging.info(f"设置成功: {target_config[target_key]}")

        return False

    return True


# 监听新消息事件，进行消息处理。
@client.on(events.NewMessage(outgoing=True))
async def handle_message(event):
    target_key = '%d.%d' % (event.chat_id, event.sender_id)
    try:
        message = event.message

        if not message.text:
            return

        message_content = message.text.strip()
        if not message_content:
            return

        if message_content.startswith('.tt-') and not await command_mode(event, target_key, message_content):
            return

        if target_key not in target_config:
            return

        logging.info(f"翻译消息: {message.text}")

        config = target_config[target_key]
        target_langs = config['target_langs']
        if not target_langs:
            return

        start_time = time.time()  # 记录开始时间
        translated_texts = await translate_text(message.text, config['source_lang'], target_langs)
        logging.info(f"翻译耗时: {time.time() - start_time}")

        modified_message = translated_texts[target_langs[0]]

        if len(target_langs) > 1:
            secondary_messages = []
            for lang in target_langs[1:]:
                secondary_messages.append(translated_texts[lang])

            modified_message += '\n```%s\n```' % '\n'.join(secondary_messages)

        await message.edit(modified_message)
    except Exception as e:
        # 记录处理消息时发生的异常。
        logging.error(f"Error handling message: {e}")


try:
    client.start()
    client.run_until_disconnected()
    
finally:
    # 断开客户端连接。
    client.disconnect()



# 以下代码为获取telegram的通知消息第一个为最新消息
# async def main():
#     entity = await client.get_entity(777000)
#     async for message in client.iter_messages(entity,1):
#         print(message.raw_text)

# try:
#     with client:
#         client.start()
#         client.loop.run_until_complete(main())
    
# finally:
#     # 断开客户端连接。
#     client.disconnect()
    