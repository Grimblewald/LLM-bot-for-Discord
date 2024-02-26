# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 17:04:57 2024

@author: frith
"""

import discord
from datetime import datetime, timedelta
import asyncio
from LLM_funcs import llm_completion, check_if_called, trivia_module, generalqa_module, load_api_key
import random

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return
        
        call_status = await check_if_called(user_message=message.content)
# =============================================================================
#         
#         print(message.content)
#         print(call_status.choices[0].message.content)
# =============================================================================
    
        if call_status.choices[0].message.content == "trivia":
            await trivia_module(message=message, client=self)
        if call_status.choices[0].message.content == "generalQA":
            await generalqa_module(message=message, client=self)
        elif call_status.choices[0].message.content == "unsure":
            await message.channel.send("I'm not sure I can do this kind of thing yet, let's see if fritz can make it happen!")
        elif call_status.choices[0].message.content == "false":
            print("A message was sent, but it does not seem to call me")
            
    async def schedule_trivia(self):
        now = datetime.now()
        if now.hour < 9:
            start_time = datetime(now.year, now.month, now.day, 2, 52, 0)
        else:
            start_time = datetime(now.year, now.month, now.day + 1, 9, 0, 0)

        timeout_time = datetime(now.year, now.month, now.day, 21, 0, 0)

        time_until_start = start_time - now
        time_until_timeout = timeout_time - now

        await asyncio.sleep(time_until_start.total_seconds())

        await self.start_trivia()

        await asyncio.sleep(time_until_timeout.total_seconds())

        await self.timeout_trivia()

    async def start_trivia(self):
        channel = self.get_channel("#trivia")  # Replace CHANNEL_ID with the actual channel ID where you want to start the trivia
        await channel.send("Trivia module starting now!")
        await trivia_module(message=None, client=self)

    async def timeout_trivia(self):
        channel = self.get_channel("#trivia")  # Replace CHANNEL_ID with the actual channel ID where you want to send the timeout message
        await channel.send("Trivia module timeout reached!")


intents = discord.Intents.default()
intents.message_content = True

games = ["Team Fortress 3","Portal 3", "Portal 3", "with matches", "the fiddle", "Human"]
playing_game = random.choice(games)

client = MyClient(intents=intents, activity=discord.Game(name=playing_game))
client.run(load_api_key("discord"))


