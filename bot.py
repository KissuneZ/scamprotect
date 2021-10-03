import discord
from discord.ext import commands
from wolverine import *

bot = commands.Bot(command_prefix=determine_prefix,
		   intents=discord.Intents().all(),
		   case_insensitive=True,
		   help_command=None)

Token = "ODY3MDMwOTQ1MTIyNjE1Mjk3.YPbLfQ.Yvo95f-qmLF3wmHBXDkcnpXGv_M"

archive_logs()
logging.basicConfig(filename="./logs/latest.log", filemode="w+",
				    format='[%(asctime)s | %(name)s / %(levelname)s]: %(message)s', level=logging.INFO)


logger = logging.getLogger("Main")
logger.info(f"Running...")

init()

logger.info("Loading CommandListener...")
bot.load_extension("main")


@bot.event
async def on_ready():
	logger.info("Logged in.")
	await is_restarted(bot)
	asyncio.create_task(presence_loop(bot))
	asyncio.create_task(auto_restart(bot))


@bot.event
async def on_command_error(ctx, error):
	msg = error

	if isinstance(error, commands.errors.CommandInvokeError):
		_error = str(error).replace("Command raised an exception: ", "")
		logger.error(f"`{_error}` was raised while executing `{ctx.message.content}`.")
		msg = f"Произошла ошибка.\n```py\n{_error}```"

	if isinstance(error, commands.errors.CommandNotFound):
		return

	if isinstance(error, commands.CommandOnCooldown):
		msg = f"Команда будет доступна через {int(error.retry_after)} секунд."

	if isinstance(error, commands.errors.BotMissingPermissions):
		msg = "У меня нет прав для выполнения данной команды."

	if isinstance(error, commands.errors.MissingRequiredArgument):
		msg = "Вы не указали обязательный аргумент."

	if isinstance(error, commands.MissingPermissions):
		msg = f'У вас нет прав для вызова этой команды.'

	if isinstance(error, commands.errors.ChannelNotFound):
		msg = 'Канал не найден.'

	if isinstance(error, commands.BadArgument):
		msg = 'Несовместимый тип аргумента.'

	if isinstance(error, commands.errors.NotOwner):
		msg = 'Вы не владелец бота.'

	await fail(ctx, msg)


@bot.event
async def on_message(message):
	if message.author.bot:
		return

	mentions = [f"<@!{bot.user.id}>", f"<@{bot.user.id}>"]
	if message.content in mentions:
		p = get_prefix(message.guild.id)
		return await message.reply(f"{vmark} Мой префикс: [`{p}`].")

	await bot.process_commands(message)
	if not "http" in message.content:
		return

	key = message.guild.id
	args = fetch_scanner_arguments(key)

	if args["disabled"]:
		await scan_message(message, **args)




logger.info("Logging in...")
bot.run(Token)
