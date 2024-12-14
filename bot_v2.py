# bot.py
# Mr. Weather v2.0
import discord
from discord.ext import commands
import requests

import os
import datetime
from datetime import datetime
import pytz 

from dotenv import load_dotenv

bot_version: str = "1.0"

from keep_alive import keep_alive

# change working directory to wherever this file is located at
# for your reference: https://www.geeksforgeeks.org/python-os-path-abspath-method-with-example/
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# load bot token
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# client = discord.Client(intents=discord.Intents.default())
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# plz neglect this part
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Kingdom!'
    )

@client.command(name='timezones')
async def list_of_timezones(ctx):
    common_timezones = [
        'US/Eastern',
        'US/Pacific',
        'Europe/London',
        'Europe/Paris',
        'Asia/Tokyo',
        'Asia/Hong_Kong',
        'Australia/Sydney',
    ]

    timezone_list = '\n'.join(common_timezones)
    embed = discord.Embed(
        title = 'Common Timezones',
        description = f'Here are some common timezones you can choose:\n```{timezone_list}```\nUse with weather command like: !weather Hong Kong Asia/Hong_Kong',
        color = 0x7289DA
    )
    await ctx.send(embed = embed)

# weather forcast part
@client.command(name = 'weather')
async def get_weather(ctx, *, args):
    args = args.split()
    if len(args) < 1:
        await ctx.send('Please provide a city name!')
        return
    if '/' in args[-1]:
        timezone = args[-1]
        city = ' '.join(args[:-1])
    else:
        timezone = None
        city = ' '.join(args)
        
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            box1 = data['main']
            current_temperature = box1['temp']
            current_pressure = box1['pressure']
            current_humidity = box1['humidity']
            box2 = data['weather']
            description = box2[0]['description']

            # hk_tz = pytz.timezone('Asia/Hong_Kong')
            # created_hkt = ctx.message.created_at.astimezone(hk_tz)
            # formatted_datetime = created_hkt.strftime("%m/%d/%Y %I:%M %p HKT")
            current_time = ctx.message.created_at
            time_suffix = 'UTC'

            if timezone:
                try:
                    user_tz = pytz.timezone(timezone)
                    current_time = ctx.message.created_at.astimezone(user_tz)
                    time_suffix = timezone.replace('_', ' ')
                except pytz.exceptions.UnknownTimeZoneError:
                    await ctx.send(f'Invalid timezone: {timezone}. Using UTC instead.')
            
            formatted_datetime = current_time.strftime(f'%m/%d/%Y %I:%M %p {time_suffix}')

            embed = discord.Embed(
            title = f'Weather forescast - {city}',
            description = f'Hi, it is currently {formatted_datetime}',
            color = 0x7289DA
            )
            # embed.timestamp = created_hkt
            embed.timestamp = current_time
            
            embed.add_field(
                name = 'Description',
                value = f'**{description}**',
                inline= False
            )
            embed.add_field(
                name = 'Temperature(°C)',
                value = f'**{current_temperature}°C**',
                inline = False
            )
            embed.add_field(
                name = 'Humidity(%)', 
                value = f'**{current_humidity}**',
                inline = False
            )
            embed.add_field(
                name = 'Atmospheric Pressure(hPa)',
                value = f'**{current_pressure}**',
                inline = False
            )
            embed.set_footer(text = f'Requested by {ctx.author.name}')

            await ctx.send(embed = embed)
        else:
            await ctx.send(f'Error: Unable to fetch weather data for {city}.')

    except Exception as e:
        await ctx.send(f'An error occurred: {str(e)}')

keep_alive()
client.run(DISCORD_TOKEN)