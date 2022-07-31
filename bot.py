import hikari, lightbulb
import os
from dotenv import load_dotenv

load_dotenv()

bot = lightbulb.BotApp(os.getenv("TOKEN"), 
    default_enabled_guilds=int(os.getenv("DEFAULT_GUILD_ID"))
)

@bot.listen(hikari.StartedEvent)
async def bot_started(event):
    print("BOT IS SERVING THE PEOPLE")

bot.load_extensions_from("./extensions")
bot.run()