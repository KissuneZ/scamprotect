from threading import Thread
from discord.ext import commands
from wolverine import *
import asyncio
import nest_asyncio
import discord
import sys
import os
import json

nest_asyncio.apply()


bot = commands.Bot("/", help_command=None)
TOKEN = read_config()["token"]


@bot.event
async def on_ready():
	connection_check()
	init_scanner()
	await AsyncScannerThread(data, channels).run()


class Cancelled(Exception):
	pass


class AsyncScannerThread(Thread):
	def __init__(self, data, channels):
		Thread.__init__(self)
		self.channels = channels
		self.index    = data[0]
		self.limit    = data[1]
		self.message  = data[2]
		self.channel  = data[4]
		self.deleted  = 0
		self.bot      = bot
		self.glimit   = self.limit
		if len(data) == 6:
			self.glimit = data[5]


	def get_channels(self, cids):
		channels = []
		self.channel = self.bot.get_channel(self.channel)
		for cid in cids:
			channels.append(self.bot.get_channel(cid))
		print(channels)
		return channels

	async def run(self):
		d = []
		self.channels = self.get_channels(self.channels)
		self.message  = await self.channel.fetch_message(self.message)
		for channel in self.channels:
			try:
				d = await channel.purge(limit=self.limit, check=self.check)
			except Cancelled:
				break
			except:
				self.index += self.limit
			self.deleted += len(d)
		await done(self.channel, lang(self.message)["msgs_deleted"].format(self.deleted))
		try:
			os.remove(fname)
		except:
			pass
		exit(0)

	def check(self, message):
		return asyncio.run(self.check_(message))

	async def check_(self, message):
		self.index += 1
		i = self.index
		l = self.glimit
		m = self.message

		text = pattern.format(waiting, i, l)
		if i < l:
			try:
				text = lang(self.message)["scan_pattern"].format(vmark, i, l)
				await m.edit(content=text)
			except Exception as e:
				print(e)
				text  = lang(self.message)["s_cancelled"].format(vmark, i, l)
				await m.channel.send(content=text)
				os.remove(fname)
				raise Cancelled()
		else:
			text = lang(self.message)["s_done"].format(vmark, i, l)
			await m.edit(content=text)

		if "http" in message.content:
			result = await scan_message(message, **manual_scanner_args)
			return result

		return False


sid = sys.argv[1]
fname = f"./scanners/{sid}.json"
with open(fname, "r") as f:
	data = json.loads(f.read())
channels = data[3]

bot.run(TOKEN)
