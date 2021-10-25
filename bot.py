import discord
from discord.ext import commands
from wolverine import *

bot = commands.Bot(command_prefix=determine_prefix,
		   intents=discord.Intents().all(),
		   case_insensitive=True,
		   help_command=None)

TOKEN = read_config()["token"]

archive_logs()
logging.basicConfig(filename="./logs/latest.log", filemode="w+",
				    format=log_pattern, level=logging.INFO)


logger = logging.getLogger("Main")
logger.info(f"Starting up...")

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
		msg = lang(ctx)["exception"] + f"\n```py\n{_error}```"

	if isinstance(error, commands.errors.CommandNotFound):
		return

	if isinstance(error, commands.CommandOnCooldown):
		msg = lang(ctx)["retry_after"].format(int(error.retry_after))

	ctx.command.reset_cooldown(ctx)

	if isinstance(error, commands.errors.BotMissingPermissions):
		msg = lang(ctx)["missing_access"]
		for perm in error.missing_perms:
			msg += f"\n> {lang(ctx)['perms'][perm]}"

	if isinstance(error, commands.MissingPermissions):
		msg = lang(ctx)["no_perms"]
		for perm in error.missing_perms:
			msg += f"\n> {lang(ctx)['perms'][perm]}"

	if isinstance(error, commands.errors.MissingRequiredArgument):
		lang(ctx)["missing_reqarg"]

	if isinstance(error, commands.errors.ChannelNotFound):
		lang(ctx)["channel_nf"]

	if isinstance(error, commands.BadArgument):
		lang(ctx)["bad_arg"]

	if isinstance(error, commands.errors.NotOwner):
		lang(ctx)["not_owner"]

	await fail(ctx, msg)




@bot.event
async def on_message(message):
	if message.author.bot:
		return

	mentions = [f"<@!{bot.user.id}>", f"<@{bot.user.id}>"]
	if message.content in mentions:
		p = get_prefix(message.guild.id)
		return await message.reply(lang(message)["my_prefix"].format(vmark, p))

	await bot.process_commands(message)
	if not "http" in message.content:
		return

	key = message.guild.id
	kwargs = fetch_scanner_arguments(key)

	if kwargs["disabled"]:
		await scan_message(message, **kwargs)




logger.info("Logging in...")
bot.run(TOKEN)
