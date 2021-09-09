import discord, asyncio, re
from discord.ext import commands

bot = commands.Bot(command_prefix='sp!',
				   intents=discord.Intents().all(),
				   case_insensitive=True,
				   help_command=None)
Token = "ODY3MDMwOTQ1MTIyNjE1Mjk3.YPbLfQ.Yvo95f-qmLF3wmHBXDkcnpXGv_M"
embed_blacklist = ["discord nitro бесплатно на 3 месяца от steam", "сделайте discord ещё круче с nitro", "3 months of discord nitro free from steam", "get 3 months of discord nitro free from steam. upgrade your emoji, enjoy bigger file uploads, stand out in your favorite discords, and more."]
patterns_blacklist = [r"i'm leaving.*skin.*https:\/\/", r"i'm leaving.*skin.*http:\/\/"]
reasons = ["blacklist.link:{}", "blacklist.embed:{}", "blacklist.pattern:{}"]

with open("blacklist.txt") as file:
	_text_ = file.read()
	blacklist = _text_.split("\n")


@bot.command()
@commands.is_owner()
async def exc(ctx, *, command):
	eval(command, locals(), globals())


@bot.command()
async def invite(ctx):
	embed = discord.Embed(description=f"<:info:863711569975967745> Добавить бота на свой сервер: [[Нажми]](https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot)",
						  color=0x8080ff)
	await ctx.send(embed=embed)

@bot.event
async def on_message(message):
	if message.author.bot:
		return
	await bot.process_commands(message)
	index = 0
	for elem in blacklist:
		if elem in message.content and elem != "":
			return await delete(message, index, 0, 0, "message.content")
		index += 1
	index = 0
	if not message.embeds and "http" in message.content:
		await asyncio.sleep(1)
		message = await message.channel.fetch_message(message.id)
	for elem in embed_blacklist:
		indexx = 0
		for embed in message.embeds:
			if elem in embed.title.lower() and elem != "":
				return await delete(message, index, indexx, 1, "title")
			indexx += 1
		index += 1
	index = 0
	for elem in embed_blacklist:
		indexx = 0
		for embed in message.embeds:
			if elem in embed.description.lower() and elem != "":
				return await delete(message, index, indexx, 1, "description")
			indexx += 1
		index += 1
	index = 0
	for elem in patterns_blacklist:
		if re.findall(elem, message.content.lower()):
			return await delete(message, index, 0, 2, "message.content")
		index += 1


async def delete(message, index, indexx, rindex, blkey):
	await message.delete()
	reason = reasons[rindex].format(f"{blkey}: {[indexx]}: {index}")
	embed = discord.Embed(description=f"<:danger:862303667465093140> Удалено сообщение от пользователя {message.author.mention}.\n \➡ **Причина**: **`{reason}`**.",
						  color=0xff6060)
	await message.channel.send(embed=embed)
	embed = discord.Embed(description=f"<:danger:862303667465093140> **Ваше сообщение было удалено**.\n```{message.content}```",
				          color=0xff6060)
	embed.set_footer(text="Вероятнее всего, вы стали жертвой взлома и ваш аккаунт был использован для рассылки скама. Что-бы такое не повторилось, удалите BtterDiscrd с вашего ПК и используйте надежный антивирус.")
	await message.author.send(embed=embed)


@bot.event
async def on_ready():
	print("Logged in.")
	presence = f'sp!invite | [{len(bot.guilds)}]'
	await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(presence))


@bot.event
async def on_command_error(ctx, error):
	await ctx.send(f'```{error}```')


bot.run(Token)
