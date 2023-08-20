import os
from telebot.async_telebot import AsyncTeleBot, types
import asyncio
from chat_parser import ChatParser
from dotenv import load_dotenv


load_dotenv()
TG_TOKEN = os.getenv('TG_TOKEN')
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')

bot = AsyncTeleBot(TG_TOKEN)
channels = []


async def get_data(channel):
    async with ChatParser.instance(api_id=API_ID, api_hash=API_HASH) as p:
        p.add_channel(channel)
        data = await p.parse(p.channels.index(channel))
        return data
    

# Asynchronous iterator. Can iterate through dictionaries and lists.
async def a_iter(data):
    if type(data) == dict:
        for k, v in data.items():
            yield k, v
    elif type(data) == list:
        for v in data:
            yield v


async def send(correspondence, channel):
    data = await get_data(channel)
    # Store photos here in order to delete them once they have been sent to the welcome channel
    photos = []
    async for _, data_chunk in a_iter(data=data):
        # print(data_chunk)
        if isinstance(data_chunk[1], list):
            pictures = []
            counter = 0
            async for picture in a_iter(data=data_chunk[1]):
                with open(picture, 'rb') as f:
                    counter += 1
                    if counter < 2:
                        pictures.append(types.InputMediaPhoto(f.read(), caption=data_chunk[0], parse_mode='HTML'))
                    else:
                        pictures.append(types.InputMediaPhoto(f.read(), caption=None, parse_mode='HTML'))
            photos.extend(data_chunk[1])
            try:
                await bot.send_media_group(correspondence.chat.id,
                                           media=pictures)
            except Exception as e:
                print(e)
        elif data_chunk[1] is not None:
            photos.append(data_chunk[1])
            with open(data_chunk[1], 'rb') as photo:
                await bot.send_photo(correspondence.chat.id,
                                     photo=photo,
                                     caption=f'{data_chunk[0]}',
                                     parse_mode='HTML')
        else: 
            await bot.send_message(correspondence.chat.id,
                                   f'{data_chunk[0]}',
                                   parse_mode='HTML')
    async for photo in a_iter(data=photos):
        os.remove(photo)


@bot.message_handler(commands=['start'])
async def start(correspondence):
    async for channel in a_iter(channels):
        try:
            await send(correspondence, channel)
        except Exception as e:        
            print(e)


@bot.message_handler(commands=['add_channels'])
async def set_channels(correspondence):
    channels.extend(correspondence.text.split())
    channels.remove('/add_channels')
    await bot.send_message(correspondence.chat.id,
                           'channels added:\n' + '\n'.join(channels))


@bot.message_handler(commands=['channels'])
async def display_channels(correspondence):
    if len(channels) != 0:
        await bot.send_message(correspondence.chat.id, '\n'.join(channels))
    else:
        await bot.send_message(correspondence.chat.id, 'There are no channels yet! Write down the channel(s) you want to track separated by blank spaces. Ex: /add_channels https://t.me/ru4chan')


async def add_channels(correspondence):
    await channels.append(correspondence.from_user.text.split())


async def main():
    await bot.infinity_polling()


asyncio.run(main())
