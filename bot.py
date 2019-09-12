#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
import asyncio
from io import BytesIO
from PIL import Image, ImageTk, PngImagePlugin
import re
import sys
import threading
import time
import tkinter as tk
from urllib.request import urlopen

import discord
from discord.ext import commands

import pyowm
from time import localtime, strftime

_nonbmp = re.compile(r'[\U00010000-\U0010FFFF]')

def _surrogatepair(match):
   char = match.group()
   assert ord(char) > 0xffff
   encoded = char.encode('utf-16-le')
   return (
      chr(int.from_bytes(encoded[:2], 'little')) + 
      chr(int.from_bytes(encoded[2:], 'little')))

def with_surrogates(text):
   return _nonbmp.sub(_surrogatepair, text)

#Open Weather Map Stuff
owm = pyowm.OWM('YOUR_OWM_API_KEY')
wap = owm.weather_at_place('Berlin, DE')
weather = wap.get_weather()

# Discord Bot Stuff
token = "YOUR_DISCORD_BOT_TOKEN"
bot = commands.Bot(command_prefix='!')

async def start_discord_bot():
    await bot.start(token)

def run_bot_forever(loop):
    loop.run_forever()

def init_discord():
   print("╔═══════════════Jerry-Pi═══════════════╗")
   print("║ Initializing Discord Bot....         ║")

   loop = asyncio.get_event_loop()
   loop.create_task(start_discord_bot())

   thread = threading.Thread(target=run_bot_forever, args=(loop,))
   thread.start()
   print("║ Discord Bot running!                 ║")
   print("╚══════════════════════════════════════╝")
   print(" Current Weather: " + str(weather.get_temperature(unit='celsius')["temp"]) + " °C - " + weather.get_detailed_status())

@bot.command()
async def ppg(ctx, *args):
   print("[" + strftime("%Y-%m-%d %H:%M:%S", localtime())+ "] [Debug] Command \"ppg\" from " + ctx.author.name + " | " + '{} arguments | {}'.format(len(args), ' '.join(args)))
   await ctx.send('{}'.format(len(args), ' '.join(args)) + " 🦜")

@bot.command()
async def pi(ctx, *args):
   global canvas
   global discordMessage_text

   print("[" + strftime("%Y-%m-%d %H:%M:%S", localtime())+ "] [Debug] Command \"pi\" from " + ctx.author.name + " | " + '{} arguments | {}'.format(len(args), ' '.join(args)))
   canvas.itemconfig(discordMessage_text, text=with_surrogates("[" + strftime("%Y-%m-%d %H:%M:%S", localtime())+ "] " + ctx.author.name + ": " + '{}'.format(' '.join(args))))
   await ctx.send('Sent message to Jerry-Pi display! 📟')

# GUI Stuff (TKInter)
gui_root = tk.Tk()
gui_root.geometry("480x320")
gui_root.config(cursor="none")
gui_root.overrideredirect(1)

canvas = tk.Canvas(gui_root, width=480, height=320, bg="black", highlightthickness=0)

discordMessage_text = None

weatherTemp_text = "0"
weatherStatus_text = "None"
weatherIcon = None
weatherImage = None

time_text = "00:00"

def update_weather():
   global canvas
   global weatherTemp_text
   global weatherStatus_text
   global weatherIcon
   global weatherImage

   try:
      wap = owm.weather_at_place('Aurich,DE')
      weather = wap.get_weather()

      webRequest = urlopen(weather.get_weather_icon_url())
      raw_data = webRequest.read()
      webRequest.close()

      im = Image.open(BytesIO(raw_data))
      weatherImage = ImageTk.PhotoImage(im)

      canvas.itemconfig(weatherIcon, image=weatherImage)
      print("Weather Update: " + str(round(weather.get_temperature(unit='celsius')["temp"], 1)) + "°C - " + weather.get_detailed_status())
      print("Weather Icon: " + weather.get_weather_icon_url())
      canvas.itemconfig(weatherTemp_text, text=str(round(weather.get_temperature(unit='celsius')["temp"], 1)))
      canvas.itemconfig(weatherStatus_text, text=weather.get_detailed_status())
   except:
      print("Weather update failed.")

   gui_root.after(60000, update_weather)  # reschedule event in 1 minute

def update_time():
   global canvas
   global time_text
   canvas.itemconfig(time_text, text=strftime("%H:%M", localtime()))
   gui_root.after(1000, update_time)


def main():
   global canvas
   global discordMessage_text
   global weatherTemp_text
   global weatherStatus_text
   global weatherIcon
   global time_text


   #Main Canvas
   canvas.pack(side = "top", fill = "both", expand = True)

   #Weather Label (Temperature w/o "°C")
   weatherTemp_text = canvas.create_text(285, 215, anchor = "nw", fill="white", font = ('Open Sans', 42, 'bold'))
   canvas.itemconfig(weatherTemp_text, text=str(round(weather.get_temperature(unit='celsius')["temp"], 1)))

   #Weather Label ("°C" only)    
   weatherDeg_text = canvas.create_text(400, 225, anchor = "nw", fill="white", font = ('Open Sans', 30))
   canvas.itemconfig(weatherDeg_text, text="°C")

   #Weather Label (Status e.g. "Cloudy")
   weatherStatus_text = canvas.create_text(335, 295, anchor = "w", fill="white", font = ('Open Sans', 12))
   canvas.itemconfig(weatherStatus_text, text=weather.get_detailed_status())

   #Weather Icon
   u = urlopen(weather.get_weather_icon_url())
   raw_data = u.read()
   u.close()

   im = Image.open(BytesIO(raw_data))
   weatherImage = ImageTk.PhotoImage(im)

   weatherIcon = canvas.create_image(280,272, anchor="nw", image=weatherImage)

   #Discord Message Label
   discordMessage_text = canvas.create_text(10, 10, width=460, anchor = "nw", fill="white", font = ('Open Sans', 15))
   canvas.itemconfig(discordMessage_text, text="No new Discord message. :(")

   #Time Label (Format HH:MM)
   time_text = canvas.create_text(10, 200, anchor = "nw", fill="white", font = ('Open Sans', 72))
   canvas.itemconfig(time_text, text=strftime("%H:%M", localtime()))

   #Time Separator Line
   canvas.create_line(270, 227, 270, 310, fill="#FFFFFF", width=7.0)


   init_discord()
   gui_root.after(1000, update_time)  # reschedule event in 1 second
   gui_root.after(60000, update_weather)  # reschedule event in 1 minute
   gui_root.mainloop()

if __name__ == '__main__':
   try:
      main()
   except KeyboardInterrupt:
      gui_root.destroy()
      print("\nExiting by user request.\n")
      sys.exit(0)

