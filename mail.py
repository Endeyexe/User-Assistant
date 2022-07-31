import hikari, lightbulb
from lightbulb.utils import pag, nav
import json
from difflib import get_close_matches
from datetime import date, datetime
from dateutil import parser #To parse
import pytz #get the list of timezones

plugin = lightbulb.Plugin("mail")

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
        users[str(userID)]["bookings"] = {}
        users[str(userID)]["booking_requests"] = {}
        users[str(userID)]["daily_updates"] = False

    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    f.close()
    return True

@plugin.command
@lightbulb.option("username", "The end user's name", type=hikari.User)
@lightbulb.option("message", "What you want to tell them")
@lightbulb.command("mail", "Send a message to a user")
@lightbulb.implements(lightbulb.SlashCommand)
async def mail(ctx):
    await set_profile(ctx.author.id)
    get_users_data()
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

@plugin.command
@lightbulb.command("inbox", "Commands specific to the inbox")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def inbox(ctx):
    pass

@inbox.child
@lightbulb.command("overview", "overview of your inbox")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def overview(ctx):
    pass
    #add some general info here about their inbox

@inbox.child
@lightbulb.command("messages", "View of all messages you've received")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def messages(ctx):
    #add 2 buttons to view pages of messages and have another to view appointments
    await set_profile(ctx.author.id)
    with open("users.json", "r") as f:
        users = json.load(f)
    inbox = pag.EmbedPaginator()
    inbox.set_embed_factory(build_embed)
    if len(users[str(ctx.author.id)]["messages"].keys()): #if they have messages
        for keys, values in users[str(ctx.author.id)]["messages"].items():
            for message in values: #loop in place just in case they have multiple messages from same user
                inbox.add_line(f"<@{keys}> : {message}")
                inbox.add_line("")
        navigator = nav.ButtonNavigator(inbox.build_pages())
        await navigator.run(ctx)
    else: await ctx.respond("**Your inbox is currently empty**")

@inbox.child
@lightbulb.command("booking_requests", "View booking requests")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def booking_requests(ctx):
    pass

#make a sub sub command group for clear all, clear messages, clear appointments later
@inbox.child
@lightbulb.command("clear_messages", "Clears all messages in your inbox")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def clear_messages(ctx):
    with open("users.json", "r") as f:
        users = json.load(f)
    count = len(users[str(ctx.author.id)]["messages"].values())
    users[str(ctx.author.id)]["messages"].clear()
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    embed = hikari.Embed(title="Inbox has been successfully cleared \✔️", description=f"Cleared {count} messages successfully.")
    await ctx.respond(embed)

def load(bot):
    bot.add_plugin(plugin)