import hikari, lightbulb
import os
from dotenv import load_dotenv
from datetime import datetime

datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
load_dotenv()

bot = lightbulb.BotApp(os.getenv("TOKEN"), 
    default_enabled_guilds=int(os.getenv("DEFAULT_GUILD_ID"))
)

@bot.listen(hikari.StartedEvent)
async def bot_started(event):
    print("BOT IS SERVING THE PEOPLE")

bot.load_extensions_from("./extensions")
bot.run()