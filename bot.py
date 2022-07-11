import hikari, lightbulb
from lightbulb.utils import pag, nav
import json, os
from dotenv import load_dotenv

load_dotenv()

bot = lightbulb.BotApp(os.getenv("TOKEN"), 
    default_enabled_guilds=int(os.getenv("DEFAULT_GUILD_ID"))
)

#FUNCTIONS from lightbulb.utils.pag import EmbedPaginator

def build_embed(page_index, page_content):
    return hikari.Embed(title=f"Your inbox:", description=page_content)

async def get_users_data():
    with open("users.json", "r") as f:
        users = json.load(f)
    
async def set_profile(userID):
    #make em a profile in the JSON if they don't got one already
    with open("users.json", "r") as f:
        users = json.load(f)
    if str(userID) in users:
        return False
    else:
        users[str(userID)] = {}
        users[str(userID)]["description"] = "This profile has not been edited yet. This can be changed using `/settings profile_description`"
        users[str(userID)]["messages"] = {}
        users[str(userID)]["daily_updates"] = False

    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    f.close()
    return True

#EVENTS
@bot.listen(hikari.StartedEvent)
async def bot_started(event):
    print("BOT IS SERVING THE PEOPLE")

#GENERAL COMMANDS
@bot.command
@lightbulb.command("ping", "Says pong!")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx):
    await ctx.respond("Pong")

@bot.command
@lightbulb.option("username", "The end user's name", type=hikari.User)
@lightbulb.option("message", "What you want to tell them")
@lightbulb.command("mail", "Send a message to a user")
@lightbulb.implements(lightbulb.SlashCommand)
async def mail(ctx):
    await set_profile(ctx.author.id)
    with open("users.json", "r") as f:
        users = json.load(f)
    #Check if the username id exists in the users JSON
    if str(ctx.options.username.id) in users:
        #Check if the user has already been messaged by them
        if str(ctx.author.id) in users[str(ctx.options.username.id)]["messages"]: 
            users[str(ctx.options.username.id)]["messages"][str(ctx.author.id)].append(ctx.options.message)
            with open("users.json", "w") as f:
                json.dump(users, f, indent=2)
        else:
            users[str(ctx.options.username.id)]["messages"].update({ctx.author.id:[ctx.options.message]})
            with open("users.json", "w") as f:
                json.dump(users, f, indent=2)
        embed = hikari.Embed(title=f"Message successfuly sent to {ctx.options.username.mention} \✔️",description="To edit or delete this message,\n Use `/message [code] [Action]`") 
        await ctx.respond(embed)
    else:
        await ctx.respond("**It appears the user you want to message doesn't have a profile setup. A profile can be setup by using bot commands.**")

@bot.command
@lightbulb.option("username", "The user's profile you want to view", type=hikari.User)
@lightbulb.command("profile", "View profile information of a user")
@lightbulb.implements(lightbulb.SlashCommand)
async def profile(ctx):
    await set_profile(ctx.author.id)
    with open("users.json", "r") as f:
        users = json.load(f)
    if str(ctx.options.username.id) in users:
        embed = hikari.Embed(title=f"**{ctx.options.username}**", description=users[str(ctx.options.username.id)]["description"])
        embed.set_thumbnail(ctx.options.username.display_avatar_url)
        await ctx.respond(embed)
    else:
        ctx.respond("**The profile does not seem to exist in our database**")

#INBOX COMMANDS
@bot.command
@lightbulb.command("inbox", "Commands specific to the inbox")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def inbox(ctx):
    pass
@inbox.child
@lightbulb.command("overview", "General view of messages and appointment requests you've received")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def overview(ctx):
    #add 2 buttons to view pages of messages and have another to view appointments
    await set_profile(ctx.author.id)
    with open("users.json", "r") as f:
        users = json.load(f)
    inbox = pag.EmbedPaginator()
    inbox.set_embed_factory(build_embed)
    #PLEASE ADD A EMBED TITLE LATER
    if len(users[str(ctx.author.id)]["messages"].keys()):
        for keys, values in users[str(ctx.author.id)]["messages"].items():
            inbox.add_line(f"<@{keys}> : {values}")
        navigator = nav.ButtonNavigator(inbox.build_pages())
        await navigator.run(ctx)
    else: await ctx.respond("**Your inbox is currently empty**")

@inbox.child
@lightbulb.command("clear", "Clears all messages in your inbox")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def clear(ctx):
    with open("users.json", "r") as f:
        users = json.load(f)
    count = len(users[str(ctx.author.id)]["messages"].values())
    users[str(ctx.author.id)]["messages"].clear()
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    embed = hikari.Embed(title="Inbox has been successfully cleared \✔️", description=f"Cleared {count} messages successfully.")
    await ctx.respond(embed)
    
#SETTING COMMANDS
@bot.command
@lightbulb.command("settings", "Commands to personalize this bot to your fitting")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def settings(ctx):
    pass

@settings.child
@lightbulb.option("description", "Your new profile description")
@lightbulb.command("profile_description", "Change your profile description to your liking")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def profile_description(ctx):
    with open("users.json", "r") as f:
        users = json.load(f)
    old_desc = users[str(ctx.author.id)]["description"]
    users[str(ctx.author.id)]["description"] = ctx.options.description
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    #MAKE A EMBED HERE WITH A BEFORE AND AFTER
    await ctx.respond("**Your description has been changed**")
    
    

@settings.child
@lightbulb.command("daily_updates", "Toggle to receive a update on your inbox daily by dms")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def daily_updates(ctx):
    await set_profile(ctx.author.id)
    with open("users.json", "r") as f:
        users = json.load(f)
    #This code is unnecessarily long plz find a better way to write this
    users[str(ctx.author.id)]["daily_updates"] = not users[str(ctx.author.id)]["daily_updates"] #there is probably a much shorter way to write this
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    
    embed = hikari.Embed(title="Daily updates has been toggled \✔️", description=f"`Daily_updates : {users[str(ctx.author.id)]['daily_updates']}`")
    await ctx.respond(embed)


bot.run()