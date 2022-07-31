import lightbulb, hikari
import json

plugin = lightbulb.Plugin("other")

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
        users[str(userID)]["appointments"] = {}
        users[str(userID)]["daily_updates"] = False

    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    f.close()
    return True

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
        users[str(userID)]["appointments"] = {}
        users[str(userID)]["daily_updates"] = False

    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)
    f.close()
    return True

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
    with open("users.json", "r") as f:
        users = json.load(f)
    if str(ctx.options.username.id) in users:
        embed = hikari.Embed(title=f"**{ctx.options.username}**", description=users[str(ctx.options.username.id)]["description"])
        embed.set_thumbnail(ctx.options.username.display_avatar_url)
        await ctx.respond(embed)
    else:
        ctx.respond("**The profile does not seem to exist in our database**")


def load(bot):
    bot.add_plugin(plugin)