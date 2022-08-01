import lightbulb, hikari
import json
from utils import get_users_data, set_profile

plugin = lightbulb.Plugin("other")

@plugin.command
@lightbulb.command("ping", "Says pong!")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx):
    await ctx.respond("Pong")

@plugin.command
@lightbulb.option("username", "The user's profile you want to view", type=hikari.User)
@lightbulb.command("profile", "View profile information of a user")
@lightbulb.implements(lightbulb.SlashCommand)
async def profile(ctx):
    await set_profile(ctx.author.id)
    users = await get_users_data()
    
    if str(ctx.options.username.id) in users:
        embed = hikari.Embed(title=f"**{ctx.options.username}**", description=users[str(ctx.options.username.id)]["description"])
        embed.set_thumbnail(ctx.options.username.display_avatar_url)
        await ctx.respond(embed)
    else:
        ctx.respond("**The profile does not seem to exist in our database**")


def load(bot):
    bot.add_plugin(plugin)