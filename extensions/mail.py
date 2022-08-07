import hikari, lightbulb
from lightbulb.utils import pag, nav
import json
from difflib import get_close_matches
from datetime import date, datetime
from dateutil import parser #To parse
import pytz #get the list of timezones
from utils import get_users_data, set_profile
import uuid

plugin = lightbulb.Plugin("mail")

def build_embed(page_index, page_content):
    return hikari.Embed(title=f"Your inbox:", description=page_content)

@plugin.command
@lightbulb.option("username", "The end user's name", type=hikari.User)
@lightbulb.option("message", "What you want to tell them")
@lightbulb.command("mail", "Send a message to a user")
@lightbulb.implements(lightbulb.SlashCommand)
async def mail(ctx):
    await set_profile(ctx.author.id)
    users = await get_users_data()
    #Check if the username id they mentioned exists in the users JSON
    if str(ctx.options.username.id) in users:
        ID = str(uuid.uuid4())[:8]
        #Check if the user has already been messaged by them
        users[str(ctx.options.username.id)]["messages"].update({ID:[str(ctx.author.id), ctx.options.message]})
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
        embed = hikari.Embed(title=f"Message Successfuly Sent ✔️",description=f"Code: {ID}\n To edit or delete this message,\n Use `/message [code] [Action]`") 
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
    await set_profile(ctx.author.id)
    users = await get_users_data()

    inbox = pag.EmbedPaginator()
    inbox.set_embed_factory(build_embed)
    if len(users[str(ctx.author.id)]["messages"].keys()): #if they have messages
        for keys, values in reversed(users[str(ctx.author.id)]["messages"].items()):   
            inbox.add_line(f"<@{values[0]}> : {values[1]}")
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
    users = await get_users_data()
    count = len(users[str(ctx.author.id)]["messages"].values())
    users[str(ctx.author.id)]["messages"].clear()
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    embed = hikari.Embed(title="Inbox has been successfully cleared \✔️", description=f"Cleared {count} messages successfully.")
    await ctx.respond(embed)

def load(bot):
    bot.add_plugin(plugin)