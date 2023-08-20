import datetime
import os
from telethon.sync import TelegramClient
from dotenv import load_dotenv
from telethon.tl.types import MessageEntityBold, MessageEntityItalic, MessageEntityStrike


load_dotenv()
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')


class ChatParser(TelegramClient):
    channels = []

    @classmethod
    def instance(cls, api_id, api_hash):
        return cls('Parser', api_id=api_id, api_hash=api_hash)
    
    def add_channel(self, channel: str):
        self.channels.append(channel)

    def parse_text(self, message):
        text_to_modify = message.message
        bold_text = message.get_entities_text(MessageEntityBold)
        italic_text = message.get_entities_text(MessageEntityItalic)
        striked_text = message.get_entities_text(MessageEntityStrike)
        if len(bold_text) == 1:
            entity, inner_text = bold_text[0]
            text_to_modify = text_to_modify.replace(inner_text, '<b>' + inner_text + '</b>')
        if len(italic_text) == 1:
            entity, inner_text = italic_text[0]
            text_to_modify = text_to_modify.replace(inner_text, '<i>' + inner_text + '</i>')
        if len(italic_text) == 1:
            entity, inner_text = striked_text[0]
            text_to_modify = text_to_modify.replace(inner_text, '<strike>' + inner_text + '</strike>')
        print(text_to_modify)
        return text_to_modify

    async def parse(self, channel_index, offset_date=datetime.date.today()):   
        data = {}
        async for message in self.iter_messages(self.channels[channel_index], offset_date=offset_date, reverse=True):
            if message.__class__.__name__ == 'Message':
                print(message)
                if message.photo and message.grouped_id is None:
                    data[message.id] = [self.parse_text(message=message), await self.download_media(message.photo)]
                elif message.photo and message.grouped_id in data and message.message == '':
                    data[message.grouped_id][1].append(await self.download_media(message.photo))
                elif message.photo and message.grouped_id is not None:
                    data[message.grouped_id] = [self.parse_text(message=message), [await self.download_media(message.photo)]]
                else:            
                    data[message.id] = [self.parse_text(message=message), None]
        return data
        