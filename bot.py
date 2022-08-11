import hikari, lightbulb
import miru
import os
from dotenv import load_dotenv

load_dotenv()

bot = lightbulb.BotApp(os.getenv("TOKEN"), 
    default_enabled_guilds=int(os.getenv("DEFAULT_GUILD_ID"))
)

miru.load(bot)

@bot.listen(hikari.StartedEvent)
async def bot_started(event):
    print("BOT IS SERVING THE PEOPLE")

bot.load_extensions_from("./extensions")
bot.run()